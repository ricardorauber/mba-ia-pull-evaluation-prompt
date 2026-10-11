"""
Tests for the environment template and the OpenRouter wiring of the LLM factory.
"""
from pathlib import Path

from langchain_openai import ChatOpenAI

from utils import get_llm

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
ENV_EXAMPLE = Path(__file__).parent.parent / ".env.example"

REQUIRED_VARS = [
    "LANGSMITH_TRACING",
    "LANGSMITH_ENDPOINT",
    "LANGSMITH_API_KEY",
    "LANGSMITH_PROJECT",
    "USERNAME_LANGSMITH_HUB",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "GOOGLE_API_KEY",
    "LLM_PROVIDER",
    "LLM_MODEL",
    "EVAL_MODEL",
]
SECRET_VARS = ["LANGSMITH_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY", "USERNAME_LANGSMITH_HUB"]


def parse_env_file(path: Path) -> dict:
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def test_get_llm_targets_openrouter_when_base_url_is_set(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("OPENAI_BASE_URL", OPENROUTER_BASE_URL)
    monkeypatch.setenv("LLM_MODEL", "google/gemini-3.1-flash-lite")
    monkeypatch.delenv("OPENAI_API_BASE", raising=False)

    llm = get_llm()

    assert isinstance(llm, ChatOpenAI)
    assert llm.model_name == "google/gemini-3.1-flash-lite"
    assert str(llm.root_client.base_url).rstrip("/") == OPENROUTER_BASE_URL


def test_env_example_lists_every_variable_with_empty_secrets():
    values = parse_env_file(ENV_EXAMPLE)

    for var in REQUIRED_VARS:
        assert var in values, f"{var} missing from .env.example"
    for var in SECRET_VARS:
        assert values[var] == "", f"{var} must be empty in .env.example"
    assert values["LLM_PROVIDER"] == "openai"
    assert values["OPENAI_BASE_URL"] == OPENROUTER_BASE_URL
    assert values["LLM_MODEL"] == "google/gemini-3.1-flash-lite"
    assert values["EVAL_MODEL"] == "google/gemini-3.8-flash"
