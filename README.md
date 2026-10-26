# Azure OpenAI Python

[![CI](https://github.com/raresjuretchi/azure-openai-python/actions/workflows/ci.yml/badge.svg)](https://github.com/raresjuretchi/azure-openai-python/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Small, runnable scripts for **Azure OpenAI in Microsoft Foundry** using the OpenAI-compatible **v1 API** and the standard `openai` Python SDK, with **keyless Microsoft Entra ID authentication** by default and API keys as a fallback.

## Quick start

```bash
git clone https://github.com/raresjuretchi/azure-openai-python.git
cd azure-openai-python
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set the endpoint and deployment name
az login               # for keyless auth
python -m azure_openai_examples.hello
```

## The scripts

| Script | What it shows |
|---|---|
| `python -m azure_openai_examples.hello "…"` | One request to your deployment with the Responses API |
| `python -m azure_openai_examples.stream "…"` | Streaming output deltas |
| `python -m azure_openai_examples.summarize file.md` | Structured outputs: a document summarised into a strict JSON schema |

## Create a resource and deployment (Azure CLI)

```bash
RG=rg-openai-demo; NAME=my-openai-$RANDOM; LOCATION=swedencentral

az group create -n $RG -l $LOCATION
az cognitiveservices account create -n $NAME -g $RG -l $LOCATION \
  --kind OpenAI --sku S0 --custom-domain $NAME --yes

# Pick a model your region offers
az cognitiveservices account list-models -n $NAME -g $RG -o table

az cognitiveservices account deployment create -n $NAME -g $RG \
  --deployment-name chat --model-name <model-name> --model-version <version> \
  --model-format OpenAI --sku-name GlobalStandard --sku-capacity 10

# Keyless access for your own user
az role assignment create --assignee "$(az ad signed-in-user show --query id -o tsv)" \
  --role "Cognitive Services OpenAI User" \
  --scope "$(az cognitiveservices account show -n $NAME -g $RG --query id -o tsv)"
```

Then set `AZURE_OPENAI_ENDPOINT=https://$NAME.openai.azure.com` and `AZURE_OPENAI_DEPLOYMENT=chat`. Role assignments can take a few minutes to apply.

## Configuration

| Variable | Purpose |
|---|---|
| `AZURE_OPENAI_ENDPOINT` | `https://<resource>.openai.azure.com` (the script adds `/openai/v1/`) |
| `AZURE_OPENAI_DEPLOYMENT` | Your deployment name — Azure uses it as the `model` value |
| `AZURE_OPENAI_API_KEY` | Optional. When empty, `DefaultAzureCredential` is used (Azure CLI locally, managed identity in Azure) |

The v1 route uses implicit versioning, so there is no `api-version` to manage.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The tests fake the client, so they run offline without an Azure subscription.

## Maintenance

A scheduled workflow checks the pinned dependencies once a week at a random time, bumps them when the tests still pass and records the result in [MAINTENANCE.md](MAINTENANCE.md).

<!-- maintenance:start -->
**Last maintenance:** 2026-10-26 · All 4 pinned packages current · tests ✅ 10 passed
<!-- maintenance:end -->

## License

MIT — see [LICENSE](LICENSE).
