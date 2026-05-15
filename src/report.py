from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
GRAFICOS_DIR = OUTPUT_DIR / "graficos"


def gerar_tabela(resultados, salvar=True):
    """Gera DataFrame e salva CSV em output/resultados.csv."""
    df = pd.DataFrame(resultados)

    if salvar:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        caminho_csv = OUTPUT_DIR / "resultados.csv"
        df.to_csv(caminho_csv, index=False, encoding="utf-8")
        print(f"\nTabela salva em: {caminho_csv}")

    return df


def grafico_acuracia(resultados):
    """Grafico de barras: acuracia media por tecnica e tarefa."""
    df = pd.DataFrame(resultados)
    GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)

    media = df.groupby(["tarefa", "tecnica"])["acuracia"].mean().reset_index()
    tarefas = media["tarefa"].unique()
    tecnicas = media["tecnica"].unique()

    fig, ax = plt.subplots(figsize=(10, 6))
    largura = 0.2
    x = range(len(tarefas))

    for i, tecnica in enumerate(tecnicas):
        valores = []
        for tarefa in tarefas:
            linha = media[(media["tarefa"] == tarefa) & (media["tecnica"] == tecnica)]
            valores.append(linha["acuracia"].values[0] if len(linha) > 0 else 0)
        pos = [xi + i * largura for xi in x]
        ax.bar(pos, valores, width=largura, label=tecnica)

    ax.set_xticks([xi + largura for xi in x])
    ax.set_xticklabels(tarefas, rotation=15)
    ax.set_ylabel("Acuracia media")
    ax.set_title("Acuracia por tecnica e tarefa")
    ax.set_ylim(0, 1.1)
    ax.legend()
    plt.tight_layout()

    caminho = GRAFICOS_DIR / "acuracia.png"
    plt.savefig(caminho)
    plt.close()
    print(f"Grafico salvo: {caminho}")
    return caminho


def grafico_custo(resultados):
    """Grafico de barras: tokens medios por tecnica."""
    df = pd.DataFrame(resultados)
    GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)

    media = df.groupby("tecnica")["tokens_total"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(media["tecnica"], media["tokens_total"], color="steelblue")
    ax.set_ylabel("Tokens medios")
    ax.set_title("Custo (tokens) medio por tecnica")
    plt.xticks(rotation=15)
    plt.tight_layout()

    caminho = GRAFICOS_DIR / "custo.png"
    plt.savefig(caminho)
    plt.close()
    print(f"Grafico salvo: {caminho}")
    return caminho


def grafico_temperatura(resultados_temp):
    """Grafico: consistencia por temperatura."""
    if not resultados_temp:
        return None

    GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(resultados_temp)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(
        df["temperatura"].astype(str),
        df["consistencia"],
        color="coral",
    )
    ax.set_xlabel("Temperatura")
    ax.set_ylabel("Consistencia")
    ax.set_title("Consistencia das respostas por temperatura")
    ax.set_ylim(0, 1.1)
    plt.tight_layout()

    caminho = GRAFICOS_DIR / "temperatura.png"
    plt.savefig(caminho)
    plt.close()
    print(f"Grafico salvo: {caminho}")
    return caminho


def recomendar(resultados):
    """
    Recomenda a melhor tecnica por tarefa com base na acuracia media
    e custo (tokens).
    """
    df = pd.DataFrame(resultados)
    recomendacoes = []

    for tarefa in df["tarefa"].unique():
        subset = df[df["tarefa"] == tarefa]
        media = subset.groupby("tecnica").agg(
            acuracia_media=("acuracia", "mean"),
            tokens_medio=("tokens_total", "mean"),
        ).reset_index()

        melhor = media.sort_values(
            by=["acuracia_media", "tokens_medio"],
            ascending=[False, True],
        ).iloc[0]

        justificativa = (
            f"Para '{tarefa}', '{melhor['tecnica']}' teve acuracia media "
            f"{melhor['acuracia_media']:.2%} com ~{melhor['tokens_medio']:.0f} tokens."
        )
        recomendacoes.append({
            "tarefa": tarefa,
            "tecnica_recomendada": melhor["tecnica"],
            "acuracia_media": melhor["acuracia_media"],
            "tokens_medio": melhor["tokens_medio"],
            "justificativa": justificativa,
        })
        print(f"\n{justificativa}")

    return recomendacoes


def exibir_tabela_terminal(df):
    """Mostra resumo no terminal."""
    print("\n" + "=" * 60)
    print("RESULTADOS COMPARATIVOS")
    print("=" * 60)
    colunas = ["tarefa", "tecnica", "acuracia", "tokens_total", "tempo_ms"]
    print(df[colunas].to_string(index=False))
