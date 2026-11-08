#!/usr/bin/env python3
"""Copy one real generated PNG into this project and write a provenance sidecar.

This tool never generates, repaints, keys, resizes, crops, or changes image pixels.
Request/response JSON and the prompt must already exist as actual call evidence.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys

from PIL import Image


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def project_path(root: Path, value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def portable_path(root: Path, path: Path) -> str:
    try:
        return Path(os.path.relpath(path.resolve(), root.resolve())).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def safe_kind(value: str) -> str:
    path = Path(value.replace("\\", "/"))
    if path.is_absolute() or path.drive or ".." in path.parts or not path.parts:
        raise argparse.ArgumentTypeError("kind must be a project-relative subdirectory")
    return path.as_posix()


def finalize(args: argparse.Namespace) -> dict:
    root = args.root.resolve()
    if not (root / "AGENTS.md").is_file():
        raise ValueError(f"No project AGENTS.md at {root}")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.stem):
        raise ValueError("stem must contain letters, digits, dots, underscores or hyphens")
    request_path = project_path(root, args.request)
    response_path = project_path(root, args.response)
    source_path = project_path(root, args.source)
    request = read_json(request_path)
    response = read_json(response_path)
    submitted = request.get("submittedParameters", request.get("parameters"))
    if not isinstance(submitted, dict):
        raise ValueError("Request must contain submittedParameters or parameters")
    prompt_value = args.prompt or submitted.get("promptFile") or request.get("promptFile")
    if not prompt_value:
        prompt_value = f"prompts/{args.game}/{args.stem}.prompt.txt"
    prompt_path = project_path(root, prompt_value)
    if not prompt_path.is_file():
        raise ValueError(f"Actual prompt file does not exist: {prompt_path}")
    prompt = prompt_path.read_text(encoding="utf-8-sig").strip()
    actual_prompt = submitted.get("prompt")
    if isinstance(actual_prompt, str) and prompt != actual_prompt.strip():
        raise ValueError("Prompt file does not match the exact submitted prompt")

    output = root / "designs" / args.game / args.kind / f"{args.stem}.png"
    output = output.resolve()
    if not output.is_relative_to(root):
        raise ValueError("Output must stay inside the project root")
    record_path = output.with_suffix(".png.generation.json")
    if output.exists() or record_path.exists():
        raise FileExistsError(f"Refusing to overwrite output or sidecar: {output}")
    with Image.open(source_path) as image:
        image.verify()
    with Image.open(source_path) as image:
        if image.format != "PNG":
            raise ValueError("Source must be a native PNG; no implicit conversion is allowed")
        width, height = image.size
        mode = image.mode
        metadata_keys = list(image.info)
        alpha = None
        if "A" in image.getbands():
            channel = image.getchannel("A")
            histogram = channel.histogram()
            alpha = {
                "range": list(channel.getextrema()),
                "fullyTransparentPixelCount": histogram[0],
                "semiTransparentPixelCount": sum(histogram[1:255]),
                "opaquePixelCount": histogram[255],
                "canvasCornerAlpha": [
                    channel.getpixel((0, 0)), channel.getpixel((width - 1, 0)),
                    channel.getpixel((0, height - 1)), channel.getpixel((width - 1, height - 1)),
                ],
            }
    if submitted.get("transparent_background") is True:
        if alpha is None or alpha["fullyTransparentPixelCount"] == 0:
            raise ValueError("Transparent output requested, but source has no verified transparent pixels")

    reference_values = submitted.get("referenced_image_paths", [])
    if not isinstance(reference_values, list):
        raise ValueError("referenced_image_paths must be an array when present")
    references = []
    for index, value in enumerate(reference_values):
        path = project_path(root, value)
        if not path.is_file():
            raise ValueError(f"Reference does not exist: {path}")
        role = args.reference_role[index] if index < len(args.reference_role) else (
            "首要已确认邮件/组队风格主参考" if index < 2 else "实际附图参考；具体用途见本次提示词"
        )
        item = {
            "file": portable_path(root, path),
            "sha256": sha256(path),
            "role": role,
            "actuallyAttached": True,
        }
        previous_record = path.with_suffix(path.suffix + ".generation.json")
        if previous_record.is_file():
            item["generationRecord"] = portable_path(root, previous_record)
        references.append(item)

    completed_at = response.get("callCompletedAt") or response.get("completedAt")
    if not completed_at:
        raise ValueError("Response must contain an observed callCompletedAt or completedAt")
    digest = sha256(source_path)
    configured = request.get("configSnapshot")
    snapshot_basis = "actual_request_config_snapshot"
    if not isinstance(configured, dict):
        configured = read_json(root / "config/image-generation.json")
        snapshot_basis = "project_config_read_at_finalization; request did not include configSnapshot"
    record = {
        "schemaVersion": 1,
        "file": portable_path(root, output),
        "sha256": digest,
        "generatedAt": completed_at,
        "generatedAtBasis": "Observed host call completion time; no separate internal generation time disclosed",
        "callStartedAt": response.get("callStartedAt") or request.get("startedAt"),
        "width": width, "height": height, "format": "PNG", "mode": mode,
        "nativeDimensionsPreserved": True, "resampled": False,
        "art_source": "host_image",
        "tool": request.get("tool", "image_gen.imagegen"), "route": "builtin",
        "resultId": response.get("resultId"),
        "executionCellId": response.get("executionCellId", request.get("executionCellId")),
        "configSnapshot": configured, "configSnapshotBasis": snapshot_basis,
        "submittedParameters": {
            "model": submitted.get("model"), "quality": submitted.get("quality"),
            "transparent_background": submitted.get("transparent_background", False),
            "referenced_image_paths": reference_values,
            "num_last_images_to_include": submitted.get("num_last_images_to_include"),
            "promptFile": portable_path(root, prompt_path),
        },
        "actualModel": response.get("actualModel"),
        "actualQuality": response.get("actualQuality"),
        "unverifiedReason": response.get("unverifiedReason") or (
            "宿主管理；内置工具未披露实际模型/画质。配置目标和提示词不等同实际返回证据。"
        ),
        "evidence": [
            {"file": portable_path(root, request_path), "field": "submittedParameters"},
            {"file": portable_path(root, response_path),
             "fields": ["returnedFields", "output_hint", "callStartedAt", "callCompletedAt"]},
            {"sourceImage": source_path.as_posix(), "sha256": digest, "copyHashVerified": True},
        ],
        "prompt": portable_path(root, prompt_path),
        "references": references, "pngMetadataKeys": metadata_keys,
        "alphaInspection": alpha, "assetRole": args.role or args.stem,
        "status": "draft_pending_user_review", "userApproved": False, "clientIntegrated": False,
        "finalizedAt": datetime.now(timezone.utc).isoformat(),
    }
    summary = {
        "file": record["file"], "record": portable_path(root, record_path),
        "width": width, "height": height, "mode": mode, "sha256": digest,
        "referenceCount": len(references), "alpha": alpha,
        "dryRun": args.dry_run, "actualModel": record["actualModel"],
        "actualQuality": record["actualQuality"],
    }
    if args.dry_run:
        return summary
    output.parent.mkdir(parents=True, exist_ok=True)
    with source_path.open("rb") as incoming, output.open("xb") as destination:
        shutil.copyfileobj(incoming, destination)
    if sha256(output) != digest:
        raise ValueError(f"Copied image hash mismatch: {output}")
    with record_path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--game", default="01-率土之滨")
    parser.add_argument("--stem", required=True)
    parser.add_argument("--kind", required=True, type=safe_kind,
                        help="e.g. ui, characters, assets/runtime-ui")
    parser.add_argument("--source", required=True, help="Real generated native PNG")
    parser.add_argument("--request", required=True, help="Actual request JSON evidence")
    parser.add_argument("--response", required=True, help="Actual response receipt JSON")
    parser.add_argument("--prompt", help="Actual prompt file; defaults to prompts/game/stem.prompt.txt")
    parser.add_argument("--role", help="Human-readable asset purpose")
    parser.add_argument("--reference-role", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true", help="Validate without copying or writing")
    args = parser.parse_args()
    try:
        print(json.dumps(finalize(args), ensure_ascii=False))
        return 0
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())

