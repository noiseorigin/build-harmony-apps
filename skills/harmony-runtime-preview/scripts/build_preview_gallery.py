#!/usr/bin/env python3
"""Create a dependency-free HTML gallery for HarmonyOS proof screenshots."""

from __future__ import annotations

import argparse
import html
import os
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("images", nargs="+")
    parser.add_argument("--output", required=True)
    parser.add_argument("--title", default="HarmonyOS preview proof")
    args = parser.parse_args()

    images = [Path(item).expanduser().resolve() for item in args.images]
    missing = [str(path) for path in images if not path.is_file()]
    if missing:
        parser.error("missing image(s): " + ", ".join(missing))

    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    cards = []
    for path in images:
        relative = os.path.relpath(path, output.parent)
        cards.append(
            '<figure><img loading="lazy" src="{}" alt="{}"><figcaption>{}</figcaption></figure>'.format(
                html.escape(Path(relative).as_posix(), quote=True),
                html.escape(path.stem, quote=True),
                html.escape(path.name),
            )
        )
    document = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>
:root{{color-scheme:light dark;font-family:system-ui,sans-serif}}body{{margin:0;padding:24px;background:#0b1020;color:#f5f7ff}}
h1{{font-size:24px}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px}}
figure{{margin:0;padding:12px;border:1px solid #536184;border-radius:16px;background:#151d33}}
img{{width:100%;height:auto;display:block;border-radius:10px;background:#000}}figcaption{{padding-top:10px;overflow-wrap:anywhere}}
</style></head><body><h1>{title}</h1><main>{cards}</main></body></html>
""".format(title=html.escape(args.title), cards="".join(cards))
    output.write_text(document, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
