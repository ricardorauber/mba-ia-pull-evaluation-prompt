"""
Testes automatizados para validação de prompts.
"""
import json
import re
import pytest
import yaml
import sys
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

ROOT = Path(__file__).parent.parent
PROMPT_FILE = ROOT / "prompts" / "bug_to_user_story_v2.yml"
DATASET_FILE = ROOT / "datasets" / "bug_to_user_story.jsonl"
PROMPT_KEY = "bug_to_user_story_v2"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt():
    return load_prompts(PROMPT_FILE)[PROMPT_KEY]


@pytest.fixture(scope="module")
def system_prompt(prompt):
    return prompt["system_prompt"]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt
        assert isinstance(prompt["system_prompt"], str)
        assert prompt["system_prompt"].strip()

    def test_prompt_has_role_definition(self, system_prompt):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        assert re.search(r"Você é uma? [A-ZÀ-Ú][\w-]+", system_prompt)
        assert "Product Manager" in system_prompt

    def test_prompt_mentions_format(self, system_prompt):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        assert "User Story" in system_prompt or "Markdown" in system_prompt
        assert re.search(r"Como um .+, eu quero .+, para que", system_prompt)
        assert "Critérios de Aceitação" in system_prompt
        assert "Dado que" in system_prompt

    def test_prompt_has_few_shot_examples(self, system_prompt):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        lines = [line.strip() for line in system_prompt.splitlines()]
        inputs = lines.count("Relato de bug:")
        outputs = lines.count("User Story:")
        assert inputs >= 2
        assert outputs >= 2
        assert inputs == outputs

    def test_prompt_no_todos(self, prompt):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        text = yaml.safe_dump(prompt, allow_unicode=True)
        assert "[TODO]" not in text
        assert "TODO" not in text
        assert validate_prompt_structure(prompt) == (True, [])

    def test_minimum_techniques(self, prompt):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt.get("techniques_applied", [])
        assert isinstance(techniques, list)
        assert len(techniques) >= 2
        assert all(isinstance(t, str) and t.strip() for t in techniques)

    def test_template_has_only_bug_report_variable(self, prompt):
        """Verifica se o template montado do YAML usa apenas a variável {bug_report}."""
        template = ChatPromptTemplate.from_messages([
            ("system", prompt["system_prompt"]),
            ("user", prompt["user_prompt"]),
        ])
        assert template.input_variables == ["bug_report"]
        assert "{bug_report}" not in prompt["system_prompt"]

    def test_prompt_does_not_copy_dataset_examples(self, system_prompt):
        """Garante que os exemplos Few-shot não foram copiados do dataset de avaliação."""
        with open(DATASET_FILE, 'r', encoding='utf-8') as f:
            reports = [json.loads(line)["inputs"]["bug_report"] for line in f if line.strip()]

        for report in reports:
            first_line = report.strip().splitlines()[0]
            assert first_line not in system_prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
