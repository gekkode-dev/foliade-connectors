"""Serveur MCP local qui relie Codex et Claude Code à l'API Foliade."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations


SERVER = MCPServer(
    "Foliade", version="0.2.0",
    instructions=(
        "Create drafts by default with foliade_publish_pdf. Publish only when the user "
        "explicitly requests it. To publish an existing draft, use foliade_publish_catalogue "
        "with its id; never upload the PDF again. Only unpublish a catalogue on explicit "
        "request. Draft links require the owner to be logged in. Never disclose API keys."
    ),
)
TIMEOUT = httpx.Timeout(330.0, connect=20.0)


def _configuration() -> tuple[str, str]:
    key = os.environ.get("FOLIADE_API_KEY", "").strip()
    if not key:
        raise ToolError(
            "FOLIADE_API_KEY est absente. Créez une clé dans Foliade > API."
        )
    base_url = os.environ.get(
        "FOLIADE_BASE_URL", "https://foliade.gekkode.com"
    ).strip().rstrip("/")
    parsed = urlsplit(base_url)
    if parsed.scheme != "https" and parsed.hostname not in {
        "localhost", "127.0.0.1", "::1"
    }:
        raise ToolError("FOLIADE_BASE_URL doit utiliser HTTPS.")
    return base_url, key


def _request(method: str, path: str, **kwargs: Any) -> httpx.Response:
    base_url, key = _configuration()
    headers = dict(kwargs.pop("headers", {}))
    headers["Authorization"] = f"Bearer {key}"
    try:
        response = httpx.request(
            method, f"{base_url}{path}", headers=headers, timeout=TIMEOUT, **kwargs
        )
    except httpx.RequestError as exc:
        raise ToolError("Foliade est momentanément injoignable.") from exc
    if response.is_error:
        try:
            payload = response.json()
            message = payload.get("detail") or payload.get("message") or payload.get("erreur")
        except (ValueError, AttributeError):
            message = "requête refusée"
        message = str(message or "requête refusée").replace(key, "[clé masquée]")
        raise ToolError(f"Foliade a répondu {response.status_code}: {message}")
    return response


def _catalogue_id(value: str) -> str:
    public_id = value.strip()
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,32}", public_id):
        raise ToolError("catalogue_id doit être un identifiant Foliade, pas une URL.")
    return public_id


@SERVER.tool(
    name="foliade_list_catalogues",
    title="Lister les catalogues Foliade",
    annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False),
)
def list_catalogues() -> dict[str, Any]:
    """Liste les catalogues du compte Foliade associé à la clé API."""
    return _request("GET", "/v1/catalogs").json()


@SERVER.tool(
    name="foliade_publish_pdf",
    title="Convertir un PDF en catalogue Foliade",
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=False,
        open_world_hint=True,
    ),
)
def publish_pdf(
    pdf_path: str,
    title: str = "",
    language: str = "fr",
    publish: bool = False,
) -> dict[str, Any]:
    """Convertit un PDF local en brouillon ou en catalogue public Foliade."""
    source = Path(pdf_path).expanduser().resolve()
    if not source.is_file() or source.suffix.lower() != ".pdf":
        raise ToolError("pdf_path doit désigner un fichier PDF local existant.")
    try:
        pdf_file = source.open("rb")
    except OSError as exc:
        raise ToolError("pdf_path doit désigner un fichier PDF local lisible.") from exc
    with pdf_file as pdf:
        response = _request(
            "POST",
            "/v1/catalogs",
            files={"fichier": (source.name, pdf, "application/pdf")},
            data={
                "titre": title.strip(),
                "langue": language.strip().lower() or "fr",
                "publier": "1" if publish else "0",
                "attendre": "1",
            },
        )
    return response.json()


@SERVER.tool(
    name="foliade_publish_catalogue",
    title="Publier un catalogue Foliade existant",
    annotations=ToolAnnotations(
        read_only_hint=False, destructive_hint=False,
        idempotent_hint=True, open_world_hint=True,
    ),
)
def publish_catalogue(catalogue_id: str) -> dict[str, Any]:
    """Publie un brouillon existant sur demande explicite, en conservant son id et son lien."""
    return _request("POST", f"/v1/catalogs/{_catalogue_id(catalogue_id)}/publish").json()


@SERVER.tool(
    name="foliade_catalogue_stats",
    title="Lire les statistiques d'un catalogue Foliade",
    annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False),
)
def catalogue_stats(catalogue_id: str, days: int = 30) -> dict[str, Any]:
    """Retourne les statistiques de lecture d'un catalogue sur 7, 30 ou 90 jours."""
    period = days if days in {7, 30, 90} else 30
    return _request(
        "GET", f"/v1/catalogs/{_catalogue_id(catalogue_id)}/stats?days={period}"
    ).json()


@SERVER.tool(
    name="foliade_unpublish_catalogue",
    title="Dépublier un catalogue Foliade",
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=True,
        idempotent_hint=True,
        open_world_hint=True,
    ),
)
def unpublish_catalogue(catalogue_id: str) -> dict[str, Any]:
    """Ferme le lien public d'un catalogue sans effacer ses données du compte."""
    public_id = _catalogue_id(catalogue_id)
    _request("DELETE", f"/v1/catalogs/{public_id}")
    return {"id": public_id, "etat": "depublie"}


mcp = SERVER
