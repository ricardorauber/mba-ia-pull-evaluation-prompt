"""
Tests for validating and pushing the optimized prompt to the LangSmith Hub.
"""
from unittest.mock import MagicMock

import pytest
import yaml
from langsmith.utils import LangSmithConflictError

import push_prompts

FAKE_KEY = "lsv2_pt_fake_key_for_tests"
HANDLE = "tester"


def valid_prompt() -> dict:
    return {
        "description": "Converte bugs em User Stories",
        "system_prompt": "Você é um Product Manager. Use {{chaves}} literais.",
        "user_prompt": "Relato de bug:\n{bug_report}",
        "version": "v2",
        "tags": ["user-story", "few-shot-learning"],
        "techniques_applied": ["Few-shot Learning", "Role Prompting"],
    }


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("LANGSMITH_API_KEY", FAKE_KEY)
    monkeypatch.setenv("USERNAME_LANGSMITH_HUB", HANDLE)


@pytest.fixture
def prompt_file(monkeypatch, tmp_path):
    path = tmp_path / "bug_to_user_story_v2.yml"
    path.write_text(
        yaml.safe_dump({"bug_to_user_story_v2": valid_prompt()}, allow_unicode=True),
        encoding="utf-8",
    )
    monkeypatch.setattr(push_prompts, "PROMPT_FILE", path)
    return path


@pytest.fixture
def client(monkeypatch):
    client = MagicMock()
    client.push_prompt.return_value = "https://smith.langchain.com/prompts/bug_to_user_story_v2"
    monkeypatch.setattr(push_prompts, "Client", MagicMock(return_value=client))
    return client


@pytest.mark.parametrize("missing", ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"])
def test_missing_env_var_returns_error_without_client(monkeypatch, env, missing, capsys):
    client_class = MagicMock()
    monkeypatch.setattr(push_prompts, "Client", client_class)
    monkeypatch.delenv(missing)

    assert push_prompts.main() == 1
    client_class.assert_not_called()
    assert missing in capsys.readouterr().out


def test_missing_file_returns_error(monkeypatch, env, client, tmp_path):
    monkeypatch.setattr(push_prompts, "PROMPT_FILE", tmp_path / "missing.yml")

    assert push_prompts.main() == 1
    client.push_prompt.assert_not_called()


def test_missing_entry_returns_error(env, client, prompt_file, capsys):
    prompt_file.write_text(yaml.safe_dump({"other_prompt": valid_prompt()}), encoding="utf-8")

    assert push_prompts.main() == 1
    assert "não encontrado" in capsys.readouterr().out
    client.push_prompt.assert_not_called()


def _with(**changes):
    data = valid_prompt()
    for key, value in changes.items():
        if value is None:
            data.pop(key)
        else:
            data[key] = value
    return data


@pytest.mark.parametrize(
    "prompt_data, expected_error",
    [
        (_with(techniques_applied=["Few-shot Learning"]), "Mínimo de 2 técnicas"),
        (_with(system_prompt="   "), "system_prompt está vazio"),
        (_with(user_prompt=None), "user_prompt"),
        (_with(user_prompt="{bug_report} {extra}"), "apenas a variável"),
    ],
)
def test_validate_prompt_rejects_invalid_prompts(prompt_data, expected_error):
    is_valid, errors = push_prompts.validate_prompt(prompt_data)

    assert not is_valid
    assert len(errors) == 1
    assert expected_error in errors[0]


def test_validate_prompt_accepts_the_real_v2_file():
    data = yaml.safe_load(push_prompts.PROMPT_FILE.read_text(encoding="utf-8"))

    assert push_prompts.validate_prompt(data["bug_to_user_story_v2"]) == (True, [])


def test_invalid_prompt_is_not_pushed(env, client, prompt_file):
    prompt_file.write_text(
        yaml.safe_dump({"bug_to_user_story_v2": _with(techniques_applied=[])}), encoding="utf-8"
    )

    assert push_prompts.main() == 1
    client.push_prompt.assert_not_called()


def test_push_sends_public_prompt_with_metadata(env, client, prompt_file):
    assert push_prompts.main() == 0

    client.push_prompt.assert_called_once()
    args, kwargs = client.push_prompt.call_args
    assert args == (f"{HANDLE}/bug_to_user_story_v2",)
    assert kwargs["is_public"] is True
    assert kwargs["object"].input_variables == ["bug_report"]
    assert kwargs["description"] == "Converte bugs em User Stories"
    assert kwargs["tags"] == ["user-story", "few-shot-learning", "role-prompting"]
    assert "Few-shot Learning" in kwargs["readme"]
    assert "Role Prompting" in kwargs["readme"]
    assert "v2" in kwargs["readme"]


def test_conflict_means_already_up_to_date(env, client, prompt_file, capsys):
    client.push_prompt.side_effect = LangSmithConflictError("409 Conflict: nothing to commit")

    assert push_prompts.main() == 0
    assert "já está atualizado" in capsys.readouterr().out


def test_other_push_error_returns_error(env, client, prompt_file, capsys):
    client.push_prompt.side_effect = RuntimeError("boom")

    assert push_prompts.main() == 1
    assert "Erro ao fazer push" in capsys.readouterr().out


def test_output_never_contains_api_key(env, client, prompt_file, capsys):
    push_prompts.main()
    client.push_prompt.side_effect = RuntimeError(f"auth failed for {FAKE_KEY}")
    push_prompts.main()

    captured = capsys.readouterr()
    assert FAKE_KEY not in captured.out
    assert FAKE_KEY not in captured.err
