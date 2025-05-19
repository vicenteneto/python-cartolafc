from __future__ import annotations

from typing import Any

import httpx

BASE_URL = "https://api.cartola.globo.com"


class CartolaClient:
    """Blocking (synchronous) API wrapper for Cartola FC."""

    def __init__(self, token: str | None = None, *, timeout: float = 10.0) -> None:
        self._client = httpx.Client(
            base_url=BASE_URL,
            timeout=timeout,
            headers={"User-Agent": "python-cartolafc/0.1.0"},
        )
        if token:
            self._client.headers["X-GLB-Token"] = token

    # Example endpoint  ──────────────────────────────────────────────
    def mercado_status(self) -> dict[str, Any]:
        """Return current market (mercado) status."""
        resp = self._client.get("/mercado/status")
        resp.raise_for_status()
        return resp.json()

    # Context‑manager helpers ───────────────────────────────────────
    def close(self) -> None:  # noqa: D401 – simple helper
        self._client.close()

    def __enter__(self) -> "CartolaClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        self.close()


class CartolaAsyncClient:
    """Async API wrapper for Cartola FC (uses *httpx.AsyncClient* under the hood)."""

    def __init__(self, token: str | None = None, *, timeout: float = 10.0) -> None:
        self._client = httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=timeout,
            headers={"User-Agent": "python-cartolafc/0.1.0"},
        )
        if token:
            self._client.headers["X-GLB-Token"] = token

    async def mercado_status(self) -> dict[str, Any]:
        resp = await self._client.get("/mercado/status")
        resp.raise_for_status()
        return resp.json()

    # Async context‑manager helpers ─────────────────────────────────
    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "CartolaAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        await self.aclose()
