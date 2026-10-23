"""Build an OpenAI client that talks to an Azure OpenAI resource.

Azure OpenAI's v1 API is OpenAI-compatible: the standard `openai` client works
once `base_url` points at https://<resource>.openai.azure.com/openai/v1/.

Authentication, in order of preference:
  * Microsoft Entra ID (keyless) via DefaultAzureCredential — `az login` locally,
    managed identity in Azure. Needs the "Cognitive Services OpenAI User" role.
  * An API key in AZURE_OPENAI_API_KEY (simpler, but a secret to manage).
"""
from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

load_dotenv()

ENTRA_SCOPE = "https://ai.azure.com/.default"


def base_url(endpoint: str) -> str:
    """Normalise a resource endpoint or name into the v1 base URL."""
    endpoint = endpoint.strip().rstrip("/")
    if not endpoint.startswith("https://"):
        endpoint = f"https://{endpoint}.openai.azure.com"
    if endpoint.endswith("/openai/v1"):
        return endpoint + "/"
    return endpoint + "/openai/v1/"


def deployment() -> str:
    name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    if not name:
        sys.exit("AZURE_OPENAI_DEPLOYMENT is not set (the name you gave your model deployment).")
    return name


def get_client():
    from openai import OpenAI

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if not endpoint:
        sys.exit("AZURE_OPENAI_ENDPOINT is not set, e.g. https://my-resource.openai.azure.com")

    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if api_key:
        return OpenAI(base_url=base_url(endpoint), api_key=api_key)

    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    # Passing the provider (not a token) lets the client refresh tokens as they expire.
    token_provider = get_bearer_token_provider(DefaultAzureCredential(), ENTRA_SCOPE)
    return OpenAI(base_url=base_url(endpoint), api_key=token_provider)


def auth_mode() -> str:
    return "API key" if os.getenv("AZURE_OPENAI_API_KEY") else "Microsoft Entra ID"


def prompt_from_args(default: str) -> str:
    return " ".join(sys.argv[1:]).strip() or default
