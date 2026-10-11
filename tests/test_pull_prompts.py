"""
Tests for pulling the seed prompt from the LangSmith Hub.
"""
from unittest.mock import MagicMock

import pytest
import yaml
from langchain_core.prompts import ChatPromptTemplate

import pull_prompts

FAKE_KEY = "lsv2_pt_fake_key_for_tests"
SYSTEM_TEXT = "Você é um assistente.\n\nRelato de Bug:\n{bug_report}\n"
USER_TEXT = "{bug_report}"


@pytest.fixture
def seed_prompt():
    return ChatPromptTemplate.from_messages([("system", SYSTEM_TEXT), ("human", USER_TEXT)])


@pytest.fixture
def mock_client(monkeypatch, seed_prompt):
    client = MagicMock()
    client.pull_prompt.return_value = seed_prompt
    client_class = MagicMock(return_value=client)
    monkeypatch.setattr(pull_prompts, "Client", client_class)
    monkeypatch.setenv("LANGSMITH_API_KEY", FAKE_KEY)
    return client_class, client


@pytest.fixture
def output_path(monkeypatch, tmp_path):
    path = tmp_path / "prompts" / "bug_to_user_story_v1.yml"
    monkeypatch.setattr(pull_prompts, "OUTPUT_PATH", path)
    return path


def test_missing_api_key_returns_error_without_client(monkeypatch, capsys):
    client_class = MagicMock()
    monkeypatch.setattr(pull_prompts, "Client", client_class)
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)

    assert pull_prompts.main() == 1
    client_class.assert_not_called()
    assert "LANGSMITH_API_KEY" in capsys.readouterr().out


def test_pulls_seed_prompt_with_dangerous_flag(mock_client, output_path):
    _, client = mock_client

    assert pull_prompts.main() == 0
    client.pull_prompt.assert_called_once_with(
        "leonanluppi/bug_to_user_story_v1", dangerously_pull_public_prompt=True
    )


def test_saved_yaml_has_expected_fields(mock_client, output_path):
    assert pull_prompts.main() == 0

    data = yaml.safe_load(output_path.read_text(encoding="utf-8"))
    prompt = data["bug_to_user_story_v1"]
    assert prompt["system_prompt"] == SYSTEM_TEXT
    assert prompt["user_prompt"] == USER_TEXT
    assert prompt["version"] == "v1"
    assert prompt["source"] == "leonanluppi/bug_to_user_story_v1"
    assert prompt["description"]
    assert prompt["tags"]
    assert len(prompt["created_at"]) == 10
    assert "Você" in output_path.read_text(encoding="utf-8")


def test_pull_failure_returns_error(mock_client, output_path, capsys):
    _, client = mock_client
    client.pull_prompt.side_effect = RuntimeError("boom")

    assert pull_prompts.main() == 1
    assert "Erro ao fazer pull" in capsys.readouterr().out
    assert not output_path.exists()


def test_output_never_contains_api_key(mock_client, output_path, capsys):
    _, client = mock_client
    pull_prompts.main()
    client.pull_prompt.side_effect = RuntimeError(f"auth failed for {FAKE_KEY}")
    pull_prompts.main()

    captured = capsys.readouterr()
    assert FAKE_KEY not in captured.out
    assert FAKE_KEY not in captured.err
