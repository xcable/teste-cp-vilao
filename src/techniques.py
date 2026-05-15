import json
from pathlib import Path

from src import prompt_builder

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"


def _carregar_json(arquivo):
    caminho = PROMPTS_DIR / arquivo
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def _montar_instrucao(tarefa):
    return tarefa["instrucao"]


def _montar_contexto(tarefa):
    templates = _carregar_json("templates.json")
    nome = tarefa["nome"]
    if nome in templates:
        return templates[nome].get("contexto", "")
    return "Analise o texto fornecido conforme a tarefa solicitada."


def _formato_output(tarefa):
    return tarefa["formato_output"]


def zero_shot(tarefa, input_texto):
    """Zero-Shot: prompt direto sem exemplos."""
    prompt = prompt_builder.montar_prompt(
        instrucao=_montar_instrucao(tarefa),
        contexto=_montar_contexto(tarefa),
        input_dados=input_texto,
        formato_output=_formato_output(tarefa),
    )
    return prompt


def few_shot(tarefa, input_texto, exemplos):
    """Few-Shot: prompt com 2-3 exemplos Input -> Output."""
    prompt_base = prompt_builder.montar_prompt(
        instrucao=_montar_instrucao(tarefa),
        contexto=_montar_contexto(tarefa),
        input_dados=input_texto,
        formato_output=_formato_output(tarefa),
    )
    return prompt_builder.adicionar_exemplos(prompt_base, exemplos)


def chain_of_thought(tarefa, input_texto, passos):
    """Chain-of-Thought: raciocinio explicito passo a passo."""
    prompt_base = prompt_builder.montar_prompt(
        instrucao=_montar_instrucao(tarefa),
        contexto=_montar_contexto(tarefa),
        input_dados=input_texto,
        formato_output=_formato_output(tarefa),
    )
    return prompt_builder.adicionar_cot(prompt_base, passos)


def role_prompting(tarefa, input_texto, persona):
    """
    Role Prompting: usa persona do system_prompts.json.
    Retorna tupla (system, user).
    """
    personas = _carregar_json("system_prompts.json")
    if persona not in personas:
        raise ValueError(f"Persona '{persona}' nao encontrada em system_prompts.json.")

    dados_persona = personas[persona]
    system = f"""Voce e {dados_persona['nome']}.

Experiencia: {dados_persona['experiencia']}
Especialidade: {dados_persona['especialidade']}
Tom de voz: {dados_persona['tom_de_voz']}
Limitacoes: {dados_persona['limitacoes']}"""

    user = prompt_builder.montar_prompt(
        instrucao=_montar_instrucao(tarefa),
        contexto=_montar_contexto(tarefa),
        input_dados=input_texto,
        formato_output=_formato_output(tarefa),
    )

    return system, user
