import os
import requests
import json
from typing import Iterable, List, Dict
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

load_dotenv() # Load environment variables from .env file


# API keys should be set in a .env file in the Cyfer directory, e.g.:
# GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
# OPENAI_API_KEY="YOUR_OPENAI_API_KEY" (optional)
# ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY" (optional)
# Alternatively, you can pass them directly in the 'api_key' parameter to analyze_code,
# but using a .env file is recommended for security and consistency.

def _call_gemini(prompt, api_key=None):
    gemini_api_key = api_key if api_key else os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY environment variable or provide it.")

    genai.configure(api_key=gemini_api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    model = genai.GenerativeModel(model_name)
    try:
        response = model.generate_content(prompt, stream=True)
    except google_exceptions.NotFound as exc:
        raise ValueError(
            "Gemini model '{model_name}' not found. Set GEMINI_MODEL to a valid model, e.g. 'gemini-1.5-flash' or 'gemini-1.5-pro'."
            .format(model_name=model_name)
        ) from exc

    for chunk in response:
        text = getattr(chunk, "text", None)
        if text:
            yield text

def _call_openai(prompt, api_key=None):
    openai_api_key = api_key if api_key else os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable or provide it.")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    data = {
        "model": "gpt-3.5-turbo", # Or gpt-4, gpt-4o etc.
        "messages": [{"role": "user", "content": prompt}]
    }
    url = "https://api.openai.com/v1/chat/completions"
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

def _call_claude(prompt, api_key=None):
    anthropic_api_key = api_key if api_key else os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        raise ValueError("Anthropic API key not found. Please set ANTHROPIC_API_KEY environment variable or provide it.")

    headers = {
        "Content-Type": "application/json",
        "x-api-key": anthropic_api_key,
        "anthropic-version": "2023-06-01"
    }
    data = {
        "model": "claude-3-opus-20240229", # Or other Claude models
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }
    url = "https://api.anthropic.com/v1/messages"
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response.json()['content'][0]['text']

def _messages_to_prompt(messages: List[Dict[str, str]]) -> str:
    formatted: List[str] = []
    role_labels = {
        "system": "System",
        "user": "User",
        "assistant": "Assistant",
    }
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        label = role_labels.get(role, role.title())
        formatted.append(f"{label} message:\n{content.strip()}".strip())
    return "\n\n".join(formatted)

def _yield_text(text: str) -> Iterable[str]:
    yield text

def analyze_code(messages: List[Dict[str, str]], provider="gemini", api_key=None) -> Iterable[str]:
    prompt = _messages_to_prompt(messages)
    if provider == "gemini":
        return _call_gemini(prompt, api_key)
    if provider == "openai":
        response_text = _call_openai(prompt, api_key)
        return _yield_text(response_text)
    if provider == "claude":
        response_text = _call_claude(prompt, api_key)
        return _yield_text(response_text)
    raise ValueError(f"Unsupported LLM provider: {provider}")
