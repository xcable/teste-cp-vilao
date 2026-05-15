import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Cliente para chamar a API REST do Ollama."""

    def __init__(self):
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))
        self.max_retries = int(os.getenv("OLLAMA_MAX_RETRIES", "3"))
        self.url = f"{self.host.rstrip('/')}/api/chat"

    def chat(self, prompt, system=None, temp=0.7, max_tokens=512):
        """
        Envia mensagem ao Ollama e retorna resposta com metricas.

        Retorna dict: resposta, tokens_prompt, tokens_resposta, tempo_ms
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temp,
                "num_predict": max_tokens,
            },
        }

        ultimo_erro = None
        for tentativa in range(1, self.max_retries + 1):
            try:
                inicio = time.time()
                resposta_http = requests.post(
                    self.url,
                    json=payload,
                    timeout=self.timeout,
                )
                tempo_ms = int((time.time() - inicio) * 1000)

                if resposta_http.status_code == 429:
                    ultimo_erro = "Rate limit (429). Aguardando retry..."
                    time.sleep(2 * tentativa)
                    continue

                resposta_http.raise_for_status()
                dados = resposta_http.json()

                texto = dados.get("message", {}).get("content", "")
                tokens_prompt = dados.get("prompt_eval_count", 0)
                tokens_resposta = dados.get("eval_count", 0)

                return {
                    "resposta": texto.strip(),
                    "tokens_prompt": tokens_prompt,
                    "tokens_resposta": tokens_resposta,
                    "tempo_ms": tempo_ms,
                }

            except requests.exceptions.Timeout:
                ultimo_erro = f"Timeout apos {self.timeout}s"
                time.sleep(1 * tentativa)
            except requests.exceptions.ConnectionError:
                ultimo_erro = "Nao foi possivel conectar ao Ollama. Verifique se esta rodando."
                time.sleep(1 * tentativa)
            except requests.exceptions.RequestException as erro:
                ultimo_erro = str(erro)
                time.sleep(1 * tentativa)

        raise RuntimeError(
            f"Falha ao chamar Ollama apos {self.max_retries} tentativas: {ultimo_erro}"
        )
