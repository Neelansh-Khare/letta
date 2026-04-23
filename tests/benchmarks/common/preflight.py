from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import httpx

from tests.benchmarks.common.utils import split_model_handle


@dataclass
class PreflightResult:
    ok: bool
    name: str
    message: str
    details: Optional[dict[str, Any]] = None


def check_model_handle(model_handle: str) -> PreflightResult:
    try:
        provider, model_name = split_model_handle(model_handle)
    except ValueError as exc:
        return PreflightResult(ok=False, name="model_handle", message=str(exc))

    return PreflightResult(
        ok=True,
        name="model_handle",
        message=f"Model handle is valid: provider='{provider}', model='{model_name}'",
        details={"provider": provider, "model": model_name},
    )


def check_server_health(base_url: str, timeout: float = 5.0) -> PreflightResult:
    health_url = f"{base_url.rstrip('/')}/v1/health/"
    try:
        response = httpx.get(health_url, follow_redirects=True, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        return PreflightResult(
            ok=False,
            name="server_health",
            message=f"Failed to reach Letta server at {health_url}: {exc}",
            details={"base_url": base_url},
        )

    return PreflightResult(
        ok=True,
        name="server_health",
        message=f"Letta server is reachable (status={payload.get('status')}, version={payload.get('version')})",
        details={"base_url": base_url, "payload": payload},
    )


def check_model_available(base_url: str, model_handle: str, timeout: float = 10.0) -> PreflightResult:
    models_url = f"{base_url.rstrip('/')}/v1/models/"
    try:
        response = httpx.get(models_url, follow_redirects=True, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        return PreflightResult(
            ok=False,
            name="model_available",
            message=f"Failed to query Letta models endpoint at {models_url}: {exc}",
            details={"base_url": base_url, "model": model_handle},
        )

    handles = {item.get("handle") for item in payload if isinstance(item, dict)}
    if model_handle not in handles:
        sample = sorted(handle for handle in handles if handle)[:10]
        return PreflightResult(
            ok=False,
            name="model_available",
            message=(f"Model '{model_handle}' was not found in Letta's available model list. " f"Sample available handles: {sample}"),
            details={"available_handles": sample, "model": model_handle},
        )

    return PreflightResult(
        ok=True,
        name="model_available",
        message=f"Model '{model_handle}' is available from the Letta server",
        details={"model": model_handle},
    )


def check_dataset_path(data_path: str, *, required: bool) -> PreflightResult:
    path = Path(data_path)
    if path.exists():
        return PreflightResult(
            ok=True,
            name="dataset_path",
            message=f"Dataset path exists: {path}",
            details={"data_path": str(path)},
        )

    if required:
        return PreflightResult(
            ok=False,
            name="dataset_path",
            message=f"Required dataset path does not exist: {path}",
            details={"data_path": str(path)},
        )

    return PreflightResult(
        ok=True,
        name="dataset_path",
        message=f"Dataset path not found, but this benchmark supports fallback behavior: {path}",
        details={"data_path": str(path), "fallback": True},
    )


def check_output_path(output_path: Optional[str]) -> PreflightResult:
    if not output_path:
        return PreflightResult(ok=True, name="output_path", message="No output path specified")

    output = Path(output_path)
    parent = output.parent
    if parent.exists():
        return PreflightResult(
            ok=True,
            name="output_path",
            message=f"Output directory is available: {parent}",
            details={"output_path": str(output)},
        )

    try:
        parent.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        return PreflightResult(
            ok=False,
            name="output_path",
            message=f"Failed to create output directory '{parent}': {exc}",
            details={"output_path": str(output)},
        )

    return PreflightResult(
        ok=True,
        name="output_path",
        message=f"Created output directory: {parent}",
        details={"output_path": str(output)},
    )


def run_benchmark_preflight(
    *,
    benchmark_name: str,
    base_url: str,
    model: str,
    data_path: str,
    output_path: Optional[str],
    require_dataset: bool,
) -> list[PreflightResult]:
    return [
        PreflightResult(ok=True, name="benchmark", message=f"Running preflight for {benchmark_name}"),
        check_model_handle(model),
        check_server_health(base_url),
        check_model_available(base_url, model),
        check_dataset_path(data_path, required=require_dataset),
        check_output_path(output_path),
    ]


def assert_preflight_ok(results: list[PreflightResult]) -> None:
    failures = [result for result in results if not result.ok]
    if failures:
        lines = ["Benchmark preflight failed:"]
        for result in failures:
            lines.append(f"- [{result.name}] {result.message}")
        raise RuntimeError("\n".join(lines))


def print_preflight_report(results: list[PreflightResult]) -> None:
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"[Preflight:{status}] {result.message}")
