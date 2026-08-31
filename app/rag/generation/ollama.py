import json
import re
from urllib.error import URLError
from urllib.request import Request, urlopen

DEFAULT_OLLAMA_MODEL = "qwen3:4b"
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_OLLAMA_TIMEOUT = 300.0


class OllamaLLMProvider:
    """Local LLM provider backed by Ollama."""

    def __init__(
        self,
        model: str = DEFAULT_OLLAMA_MODEL,
        base_url: str = DEFAULT_OLLAMA_URL,
        timeout: float = DEFAULT_OLLAMA_TIMEOUT,
    ) -> None:
        if not model.strip():
            raise ValueError("model cannot be empty.")

        if not base_url.strip():
            raise ValueError("base_url cannot be empty.")

        if timeout <= 0:
            raise ValueError(
                "timeout must be greater than 0."
            )

        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(
        self,
        prompt: str,
    ) -> str:
        """Generate one structured non-streaming response."""

        if not prompt.strip():
            raise ValueError(
                "prompt cannot be empty."
            )

        request_prompt = prompt

        if "qwen3" in self.model.lower():
            request_prompt = (
                "/no_think\n"
                f"{prompt}"
            )

        payload = json.dumps(
            {
                "model": self.model,
                "prompt": request_prompt,
                "stream": False,
                "think": False,
                "format": "json",
                "keep_alive": "10m",
                "options": {
                    "temperature": 0.0,
                    "num_predict": 192,
                },
            }
        ).encode()

        request = Request(
            url=f"{self.base_url}/api/generate",
            data=payload,
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                body = response.read().decode()

        except TimeoutError as exc:
            raise TimeoutError(
                "Ollama generation exceeded the configured timeout."
            ) from exc

        except URLError as exc:
            raise ConnectionError(
                "Could not connect to Ollama."
            ) from exc

        data = json.loads(body)

        answer = data.get("response")

        if not isinstance(answer, str):
            raise TypeError(
                "Ollama returned an invalid response."
            )

        answer = re.sub(
            r"<think>.*?</think>",
            "",
            answer,
            flags=re.DOTALL | re.IGNORECASE,
        ).strip()

        if not answer:
            raise ValueError(
                "Ollama returned an empty response."
            )

        return answer