"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt semente do desafio
3. Salva localmente em prompts/bug_to_user_story_v1.yml
"""

import sys
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

SEED_PROMPT = "leonanluppi/bug_to_user_story_v1"
PROMPT_KEY = "bug_to_user_story_v1"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "prompts" / f"{PROMPT_KEY}.yml"
DESCRIPTION = "Prompt para converter relatos de bugs em User Stories"
TAGS = ["bug-analysis", "user-story", "product-management"]


def prompt_to_dict(prompt: ChatPromptTemplate) -> dict:
    """Convert the pulled chat template into the local YAML structure."""
    system_prompt = ""
    user_prompt = ""

    for message in prompt.messages:
        if isinstance(message, SystemMessagePromptTemplate):
            system_prompt = message.prompt.template
        elif isinstance(message, HumanMessagePromptTemplate):
            user_prompt = message.prompt.template

    return {
        PROMPT_KEY: {
            "description": DESCRIPTION,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "created_at": date.today().isoformat(),
            "tags": list(TAGS),
            "source": SEED_PROMPT,
        }
    }


def pull_prompts_from_langsmith(output_path: Path = OUTPUT_PATH) -> bool:
    """Pull the seed prompt from the Hub and save it as YAML."""
    try:
        client = Client()
        # The seed prompt is owned by a third party ("owner/name"), so the Hub
        # requires an explicit opt-in to deserialize it. Only this fixed,
        # known identifier is ever pulled with this flag.
        prompt = client.pull_prompt(SEED_PROMPT, dangerously_pull_public_prompt=True)
    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt '{SEED_PROMPT}': {type(e).__name__}")
        print("   Verifique a LANGSMITH_API_KEY, o LANGSMITH_ENDPOINT e sua conexão.")
        return False

    print(f"   ✓ Prompt '{SEED_PROMPT}' carregado do LangSmith Hub")

    if not save_yaml(prompt_to_dict(prompt), str(output_path)):
        print(f"❌ Não foi possível salvar o prompt em {output_path}")
        return False

    print(f"   ✓ Prompt salvo em {output_path}")
    return True


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    if not pull_prompts_from_langsmith(OUTPUT_PATH):
        return 1

    print("\n✅ Pull concluído com sucesso!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
