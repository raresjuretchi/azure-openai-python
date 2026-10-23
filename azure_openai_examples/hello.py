"""One request to your Azure OpenAI deployment.

    python -m azure_openai_examples.hello "What is an Azure landing zone?"
"""
from azure_openai_examples.client import auth_mode, deployment, get_client, prompt_from_args


def ask(client, model: str, prompt: str) -> str:
    return client.responses.create(model=model, input=prompt).output_text


def main() -> None:
    model = deployment()
    print(f"[{model} via {auth_mode()}]")
    print(ask(get_client(), model, prompt_from_args("In two sentences, what is an Azure landing zone?")))


if __name__ == "__main__":
    main()
