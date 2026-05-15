import json
import re

import tiktoken

from src.llm_client import LLMClient


def contar_tokens(texto, modelo="gpt-4"):
    """Conta tokens de um texto usando tiktoken."""
    if not texto:
        return 0
    try:
        encoding = tiktoken.encoding_for_model(modelo)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(str(texto)))


def medir_acuracia(resposta, esperado):
    """
    Mede acuracia por match exato ou por keywords.
    Retorna valor entre 0.0 e 1.0.
    """
    if resposta is None or esperado is None:
        return 0.0

    resp = str(resposta).strip().upper()
    esp = esperado

    if isinstance(esp, dict):
        try:
            resp_json = json.loads(resposta)
            if isinstance(resp_json, dict):
                campos_ok = 0
                total = len(esp)
                for chave, valor in esp.items():
                    valor_resp = str(resp_json.get(chave, "")).lower()
                    valor_esp = str(valor).lower()
                    if valor_esp in valor_resp or valor_resp in valor_esp:
                        campos_ok += 1
                return campos_ok / total if total > 0 else 0.0
        except (json.JSONDecodeError, TypeError):
            pass

        texto_resp = str(resposta).lower()
        acertos = sum(1 for v in esp.values() if str(v).lower() in texto_resp)
        return acertos / len(esp) if esp else 0.0

    esp_str = str(esp).strip().upper()
    if resp == esp_str:
        return 1.0

    palavras_esperadas = re.split(r"[;,|\s]+", str(esp).lower())
    palavras_esperadas = [p for p in palavras_esperadas if len(p) > 2]
    if not palavras_esperadas:
        return 0.0

    texto = str(resposta).lower()
    encontradas = sum(1 for p in palavras_esperadas if p in texto)
    return encontradas / len(palavras_esperadas)


def medir_consistencia(respostas):
    """
    Mede consistencia: mesma pergunta N vezes, % de respostas iguais.
    respostas: lista de strings
    """
    if not respostas:
        return 0.0
    if len(respostas) == 1:
        return 1.0

    normalizadas = [str(r).strip().upper() for r in respostas]
    mais_comum = max(set(normalizadas), key=normalizadas.count)
    iguais = normalizadas.count(mais_comum)
    return iguais / len(normalizadas)


def testar_temperatura(client, prompt, system=None, temps=None, repeticoes=3):
    """
    Roda o mesmo prompt com temperaturas 0.1, 0.5 e 1.0.
    Retorna lista de dicts com resultados por temperatura.
    """
    if temps is None:
        temps = [0.1, 0.5, 1.0]

    resultados = []
    for temp in temps:
        respostas = []
        tokens_total = 0
        tempo_total = 0

        for _ in range(repeticoes):
            resultado = client.chat(prompt, system=system, temp=temp)
            respostas.append(resultado["resposta"])
            tokens_total += resultado["tokens_prompt"] + resultado["tokens_resposta"]
            tempo_total += resultado["tempo_ms"]

        resultados.append({
            "temperatura": temp,
            "respostas": respostas,
            "consistencia": medir_consistencia(respostas),
            "tokens_medio": tokens_total / repeticoes,
            "tempo_medio_ms": tempo_total / repeticoes,
        })

    return resultados


def criar_resultado(
    tarefa,
    tecnica,
    input_texto,
    esperado,
    resposta_llm,
    tokens_prompt,
    tokens_resposta,
    tempo_ms,
):
    """Monta dict padronizado para o report."""
    acuracia = medir_acuracia(resposta_llm, esperado)
    return {
        "tarefa": tarefa,
        "tecnica": tecnica,
        "input": input_texto,
        "esperado": esperado,
        "resposta": resposta_llm,
        "acuracia": acuracia,
        "tokens_prompt": tokens_prompt,
        "tokens_resposta": tokens_resposta,
        "tokens_total": tokens_prompt + tokens_resposta,
        "tempo_ms": tempo_ms,
    }
