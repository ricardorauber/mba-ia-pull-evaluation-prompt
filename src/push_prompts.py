"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)
"""

import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langsmith.utils import LangSmithConflictError
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()

PROMPT_KEY = "bug_to_user_story_v2"
PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / f"{PROMPT_KEY}.yml"
INPUT_VARIABLE = "bug_report"


def build_chat_prompt(prompt_data: dict) -> ChatPromptTemplate:
    """Build the chat template from the system and user prompts."""
    return ChatPromptTemplate.from_messages([
        ("system", prompt_data["system_prompt"]),
        ("user", prompt_data["user_prompt"]),
    ])


def slugify(text: str) -> str:
    """Turn a technique name into a Hub tag (e.g. "Few-shot Learning" -> "few-shot-learning")."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def build_tags(prompt_data: dict) -> list:
    """YAML tags followed by one tag per technique, without duplicates."""
    tags = list(prompt_data.get("tags", []))
    tags += [slugify(t) for t in prompt_data.get("techniques_applied", [])]
    return list(dict.fromkeys(tag for tag in tags if tag))


def build_readme(prompt_data: dict) -> str:
    """Markdown readme shown on the Hub page."""
    techniques = "\n".join(f"- {t}" for t in prompt_data.get("techniques_applied", []))
    return (
        f"# {PROMPT_KEY}\n\n"
        f"{prompt_data.get('description', '')}\n\n"
        f"**Versão:** {prompt_data.get('version', '')}\n\n"
        f"## Técnicas aplicadas\n\n{techniques}\n\n"
        f"## Entrada\n\n- `{{{INPUT_VARIABLE}}}`: relato do bug a ser convertido em User Story\n"
    )


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        client = Client()
        url = client.push_prompt(
            prompt_name,
            object=build_chat_prompt(prompt_data),
            is_public=True,
            description=prompt_data.get("description", ""),
            readme=build_readme(prompt_data),
            tags=build_tags(prompt_data),
        )
    except LangSmithConflictError:
        print(f"   ✓ O prompt '{prompt_name}' já está atualizado no LangSmith Hub (nada mudou desde o último push)")
        return True
    except Exception as e:
        print(f"❌ Erro ao fazer push do prompt '{prompt_name}': {type(e).__name__}")
        print("   Verifique a LANGSMITH_API_KEY, o USERNAME_LANGSMITH_HUB e sua conexão.")
        return False

    print(f"   ✓ Prompt publicado: {prompt_name}")
    print(f"   ✓ {url}")
    return True


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    _, errors = validate_prompt_structure(prompt_data)
    errors = list(errors)

    user_prompt = prompt_data.get("user_prompt") or ""
    if not user_prompt.strip():
        errors.append("Campo obrigatório faltando: user_prompt")
    elif (prompt_data.get("system_prompt") or "").strip():
        try:
            variables = build_chat_prompt(prompt_data).input_variables
        except Exception as e:
            errors.append(f"Template inválido: {e}")
        else:
            if sorted(variables) != [INPUT_VARIABLE]:
                errors.append(
                    f"O template deve usar apenas a variável {{{INPUT_VARIABLE}}}, "
                    f"encontradas: {sorted(variables)}"
                )

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    data = load_yaml(str(PROMPT_FILE))
    if data is None:
        return 1

    prompt_data = data.get(PROMPT_KEY) if isinstance(data, dict) else None
    if not prompt_data:
        print(f"❌ Prompt '{PROMPT_KEY}' não encontrado em {PROMPT_FILE}")
        return 1

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ O prompt não passou na validação:")
        for error in errors:
            print(f"   - {error}")
        return 1

    prompt_name = f"{os.getenv('USERNAME_LANGSMITH_HUB')}/{PROMPT_KEY}"
    print(f"Publicando {prompt_name}...")

    if not push_prompt_to_langsmith(prompt_name, prompt_data):
        return 1

    print("\n✅ Push concluído com sucesso!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
