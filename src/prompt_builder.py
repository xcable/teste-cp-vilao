def montar_prompt(instrucao, contexto, input_dados, formato_output):
    """
    Monta prompt separando instrucao, contexto, dados e formato.
    Valida que nenhum componente obrigatorio esta vazio.
    """
    componentes = {
        "instrucao": instrucao,
        "contexto": contexto,
        "input_dados": input_dados,
        "formato_output": formato_output,
    }

    for nome, valor in componentes.items():
        if not valor or not str(valor).strip():
            raise ValueError(f"Componente '{nome}' nao pode estar vazio.")

    prompt = f"""## Contexto
{contexto.strip()}

## Instrucao
{instrucao.strip()}

## Dados de entrada
{input_dados.strip()}

## Formato de saida
{formato_output.strip()}"""

    return prompt


def adicionar_exemplos(prompt, exemplos):
    """Adiciona exemplos few-shot no formato Input -> Output."""
    if not exemplos:
        raise ValueError("Lista de exemplos nao pode estar vazia para few-shot.")

    bloco = "\n\n## Exemplos\n"
    for i, ex in enumerate(exemplos, start=1):
        entrada = ex.get("input", "")
        saida = ex.get("output", "")
        if not entrada or not saida:
            raise ValueError(f"Exemplo {i} precisa ter 'input' e 'output'.")
        bloco += f'Input: "{entrada}"\nOutput: "{saida}"\n\n'

    return prompt + bloco.strip()


def adicionar_cot(prompt, passos):
    """Adiciona instrucao de raciocinio passo a passo (Chain-of-Thought)."""
    if not passos:
        raise ValueError("Lista de passos nao pode estar vazia para CoT.")

    bloco = "\n\n## Raciocinio\nAnalise passo a passo antes de responder:\n"
    for i, passo in enumerate(passos, start=1):
        bloco += f"{i}. {passo}\n"

    bloco += "\nDepois de analisar todos os passos, apresente a resposta final."
    return prompt + bloco
