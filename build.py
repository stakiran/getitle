# -*- coding: utf-8 -*-
"""raw/*.json (Cosense exported json) からタイトルキャッシュと standalone html を生成する。

usage:
    python build.py

- raw/*.json をパースして cache/<name>.txt をつくる（1行1タイトル、エクスポート順）
- template.html の __DATA__ プレースホルダにキャッシュを埋め込み getitle_<name>.html を出力する
"""

import json
import time
from pathlib import Path

ROOT = Path(__file__).parent
RAW_DIR = ROOT / "raw"
CACHE_DIR = ROOT / "cache"
TEMPLATE = ROOT / "template.html"

PLACEHOLDER = "/*__DATA__*/"


def build_cache():
    CACHE_DIR.mkdir(exist_ok=True)
    projects = {}
    for jsonpath in sorted(RAW_DIR.glob("*.json")):
        start = time.perf_counter()
        with open(jsonpath, encoding="utf-8") as f:
            data = json.load(f)
        titles = [page["title"] for page in data["pages"]]
        elapsed = time.perf_counter() - start

        name = jsonpath.stem
        cachepath = CACHE_DIR / f"{name}.txt"
        with open(cachepath, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(titles) + "\n")

        projects[name] = titles
        size_mb = jsonpath.stat().st_size / 1024 / 1024
        print(f"{name}: {len(titles)} titles ({size_mb:.1f}MB, {elapsed:.2f}s)")
    return projects


def build_html(name, titles, template):
    # </script> でタグが閉じないよう </ をエスケープする
    payload = json.dumps(titles, ensure_ascii=False).replace("</", "<\\/")
    data_js = f'const PROJECT_NAME = {json.dumps(name)};\nconst TITLES = {payload};'
    html = template.replace(PLACEHOLDER, data_js)
    outpath = ROOT / f"getitle_{name}.html"
    outpath.write_text(html, encoding="utf-8", newline="\n")
    size_mb = outpath.stat().st_size / 1024 / 1024
    print(f"-> {outpath.name} ({size_mb:.1f}MB)")


def main():
    template = TEMPLATE.read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        raise RuntimeError(f"placeholder {PLACEHOLDER} not found in {TEMPLATE}")
    projects = build_cache()
    for name, titles in projects.items():
        build_html(name, titles, template)


if __name__ == "__main__":
    main()
