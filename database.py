import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    create_engine,
    desc,
    insert,
    select,
    update,
)
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import make_url

DEFAULT_SQLITE_URL = "sqlite:///instance/cyfer.db"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://") and "+psycopg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

def _ensure_sqlite_path(url: str) -> None:
    parsed = make_url(url)
    if parsed.get_backend_name() != "sqlite":
        return
    database_path = parsed.database
    if not database_path:
        return
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

_ensure_sqlite_path(DATABASE_URL)

engine: Engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
)

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("email", String(320), nullable=False),
    Column("password_hash", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    UniqueConstraint("email", name="uq_users_email"),
)

chats = Table(
    "chats",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("title", Text, nullable=False),
    Column("language", String(50)),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

messages = Table(
    "messages",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("chat_id", String(36), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False),
    Column("role", String(16), nullable=False),
    Column("language", String(50)),
    Column("content", Text, nullable=False),
    Column("display_content", Text),
    Column("code_snapshot", Text),
    Column("code_diff", Text),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

user_chats = Table(
    "user_chats",
    metadata,
    Column("user_id", String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("chat_id", String(36), ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

def init_db() -> None:
    metadata.create_all(engine)

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

def create_user(email: str, password_hash: str) -> dict:
    user_id = str(uuid4())
    now = _utcnow()
    payload = {
        "id": user_id,
        "email": email,
        "password_hash": password_hash,
        "created_at": now,
    }
    with engine.begin() as connection:
        connection.execute(insert(users).values(payload))
    return payload

def get_user_by_email(email: str) -> Optional[dict]:
    with engine.connect() as connection:
        stmt = select(users).where(users.c.email == email)
        row = connection.execute(stmt).mappings().first()
        return dict(row) if row else None

def create_chat(title: str, language: Optional[str] = None, *, user_id: Optional[str] = None) -> dict:
    chat_id = str(uuid4())
    now = _utcnow()
    payload = {
        "id": chat_id,
        "title": title,
        "language": language,
        "created_at": now,
        "updated_at": now,
    }
    with engine.begin() as connection:
        connection.execute(insert(chats).values(payload))
        if user_id:
            connection.execute(
                insert(user_chats).values(
                    {
                        "user_id": user_id,
                        "chat_id": chat_id,
                        "created_at": now,
                    }
                )
            )
    return payload

def list_chats(user_id: Optional[str], limit: int = 100) -> List[dict]:
    with engine.connect() as connection:
        if user_id:
            stmt = (
                select(chats)
                .join(user_chats, chats.c.id == user_chats.c.chat_id)
                .where(user_chats.c.user_id == user_id)
                .order_by(desc(chats.c.updated_at))
                .limit(limit)
            )
        else:
            stmt = (
                select(chats)
                .order_by(desc(chats.c.updated_at))
                .limit(limit)
            )
        chat_rows = connection.execute(stmt).mappings().all()
        chat_ids = [row["id"] for row in chat_rows]
        last_messages: dict = {}
        if chat_ids:
            message_stmt = (
                select(
                    messages.c.chat_id,
                    messages.c.display_content,
                    messages.c.content,
                )
                .where(messages.c.chat_id.in_(chat_ids))
                .order_by(messages.c.chat_id, desc(messages.c.created_at))
            )
            for row in connection.execute(message_stmt).mappings():
                chat_id = row["chat_id"]
                if chat_id in last_messages:
                    continue
                preview_source = row["display_content"] or row["content"]
                last_messages[chat_id] = preview_source or ""
        result: List[dict] = []
        for row in chat_rows:
            data = dict(row)
            data["last_message_preview"] = last_messages.get(row["id"], "")
            result.append(data)
        return result

def get_chat(chat_id: str, *, user_id: Optional[str] = None) -> Optional[dict]:
    with engine.connect() as connection:
        stmt = select(chats)
        if user_id:
            stmt = (
                stmt.join(user_chats, chats.c.id == user_chats.c.chat_id)
                .where(user_chats.c.user_id == user_id, user_chats.c.chat_id == chat_id)
            )
        else:
            stmt = stmt.where(chats.c.id == chat_id)
        row = connection.execute(stmt).mappings().first()
        return dict(row) if row else None

def get_chat_messages(chat_id: str, limit: Optional[int] = None) -> List[dict]:
    with engine.connect() as connection:
        stmt = (
            select(messages)
            .where(messages.c.chat_id == chat_id)
            .order_by(messages.c.created_at.asc())
        )
        if limit:
            stmt = stmt.limit(limit)
        rows = connection.execute(stmt).mappings().all()
        return [dict(row) for row in rows]

def add_message(
    chat_id: str,
    role: str,
    content: str,
    *,
    language: Optional[str] = None,
    display_content: Optional[str] = None,
    code_snapshot: Optional[str] = None,
    code_diff: Optional[str] = None,
) -> dict:
    message_id = str(uuid4())
    now = _utcnow()
    payload = {
        "id": message_id,
        "chat_id": chat_id,
        "role": role,
        "language": language,
        "content": content,
        "display_content": display_content,
        "code_snapshot": code_snapshot,
        "code_diff": code_diff,
        "created_at": now,
    }
    with engine.begin() as connection:
        connection.execute(insert(messages).values(payload))
        connection.execute(
            update(chats)
            .where(chats.c.id == chat_id)
            .values(updated_at=now)
        )
    return payload

def update_chat(chat_id: str, *, title: Optional[str] = None, language: Optional[str] = None) -> None:
    values = {}
    if title is not None:
        values["title"] = title
    if language is not None:
        values["language"] = language
    if not values:
        return
    with engine.begin() as connection:
        connection.execute(
            update(chats)
            .where(chats.c.id == chat_id)
            .values(**values)
        )
