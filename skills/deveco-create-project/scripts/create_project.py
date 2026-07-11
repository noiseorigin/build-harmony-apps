#!/usr/bin/env python3
"""Create a minimal HarmonyOS Stage-model app from the bundled template."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any


REQUIRED = (
    "build-profile.json5",
    "oh-package.json5",
    "hvigor/hvigor-config.json5",
    "AppScope/app.json5",
    "entry/build-profile.json5",
    "entry/src/main/module.json5",
    "entry/src/main/ets/entryability/EntryAbility.ets",
    "entry/src/main/ets/pages/Index.ets",
    "entry/src/main/resources/base/profile/main_pages.json",
)


def roots() -> list[Path]:
    values: list[Path] = []
    for key in ("DEVECO_HOME", "DEVECO_STUDIO_HOME"):
        raw = os.environ.get(key)
        if raw:
            value = Path(raw).expanduser()
            values.append(value / "Contents" if value.suffix == ".app" else value)
    if sys.platform == "darwin":
        values.append(Path("/Applications/DevEco-Studio.app/Contents"))
    elif os.name == "nt":
        values.extend((Path(r"C:\Program Files\Huawei\DevEco Studio"), Path(r"C:\Program Files\DevEco Studio")))
    else:
        values.extend((Path.home() / "devecostudio/Contents", Path.home() / "DevEco-Studio/Contents"))
    return values


def installed_sdk() -> tuple[Path, dict[str, Any]]:
    for root in roots():
        path = root / "sdk/default/sdk-pkg.json"
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8")).get("data", {})
        except (OSError, json.JSONDecodeError):
            continue
        api = str(data.get("apiVersion", "")).strip()
        platform_version = str(data.get("platformVersion") or data.get("version") or "").strip()
        if api and platform_version:
            return path, data
    raise RuntimeError("DevEco default SDK metadata was not found; set DEVECO_HOME or install DevEco Studio")


def default_bundle(name: str) -> str:
    suffix = re.sub(r"[^a-z0-9]", "", name.lower())
    if not suffix:
        raise ValueError("app name does not contain characters usable in a bundle name")
    return f"com.example.{suffix}"


def validate_bundle(value: str) -> None:
    if len(value) > 127 or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+", value):
        raise ValueError("bundle name must be a dotted identifier such as com.example.myapp")


def replace_text(root: Path, replacements: dict[str, str]) -> None:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = content
        for source, target in replacements.items():
            updated = updated.replace(source, target)
        if updated != content:
            path.write_text(updated, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--bundle")
    parser.add_argument("--api-level", type=int)
    parser.add_argument("--compatible-sdk", help="Full compatible SDK value, otherwise target SDK is used")
    parser.add_argument("--force-empty", action="store_true")
    args = parser.parse_args()
    try:
        sdk_file, sdk = installed_sdk()
        detected_api = int(str(sdk["apiVersion"]))
        if args.api_level is not None and args.api_level != detected_api:
            raise ValueError(
                f"requested API {args.api_level} is not the installed default API {detected_api}; select/install that SDK in DevEco first"
            )
        name = args.name.strip()
        if not name or any(char in name for char in ("/", "\\", "\0")):
            raise ValueError("app name must be a non-empty directory-safe name")
        bundle = args.bundle.strip() if args.bundle else default_bundle(name)
        validate_bundle(bundle)
        parent = Path(args.parent).expanduser().resolve()
        destination = parent / name
        if destination.exists():
            if not destination.is_dir():
                raise ValueError(f"destination is not a directory: {destination}")
            if any(destination.iterdir()):
                raise ValueError(f"destination is not empty: {destination}")
            if not args.force_empty:
                raise ValueError("destination exists; pass --force-empty only after confirming it is empty")
        parent.mkdir(parents=True, exist_ok=True)
        template = Path(__file__).resolve().parent.parent / "assets/application"
        if not template.is_dir():
            raise RuntimeError(f"template not found: {template}")
        if destination.exists():
            shutil.copytree(template, destination, dirs_exist_ok=True)
        else:
            shutil.copytree(template, destination)
        platform_version = str(sdk.get("platformVersion") or sdk.get("version"))
        # DevEco/Hvigor uses the legacy platform(api) form through API 24.
        # API 26+ is a full MSF version and must be written without parentheses.
        target_sdk = platform_version if detected_api >= 26 else f"{platform_version}({detected_api})"
        compatible_sdk = args.compatible_sdk or target_sdk
        replace_text(
            destination,
            {
                "__APP_NAME__": name,
                "__BUNDLE_NAME__": bundle,
                "__TARGET_SDK__": target_sdk,
                "__COMPATIBLE_SDK__": compatible_sdk,
                "__MODEL_VERSION__": platform_version,
            },
        )
        missing = [item for item in REQUIRED if not (destination / item).is_file()]
        if missing:
            raise RuntimeError("template integrity failure: " + ", ".join(missing))
        result = {
            "projectRoot": str(destination),
            "appName": name,
            "bundleName": bundle,
            "apiLevel": detected_api,
            "targetSdkVersion": target_sdk,
            "compatibleSdkVersion": compatible_sdk,
            "modelVersion": platform_version,
            "sdkSource": str(sdk_file),
            "devecoSdkHome": str(sdk_file.parents[1]),
            "javaHome": str(sdk_file.parents[2] / "jbr/Contents/Home"),
            "sdkStage": sdk.get("stage") or sdk.get("releaseType"),
            "verified": True,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
