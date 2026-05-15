# Prompt Toolkit — Checkpoint 02

Toolkit Python que aplica automaticamente as 4 tecnicas de prompting (Zero-Shot, Few-Shot, Chain-of-Thought e Role Prompting) a tarefas de e-commerce, compara resultados e recomenda a melhor abordagem.

## Dominio

E-commerce — analise de avaliacoes de produtos (classificacao de sentimento, extracao de dados e sumarizacao).

## Requisitos

- Python 3.10+
- [Ollama](https://ollama.com/) instalado e rodando localmente
- Modelo `gpt-oss:120b` (ou outro configurado no `.env`)

## Instalacao

```bash
cd teste-cp-vilao
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Edite o arquivo `.env` se necessario:

```
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gpt-oss:120b
```

Certifique-se de que o Ollama esta rodando e o modelo foi baixado:

```bash
ollama pull gpt-oss:120b
ollama serve
```

## Execucao

Na raiz do projeto:

```bash
python main.py
```

O sistema ira:

1. Carregar inputs de `data/inputs.json` e prompts de `prompts/`
2. Executar 4 tecnicas para cada uma das 3 tarefas
3. Medir acuracia, tokens e tempo
4. Gerar CSV em `output/resultados.csv`
5. Gerar graficos em `output/graficos/`
6. Exibir recomendacao da melhor tecnica por tarefa
7. Executar teste de temperatura (0.1, 0.5, 1.0)

## Estrutura

```
teste-cp-vilao/
├── main.py              # Ponto de entrada
├── src/
│   ├── llm_client.py    # Conexao Ollama
│   ├── prompt_builder.py
│   ├── techniques.py    # ZS, FS, CoT, Role
│   ├── tasks.py         # 3 tarefas do dominio
│   ├── evaluator.py     # Metricas
│   └── report.py        # Tabelas e graficos
├── data/
├── prompts/
└── output/
```

## Documentacao

O PDF do grupo deve ser colocado em `docs/CP02_NomeDoGrupo.pdf`.
