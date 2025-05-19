# Python Cartola FC API

[![PyPI](https://img.shields.io/pypi/v/python-cartolafc.svg)](https://pypi.org/project/python-cartolafc/)
[![CI](https://github.com/vicenteneto/python-cartolafc/actions/workflows/main.yml/badge.svg)](https://github.com/vicenteneto/python-cartolafc/actions/workflows/main.yml)
[![Development Status](https://img.shields.io/:status-alpha/development-red.svg)](https://github.com/vicenteneto/python-cartolafc)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]([LICENSE](https://github.com/vicenteneto/python-cartolafc/blob/main/LICENSE))

> **Uma interface moderna em Python (≥ 3.11) para a API REST do [Cartola FC](https://cartolafc.globo.com/).**

This project is a complete rewrite of the original **Python‑CartolaFC** library, now featuring:

* 🔌 **httpx** under the hood (sync & async)
* 🛡️ **Pydantic v2** typed models (extra‑field tolerant)
* 🍰 Simple, composable API surface – `CartolaClient` & `CartolaAsyncClient`
* 💅 Pre‑commit tooling (ruff 🚀, black, mypy) and Hatch build backend

Portuguese docs are included below for the Brazilian community ⚽.

---

## Table of contents  •  Índice

* [Features / Funcionalidades](#features--funcionalidades)
* [Installation / Instalação](#installation--instalação)
* [Quick start](#quick-start)
  * [Synchronous](#synchronous)
  * [Asynchronous](#asynchronous)
* [Development](#development)
* [Contributing / Contribuindo](#contributing--contribuindo)
* [License](#license)

---

## Features • Funcionalidades

| English | Português |
|---------|-----------|
| • Sync **and** async clients | • Clientes **síncrono** e **assíncrono** |
| • Typed models for Club, Player, Market, League, etc. | • Modelos tipados para Clube, Atleta, Mercado, Liga, etc. |
| • Graceful handling of extra/unknown API fields | • Tolera campos extras adicionados pela API |
| • Python ≥ 3.11, zero legacy deps | • Requer Python ≥ 3.11, sem dependências legadas |

---

## Installation • Instalação

```bash
# Stable release (PyPI)
pip install python-cartolafc

# Bleeding‑edge (GitHub main)
pip install git+https://github.com/vicenteneto/python-cartolafc.git
```

---

## Quick start

### Synchronous

```python
from cartolafc import CartolaClient
from cartolafc.models import Mercado

with CartolaClient() as api:
    raw = api.mercado_status()
    mercado = Mercado.model_validate(raw)

print(f"Round {mercado.rodada_atual} • status = {mercado.status.name}")
```

### Asynchronous

```python
import asyncio
from cartolafc import CartolaAsyncClient
from cartolafc.models import Mercado

async def main():
    async with CartolaAsyncClient() as api:
        raw = await api.mercado_status()
        mercado = Mercado.model_validate(raw)
        print(mercado.fechamento.as_datetime)

asyncio.run(main())
```

> **Note:** Some endpoints require an authentication token (`X‑GLB‑Token`). Pass it to the client constructor: `CartolaClient(token="abc123")`.

---

## Development

```bash
# Clone & install dev extras
git clone https://github.com/vicenteneto/python-cartolafc.git
cd python-cartolafc
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# Run checks & tests
pre-commit run --all-files
pytest
```

---

## Contributing • Contribuindo

Spotted a bug, translation typo, or have a feature request?  
Abra uma [Issue](https://github.com/vicenteneto/python-cartolafc/issues) ou mande um PR – ficaremos felizes em revisar!

---

## License

MIT © 2025  Vicente Ramos
