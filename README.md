# Cyfer: Your Everyday AI Assistant

Cyfer is a sophisticated Flask-based web application designed to be your intelligent, conversational AI assistant for a wide range of day-to-day tasks. It provides real-time information, answers questions, and engages in general conversation. With a focus on persistent chat history and an intuitive user interface, Cyfer streamlines your daily interactions and enhances productivity.

The application leverages a robust backend, supporting both Neon-hosted PostgreSQL for scalable, durable storage and local SQLite for development flexibility. Its multi-session memory ensures that every review session maintains full context, allowing for a seamless and continuous dialogue about your codebase. The polished UI, adaptable to both dark and light themes, provides a modern and responsive experience across various devices.

## Key Features

- **Conversational AI Assistant:** Engage in natural language conversations with an AI assistant to get instant answers, information, and assistance with various tasks.
- **Persistent Chat History:** All review sessions and messages are securely stored, allowing you to revisit past discussions and track the evolution of your code over time.
- **Multi-Session Memory:** Each chat session maintains its own independent history, ensuring that the AI's responses are always relevant to the specific code review context.
- **Contextual Code Analysis with Diffs:** The AI intelligently replays earlier prompts and highlights key code changes through integrated diffs, providing precise and actionable insights.
- **Flexible Database Integration:**
    - **Neon PostgreSQL Backend:** Seamlessly integrates with Neon for a powerful, scalable, and cloud-hosted PostgreSQL database, ensuring high availability and data durability.
- **Local SQLite Fallback:** Automatically switches to a local SQLite database (`instance/cyfer.db`) if a `DATABASE_URL` is not configured, perfect for local development and testing.
- **Modern and Responsive User Interface:**
    - **Enhanced Composer UI:** A clean and intuitive interface with aligned controls for an optimal user experience.
    - **Dynamic Theme Toggle:** Effortlessly switch between dark and light themes to suit your preference and working environment.
    - **Responsive Layout:** Designed to provide a consistent and enjoyable experience on both desktop and tablet devices.
- **Easy Setup and Deployment:** Simple environment variable configuration and clear setup instructions make it easy to get Cyfer up and running locally or deployed to production.
- **Extensible LLM Support:** Configurable to work with various Large Language Model providers (Gemini, OpenAI, Anthropic) via API keys, offering flexibility in AI capabilities.

## Prerequisites

## Prerequisites

- Python 3.10+
- Node is optional (only static assets, no build step required)
- A Neon PostgreSQL database URL (or use SQLite locally)
- API key for at least one LLM provider (Gemini by default)

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `GEMINI_API_KEY` | Required unless you pass a key per request. |
| `OPENAI_API_KEY` | Optional, used when the request key starts with `sk-`. |
| `ANTHROPIC_API_KEY` | Optional, used for Claude. |
| `DEFAULT_PROVIDER` | Optional, defaults to `gemini`. |
| `DATABASE_URL` | Neon/Postgres connection string (example below). |

### Neon connection string

In Neon, create a database and copy the connection string. Convert it to the SQLAlchemy + psycopg format:

```
postgresql+psycopg://<user>:<password>@<host>/<database>?sslmode=require
```

The app automatically rewrites `postgres://` or `postgresql://` URLs to append `+psycopg`, so you can paste the standard Neon connection string as-is.

If `DATABASE_URL` is omitted, the app stores data in `instance/cyfer.db` (SQLite).

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_key
# Optional fallbacks
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DATABASE_URL=postgresql+psycopg://...
```

## Running locally

```bash
python app.py
```

The app runs at http://127.0.0.1:5000. The first visit creates a chat automatically; new chats live in the sidebar.

## How it works

1. The frontend calls `/api/chats` to create or list sessions stored in Neon.
2. Each message is persisted along with the raw code snippet and a generated diff.
3. The backend assembles a memory window (system prompt + recent messages) and streams the LLM reply.
4. The UI displays diffs inside expandable blocks, ensuring the assistant always receives key context from earlier turns.

## Testing the database link

- Confirm `DATABASE_URL` is reachable by running `python -c "import database; database.init_db(); print('ok')"`.
- Check the `chats` and `messages` tables using any Postgres client.

## Deployment notes

- Ensure the `DATABASE_URL` uses `sslmode=require` on Neon.
- Set `FLASK_ENV=production` (or run through a WSGI server such as Gunicorn) for production deployments.
- Static assets are served by Flask; configure caching or a CDN if needed.

## Roadmap ideas

- Add chat renaming and deletion.
- Surface diff summaries in the sidebar preview.
- Expose a REST endpoint for exporting review transcripts.
