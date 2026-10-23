"""Stream a reply from your Azure OpenAI deployment.

    python -m azure_openai_examples.stream "Explain hub-and-spoke networking"
"""
from azure_openai_examples.client import deployment, get_client, prompt_from_args


def stream_reply(client, model: str, prompt: str, out=print) -> str:
    chunks = []
    for event in client.responses.create(model=model, input=prompt, stream=True):
        if event.type == "response.output_text.delta":
            chunks.append(event.delta)
            out(event.delta, end="", flush=True)
        elif event.type == "error":
            raise RuntimeError(getattr(event, "message", "stream error"))
    out()
    return "".join(chunks)


def main() -> None:
    stream_reply(get_client(), deployment(), prompt_from_args("Explain hub-and-spoke networking in Azure briefly."))


if __name__ == "__main__":
    main()
