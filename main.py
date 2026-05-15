import json
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from src import report, techniques
from src.evaluator import criar_resultado, testar_temperatura
from src.llm_client import LLMClient
from src.tasks import obter_tarefas

load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
PROMPTS_DIR = BASE_DIR / "prompts"


def carregar_json(caminho):
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def executar_tecnica(client, tarefa, tecnica, input_texto, exemplos_json):
    """Aplica uma tecnica e retorna resposta do LLM."""
    nome = tarefa["nome"]

    if tecnica == "zero_shot":
        prompt = techniques.zero_shot(tarefa, input_texto)
        return client.chat(prompt)

    if tecnica == "few_shot":
        exemplos = tarefa.get("exemplos_fewshot") or exemplos_json.get(nome, [])
        prompt = techniques.few_shot(tarefa, input_texto, exemplos)
        return client.chat(prompt)

    if tecnica == "chain_of_thought":
        passos = tarefa.get("passos_cot", [])
        prompt = techniques.chain_of_thought(tarefa, input_texto, passos)
        return client.chat(prompt)

    if tecnica == "role_prompting":
        system, user = techniques.role_prompting(
            tarefa, input_texto, tarefa["persona"]
        )
        return client.chat(user, system=system)

    raise ValueError(f"Tecnica desconhecida: {tecnica}")


def main():
    print("=" * 60)
    print("Prompt Toolkit - Checkpoint 02")
    print("Dominio: E-commerce (avaliacoes de produtos)")
    print("=" * 60)

    inputs = carregar_json(DATA_DIR / "inputs.json")
    exemplos = carregar_json(DATA_DIR / "examples.json")
    carregar_json(PROMPTS_DIR / "system_prompts.json")
    carregar_json(PROMPTS_DIR / "templates.json")

    client = LLMClient()
    tarefas = obter_tarefas()
    tecnicas_lista = ["zero_shot", "few_shot", "chain_of_thought", "role_prompting"]

    resultados = []
    melhor_por_tarefa = {}

    for tarefa in tarefas:
        nome_tarefa = tarefa["nome"]
        lista_inputs = inputs.get(nome_tarefa, [])

        if len(lista_inputs) < 5:
            print(f"Aviso: '{nome_tarefa}' tem menos de 5 inputs.")

        print(f"\n--- Tarefa: {nome_tarefa} ({tarefa['tipo']}) ---")

        for item in lista_inputs:
            texto_input = item["input"]
            esperado = item["esperado"]

            for tecnica in tecnicas_lista:
                print(f"  {tecnica} ... ", end="", flush=True)
                try:
                    resposta_llm = executar_tecnica(
                        client, tarefa, tecnica, texto_input, exemplos
                    )
                    resultado = criar_resultado(
                        tarefa=nome_tarefa,
                        tecnica=tecnica,
                        input_texto=texto_input,
                        esperado=esperado,
                        resposta_llm=resposta_llm["resposta"],
                        tokens_prompt=resposta_llm["tokens_prompt"],
                        tokens_resposta=resposta_llm["tokens_resposta"],
                        tempo_ms=resposta_llm["tempo_ms"],
                    )
                    resultados.append(resultado)
                    print(f"ok (acuracia={resultado['acuracia']:.0%})")
                except Exception as erro:
                    print(f"erro: {erro}")

    if not resultados:
        print("\nNenhum resultado gerado. Verifique se o Ollama esta rodando.")
        return

    df = report.gerar_tabela(resultados)
    report.exibir_tabela_terminal(df)
    report.grafico_acuracia(resultados)
    report.grafico_custo(resultados)

    recomendacoes = report.recomendar(resultados)

    print("\n" + "=" * 60)
    print("TESTE DE TEMPERATURA (melhor tecnica por tarefa)")
    print("=" * 60)

    resultados_temp = []
    for rec in recomendacoes:
        tarefa = next(t for t in tarefas if t["nome"] == rec["tarefa"])
        melhor_tecnica = rec["tecnica_recomendada"]
        primeiro_input = inputs[rec["tarefa"]][0]["input"]

        if melhor_tecnica == "zero_shot":
            prompt = techniques.zero_shot(tarefa, primeiro_input)
            system = None
        elif melhor_tecnica == "few_shot":
            ex = tarefa.get("exemplos_fewshot") or exemplos.get(rec["tarefa"], [])
            prompt = techniques.few_shot(tarefa, primeiro_input, ex)
            system = None
        elif melhor_tecnica == "chain_of_thought":
            prompt = techniques.chain_of_thought(
                tarefa, primeiro_input, tarefa.get("passos_cot", [])
            )
            system = None
        else:
            system, prompt = techniques.role_prompting(
                tarefa, primeiro_input, tarefa["persona"]
            )

        print(f"\nTarefa {rec['tarefa']} com tecnica {melhor_tecnica}:")
        temps = testar_temperatura(client, prompt, system=system)
        for item in temps:
            item["tarefa"] = rec["tarefa"]
            item["tecnica"] = melhor_tecnica
            resultados_temp.append(item)
            print(
                f"  temp={item['temperatura']}: "
                f"consistencia={item['consistencia']:.0%}"
            )

        melhor_por_tarefa[rec["tarefa"]] = melhor_tecnica

    if resultados_temp:
        report.grafico_temperatura(resultados_temp)

    print("\n" + "=" * 60)
    print("Execucao finalizada. Arquivos em output/")
    print("=" * 60)


if __name__ == "__main__":
    main()
