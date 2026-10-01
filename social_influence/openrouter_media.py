"""Small OpenRouter media client for Creative Engine v2 experiments.

The project deliberately keeps this client provider-neutral: model IDs and
request parameters are configuration, while provenance is recorded for every
generation so a run can be audited or repeated.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import base64
import json
import mimetypes
import os
import time
from typing import Any, Callable, Iterable
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
RECORD_LOCK = Lock()


@dataclass
class GenerationRecord:
    """Auditable metadata for one OpenRouter generation attempt."""

    route: str
    model: str
    prompt: str
    request: dict[str, Any]
    input_references: list[dict[str, Any]]
    output_path: str | None
    output_sha256: str | None
    started_at: str
    completed_at: str | None
    elapsed_seconds: float
    job_id: str | None
    generation_id: str | None
    provider: str | None
    usage: dict[str, Any] | None
    attempts: list[dict[str, Any]]


class OpenRouterMediaError(RuntimeError):
    """Raised when OpenRouter returns an unusable or non-success response."""

    def __init__(self, message: str, *, status_code: int | None = None, body: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class OpenRouterMediaClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 900,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        if not self.api_key:
            raise OpenRouterMediaError("OPENROUTER_API_KEY must be set")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Title": "social-influence Creative Engine v2",
        }

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        *,
        raw: bool = False,
        timeout: int | None = None,
    ) -> Any:
        url = path if path.startswith("http") else f"{self.base_url}/{path.lstrip('/')}"
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(url, data=body, headers=self._headers(), method=method)
        try:
            with urlopen(request, timeout=timeout or self.timeout) as response:
                content = response.read()
                if raw:
                    return content
                text = content.decode("utf-8", errors="replace")
                try:
                    return json.loads(text)
                except json.JSONDecodeError as exc:
                    raise OpenRouterMediaError(
                        f"{method} {url} returned non-JSON success body",
                        status_code=getattr(response, "status", None),
                        body=text,
                    ) from exc
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                detail = json.loads(body).get("error", {}).get("message", body)
            except json.JSONDecodeError:
                detail = body or exc.reason
            raise OpenRouterMediaError(
                f"{method} {url} failed ({exc.code}): {detail}",
                status_code=exc.code,
                body=body,
            ) from exc
        except URLError as exc:
            raise OpenRouterMediaError(f"{method} {url} failed: {exc}") from exc

    def discover_image_models(self) -> dict[str, Any]:
        return self._request("GET", "/images/models")

    def discover_video_models(self) -> dict[str, Any]:
        return self._request("GET", "/videos/models")

    def image_model_endpoints(self, model: str) -> dict[str, Any]:
        return self._request("GET", f"/images/models/{model}/endpoints")

    @staticmethod
    def data_url(path: str | Path) -> str:
        path = Path(path)
        mime = mimetypes.guess_type(path.name)[0] or "image/png"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime};base64,{encoded}"

    @staticmethod
    def file_record(path: str | Path) -> dict[str, Any]:
        path = Path(path)
        return {
            "path": str(path),
            "sha256": sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size,
        }

    @classmethod
    def _redacted_request(
        cls, payload: dict[str, Any], reference_paths: Iterable[Path]
    ) -> dict[str, Any]:
        """Copy a request without persisting base64 image bytes in provenance."""
        copy = json.loads(json.dumps(payload))
        refs = [cls.file_record(path) for path in reference_paths]
        seen = 0

        def scrub(value: Any) -> None:
            nonlocal seen
            if isinstance(value, dict):
                if value.get("type") in {"image_url", "input_reference"} and "image_url" in value:
                    index = min(seen, max(0, len(refs) - 1))
                    value["image_url"] = {"url": f"sha256:{refs[index]['sha256']}"}
                    seen += 1
                for child in value.values():
                    scrub(child)
            elif isinstance(value, list):
                for child in value:
                    scrub(child)

        scrub(copy)
        return copy

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def generate_image(
        self,
        *,
        route: str,
        model: str,
        prompt: str,
        output_path: str | Path,
        input_references: Iterable[str | Path] = (),
        params: dict[str, Any] | None = None,
    ) -> GenerationRecord:
        """Generate one image and persist both bytes and an audit record."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        reference_paths = [Path(item) for item in input_references]
        payload: dict[str, Any] = {"model": model, "prompt": prompt}
        if reference_paths:
            payload["input_references"] = [
                {"type": "image_url", "image_url": {"url": self.data_url(path)}}
                for path in reference_paths
            ]
        payload.update(params or {})
        started = self._utc_now()
        before = time.monotonic()
        attempts: list[dict[str, Any]] = []
        response = self._request("POST", "/images", payload)
        elapsed = time.monotonic() - before
        attempts.append({"attempt": 1, "status": "completed", "response_keys": sorted(response)})
        images = response.get("data") or []
        if not images or not images[0].get("b64_json"):
            raise OpenRouterMediaError(f"image response for {model} contained no b64_json")
        output_path.write_bytes(base64.b64decode(images[0]["b64_json"]))
        record = GenerationRecord(
            route=route,
            model=model,
            prompt=prompt,
            request=self._redacted_request(payload, reference_paths),
            input_references=[self.file_record(path) for path in reference_paths],
            output_path=str(output_path),
            output_sha256=sha256(output_path.read_bytes()).hexdigest(),
            started_at=started,
            completed_at=self._utc_now(),
            elapsed_seconds=elapsed,
            job_id=None,
            generation_id=response.get("id"),
            provider=response.get("provider"),
            usage=response.get("usage"),
            attempts=attempts,
        )
        return record

    def chat_multimodal(
        self,
        *,
        route: str,
        model: str,
        prompt: str,
        input_references: Iterable[str | Path] = (),
        params: dict[str, Any] | None = None,
        output_path: str | Path | None = None,
    ) -> GenerationRecord:
        """Run multimodal creative/art-direction inference and retain its JSON."""
        reference_paths = [Path(item) for item in input_references]
        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        content.extend(
            {"type": "image_url", "image_url": {"url": self.data_url(path)}}
            for path in reference_paths
        )
        payload: dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": content}],
            "response_format": {"type": "json_object"},
        }
        payload.update(params or {})
        started = self._utc_now()
        before = time.monotonic()
        response = self._request("POST", "/chat/completions", payload)
        elapsed = time.monotonic() - before
        text = response["choices"][0]["message"].get("content", "")
        parsed = json.loads(text) if isinstance(text, str) else text
        output_path = Path(output_path or (route + ".json"))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(parsed, indent=2) + "\n")
        return GenerationRecord(
            route=route,
            model=model,
            prompt=prompt,
            request=self._redacted_request(payload, reference_paths),
            input_references=[self.file_record(path) for path in reference_paths],
            output_path=str(output_path),
            output_sha256=sha256(output_path.read_bytes()).hexdigest(),
            started_at=started,
            completed_at=self._utc_now(),
            elapsed_seconds=elapsed,
            job_id=None,
            generation_id=response.get("id"),
            provider=response.get("provider"),
            usage=response.get("usage"),
            attempts=[{"attempt": 1, "status": "completed", "response_keys": sorted(response)}],
        )

    def submit_video(
        self,
        *,
        route: str,
        model: str,
        prompt: str,
        output_path: str | Path,
        frame_images: Iterable[str | Path] = (),
        input_references: Iterable[str | Path] = (),
        params: dict[str, Any] | None = None,
        poll_seconds: int = 30,
        on_submit: Callable[[dict[str, Any]], None] | None = None,
    ) -> GenerationRecord:
        """Submit, poll and download one asynchronous OpenRouter video job."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        frames = [Path(item) for item in frame_images]
        refs = [Path(item) for item in input_references]
        payload: dict[str, Any] = {"model": model, "prompt": prompt}
        if frames:
            payload["frame_images"] = [
                {
                    "type": "image_url",
                    "image_url": {"url": self.data_url(path)},
                    "frame_type": "first_frame",
                }
                for path in frames
            ]
        if refs:
            payload["input_references"] = [
                {"type": "image_url", "image_url": {"url": self.data_url(path)}}
                for path in refs
            ]
        payload.update(params or {})
        started = self._utc_now()
        before = time.monotonic()
        attempts: list[dict[str, Any]] = []
        submitted = self._request("POST", "/videos", payload)
        job_id = submitted.get("id")
        polling_url = submitted.get("polling_url") or f"{self.base_url}/videos/{job_id}"
        if not job_id:
            raise OpenRouterMediaError(f"video response for {model} contained no job id")
        attempts.append({"attempt": 1, "status": "submitted", "job_id": job_id})
        if on_submit:
            on_submit(
                {
                    "route": route,
                    "model": model,
                    "job_id": job_id,
                    "polling_url": polling_url,
                    "submitted_at": started,
                    "request": self._redacted_request(payload, frames + refs),
                }
            )
        status = submitted.get("status", "pending")
        poll_count = 0
        while status not in {"completed", "failed", "cancelled", "expired"}:
            time.sleep(poll_seconds)
            poll_count += 1
            polled = self._request("GET", polling_url)
            status = polled.get("status", status)
            attempts.append({"attempt": poll_count + 1, "status": status, "job_id": job_id})
        if status != "completed":
            error = polled.get("error") if "polled" in locals() else submitted.get("error")
            raise OpenRouterMediaError(f"video job {job_id} ended {status}: {error}")
        content = self._request("GET", f"/videos/{job_id}/content?index=0", raw=True, timeout=self.timeout)
        output_path.write_bytes(content)
        final = polled if "polled" in locals() else submitted
        return GenerationRecord(
            route=route,
            model=model,
            prompt=prompt,
            request=self._redacted_request(payload, frames + refs),
            input_references=[self.file_record(path) for path in frames + refs],
            output_path=str(output_path),
            output_sha256=sha256(output_path.read_bytes()).hexdigest(),
            started_at=started,
            completed_at=self._utc_now(),
            elapsed_seconds=time.monotonic() - before,
            job_id=job_id,
            generation_id=final.get("generation_id"),
            provider=final.get("provider"),
            usage=final.get("usage"),
            attempts=attempts,
        )

    def complete_video_job(
        self,
        *,
        route: str,
        model: str,
        prompt: str,
        job_id: str,
        output_path: str | Path,
        request: dict[str, Any] | None = None,
        input_references: Iterable[str | Path] = (),
        poll_seconds: int = 30,
    ) -> GenerationRecord:
        """Resume a submitted video job from its persisted ID without re-billing."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        refs = [Path(item) for item in input_references]
        started = self._utc_now()
        before = time.monotonic()
        attempts = [{"attempt": 1, "status": "resumed", "job_id": job_id}]
        polling_url = f"{self.base_url}/videos/{job_id}"
        status = "pending"
        poll_count = 0
        while status not in {"completed", "failed", "cancelled", "expired"}:
            if poll_count:
                time.sleep(poll_seconds)
            polled = self._request("GET", polling_url)
            status = polled.get("status", status)
            poll_count += 1
            attempts.append({"attempt": poll_count + 1, "status": status, "job_id": job_id})
        if status != "completed":
            raise OpenRouterMediaError(f"video job {job_id} ended {status}: {polled.get('error')}")
        content = self._request("GET", f"/videos/{job_id}/content?index=0", raw=True, timeout=self.timeout)
        output_path.write_bytes(content)
        return GenerationRecord(
            route=route,
            model=model,
            prompt=prompt,
            request=request or {},
            input_references=[self.file_record(path) for path in refs],
            output_path=str(output_path),
            output_sha256=sha256(output_path.read_bytes()).hexdigest(),
            started_at=started,
            completed_at=self._utc_now(),
            elapsed_seconds=time.monotonic() - before,
            job_id=job_id,
            generation_id=polled.get("generation_id"),
            provider=polled.get("provider"),
            usage=polled.get("usage"),
            attempts=attempts,
        )


def write_records(records: Iterable[GenerationRecord], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with RECORD_LOCK:
        existing: list[dict[str, Any]] = []
        if path.exists():
            existing = json.loads(path.read_text())
        seen = {
            (item.get("route"), item.get("output_path"), item.get("started_at"))
            for item in existing
        }
        for record in records:
            item = asdict(record)
            key = (item["route"], item["output_path"], item["started_at"])
            if key not in seen:
                existing.append(item)
                seen.add(key)
        temp = path.with_suffix(path.suffix + ".tmp")
        temp.write_text(json.dumps(existing, indent=2) + "\n")
        os.replace(temp, path)


def load_records(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise OpenRouterMediaError(f"invalid provenance ledger: {path}", body=path.read_text()) from exc
