TAREFAS = [
    {
        "nome": "classificacao_sentimento",
        "tipo": "classificacao",
        "instrucao": "Classifique como POSITIVO, NEGATIVO, NEUTRO ou MISTO",
        "formato_output": "Responda APENAS com a classificacao (uma palavra).",
        "exemplos_fewshot": [
            {"input": "Adorei!", "output": "POSITIVO"},
            {"input": "Pessimo.", "output": "NEGATIVO"},
            {"input": "Bom mas com defeito.", "output": "MISTO"},
        ],
        "passos_cot": [
            "Identifique aspectos positivos no texto",
            "Identifique aspectos negativos no texto",
            "Compare e classifique o sentimento geral",
        ],
        "persona": "analista_cx",
    },
    {
        "nome": "extracao_dados",
        "tipo": "extracao",
        "instrucao": "Extraia produto, preco e defeito mencionados no texto",
        "formato_output": (
            'Responda APENAS em JSON: {"produto": "...", "preco": "...", "defeito": "..."}'
        ),
        "exemplos_fewshot": [
            {
                "input": "Notebook Dell de R$3500 com pixels mortos",
                "output": '{"produto": "Notebook Dell", "preco": "R$3500", "defeito": "pixels mortos"}',
            },
            {
                "input": "Fone JBL R$299, bateria nao carrega",
                "output": '{"produto": "Fone JBL", "preco": "R$299", "defeito": "bateria nao carrega"}',
            },
        ],
        "passos_cot": [
            "Identifique o produto mencionado",
            "Identifique o preco mencionado",
            "Identifique o defeito ou problema relatado",
            "Monte o JSON com os tres campos",
        ],
        "persona": "especialista_dados",
    },
    {
        "nome": "sumarizacao_avaliacao",
        "tipo": "sumarizacao",
        "instrucao": "Resuma a avaliacao em ate 3 bullet points objetivos",
        "formato_output": "Responda com bullet points (- item), um por linha, maximo 3 itens.",
        "exemplos_fewshot": [
            {
                "input": "Produto bom, entrega rapida, embalagem ruim.",
                "output": "- Produto de boa qualidade\n- Entrega rapida\n- Embalagem danificada",
            },
        ],
        "passos_cot": [
            "Identifique pontos positivos",
            "Identifique pontos negativos",
            "Sintetize em ate 3 bullet points",
        ],
        "persona": "analista_cx",
    },
]


def obter_tarefas():
    """Retorna a lista de tarefas do dominio."""
    return TAREFAS


def obter_tarefa_por_nome(nome):
    """Busca uma tarefa pelo nome."""
    for tarefa in TAREFAS:
        if tarefa["nome"] == nome:
            return tarefa
    raise ValueError(f"Tarefa '{nome}' nao encontrada.")
