#!/usr/bin/env python3
"""Generate a unified diff patch and an HTML report for two code directories."""

from __future__ import annotations

import argparse
import difflib
import html
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class DiffLine:
    kind: str
    old_no: int | None
    new_no: int | None
    text: str


@dataclass
class FileDiff:
    rel_path: str
    status: str
    rows: list[DiffLine]
    patch: str
    added: int
    deleted: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare two directories and generate diff.patch plus report.html"
    )
    parser.add_argument("--left", required=True, help="left/base directory")
    parser.add_argument("--right", required=True, help="right/target directory")
    parser.add_argument("--left-name", default="left", help="label shown in report")
    parser.add_argument("--right-name", default="right", help="label shown in report")
    parser.add_argument("--ext", action="append", default=[".v"], help="file extension to include")
    parser.add_argument("--out", default="diff-report", help="output directory")
    parser.add_argument("--context", type=int, default=3, help="context lines in diff")
    return parser.parse_args()


def normalize_exts(raw_exts: list[str]) -> tuple[str, ...]:
    cleaned: list[str] = []
    for ext in raw_exts:
        ext = ext.strip()
        if not ext:
            continue
        cleaned.append(ext if ext.startswith(".") else f".{ext}")
    return tuple(dict.fromkeys(cleaned)) or (".v",)


def read_text(path: Path) -> list[str]:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gbk", "latin-1"):
        try:
            return data.decode(encoding).splitlines(keepends=True)
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1", errors="replace").splitlines(keepends=True)


def collect_files(root: Path, exts: tuple[str, ...]) -> dict[str, Path]:
    files: dict[str, Path] = {}
    if not root.exists():
        return files
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in exts:
            files[path.relative_to(root).as_posix()] = path
    return files


def build_rows(old_lines: list[str], new_lines: list[str]) -> list[DiffLine]:
    matcher = difflib.SequenceMatcher(a=old_lines, b=new_lines)
    rows: list[DiffLine] = []
    old_no = 1
    new_no = 1
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for offset in range(i2 - i1):
                rows.append(DiffLine("context", old_no, new_no, old_lines[i1 + offset]))
                old_no += 1
                new_no += 1
        elif tag == "delete":
            for line in old_lines[i1:i2]:
                rows.append(DiffLine("delete", old_no, None, line))
                old_no += 1
        elif tag == "insert":
            for line in new_lines[j1:j2]:
                rows.append(DiffLine("insert", None, new_no, line))
                new_no += 1
        elif tag == "replace":
            for line in old_lines[i1:i2]:
                rows.append(DiffLine("delete", old_no, None, line))
                old_no += 1
            for line in new_lines[j1:j2]:
                rows.append(DiffLine("insert", None, new_no, line))
                new_no += 1
    return rows


def make_patch(old_lines: list[str], new_lines: list[str], rel_path: str, context: int) -> str:
    return "".join(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{rel_path}",
            tofile=f"b/{rel_path}",
            lineterm="\n",
            n=context,
        )
    )


def row_visible(rows: list[DiffLine], index: int, context: int) -> bool:
    if rows[index].kind != "context":
        return True
    start = max(0, index - context)
    end = min(len(rows), index + context + 1)
    return any(row.kind != "context" for row in rows[start:end])


def render_rows(rows: list[DiffLine], context: int) -> str:
    parts: list[str] = []
    skipped = False
    for index, row in enumerate(rows):
        if row.kind == "context" and not row_visible(rows, index, context):
            if not skipped:
                parts.append('<tr class="skip"><td class="ln"></td><td class="ln"></td><td class="code">...</td></tr>')
                skipped = True
            continue
        skipped = False
        marker = {"context": " ", "insert": "+", "delete": "-"}[row.kind]
        old_no = "" if row.old_no is None else str(row.old_no)
        new_no = "" if row.new_no is None else str(row.new_no)
        text = html.escape(row.text.rstrip("\r\n"))
        parts.append(
            f'<tr class="{row.kind}"><td class="ln">{old_no}</td><td class="ln">{new_no}</td>'
            f'<td class="code"><span class="marker">{marker}</span>{text}</td></tr>'
        )
    return "\n".join(parts)


def build_diffs(left_root: Path, right_root: Path, exts: tuple[str, ...], context: int) -> list[FileDiff]:
    left_files = collect_files(left_root, exts)
    right_files = collect_files(right_root, exts)
    rel_paths = sorted(set(left_files) | set(right_files))
    diffs: list[FileDiff] = []
    for rel_path in rel_paths:
        left_path = left_files.get(rel_path)
        right_path = right_files.get(rel_path)
        old_lines = read_text(left_path) if left_path else []
        new_lines = read_text(right_path) if right_path else []
        if left_path and not right_path:
            status = "deleted"
        elif right_path and not left_path:
            status = "added"
        elif old_lines == new_lines:
            status = "unchanged"
        else:
            status = "modified"

        rows = build_rows(old_lines, new_lines)
        patch = "" if status == "unchanged" else make_patch(old_lines, new_lines, rel_path, context)
        added = sum(1 for row in rows if row.kind == "insert")
        deleted = sum(1 for row in rows if row.kind == "delete")
        diffs.append(FileDiff(rel_path, status, rows, patch, added, deleted))
    return diffs


def render_html(
    diffs: list[FileDiff],
    out_dir: Path,
    context: int,
    left_name: str,
    right_name: str,
    left_dir: Path,
    right_dir: Path,
) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    changed_count = sum(1 for item in diffs if item.status != "unchanged")
    total_added = sum(item.added for item in diffs)
    total_deleted = sum(item.deleted for item in diffs)
    file_items = "\n".join(
        f'''
<details class="file" id="file-{index}">
  <summary>
    <span class="file-title"><span class="status {html.escape(item.status)}">{html.escape(item.status)}</span>
    <strong class="path">{html.escape(item.rel_path)}</strong></span>
    <span class="numbers">+{item.added} -{item.deleted}</span>
  </summary>
  <table>
    <colgroup><col class="line-col"><col class="line-col"><col></colgroup>
    <tbody>{render_rows(item.rows, context)}</tbody>
  </table>
</details>
'''
        for index, item in enumerate(diffs)
    )

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Verilog Diff Report</title>
  <style>
    :root {{
      --border: #d0d7de;
      --text: #1f2328;
      --muted: #656d76;
      --bg: #f6f8fa;
      --add-bg: #dafbe1;
      --add-line: #aceebb;
      --del-bg: #ffebe9;
      --del-line: #ffcecb;
      --code-bg: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--text); font: 14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 24px; }}
    h1 {{ margin: 0 0 8px; font-size: 26px; }}
    h2 {{ margin: 0 0 12px; font-size: 18px; }}
    .meta, .numbers {{ color: var(--muted); }}
    .overview, .files {{ background: #fff; border: 1px solid var(--border); border-radius: 8px; margin-top: 16px; }}
    .overview {{ padding: 16px 18px; }}
    .overview ul {{ margin: 8px 0 0; padding-left: 22px; }}
    .stats {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }}
    .stats span {{ border: 1px solid var(--border); border-radius: 999px; padding: 4px 10px; background: #fff; }}
    .file {{ border-top: 1px solid var(--border); overflow: hidden; }}
    .file:first-child {{ border-top: 0; }}
    .file summary {{ display: flex; gap: 10px; align-items: center; padding: 10px 14px; cursor: pointer; font-family: ui-monospace,SFMono-Regular,Consolas,monospace; list-style: none; }}
    .file summary::-webkit-details-marker {{ display: none; }}
    .file summary::before {{ content: "+"; flex: 0 0 16px; color: var(--muted); font-weight: 600; text-align: center; }}
    .file[open] summary {{ border-bottom: 1px solid var(--border); background: #f6f8fa; }}
    .file[open] summary::before {{ content: "-"; }}
    .file-title {{ display: flex; gap: 10px; align-items: center; min-width: 0; }}
    .path {{ overflow-wrap: anywhere; }}
    .file summary .numbers {{ margin-left: auto; white-space: nowrap; }}
    .status {{ display: inline-block; min-width: 68px; border-radius: 999px; padding: 2px 8px; text-align: center; color: #fff; font: 12px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    .status.modified {{ background: #8250df; }}
    .status.added {{ background: #1a7f37; }}
    .status.deleted {{ background: #cf222e; }}
    .status.unchanged {{ background: #57606a; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--code-bg); table-layout: fixed; }}
    col.line-col {{ width: 56px; }}
    td {{ padding: 0; vertical-align: top; font-family: ui-monospace,SFMono-Regular,Consolas,monospace; font-size: 12px; line-height: 20px; white-space: pre-wrap; overflow-wrap: anywhere; }}
    .ln {{ width: 56px; color: var(--muted); text-align: right; padding: 0 10px; border-right: 1px solid var(--border); user-select: none; }}
    .code {{ padding-left: 10px; }}
    .marker {{ display: inline-block; width: 18px; color: var(--muted); }}
    tr.insert td {{ background: var(--add-bg); }}
    tr.insert .ln {{ background: var(--add-line); }}
    tr.delete td {{ background: var(--del-bg); }}
    tr.delete .ln {{ background: var(--del-line); }}
    tr.skip td {{ background: #f6f8fa; color: var(--muted); }}
  </style>
</head>
<body>
  <main>
    <h1>Verilog Diff Report</h1>
    <div class="meta">Generated at {html.escape(generated_at)}. Patch file: {html.escape(str(out_dir / "diff.patch"))}</div>
    <section class="overview">
      <h2>Comparison</h2>
      <ul>
        <li><strong>{html.escape(left_name)}</strong>: {html.escape(str(left_dir))}</li>
        <li><strong>{html.escape(right_name)}</strong>: {html.escape(str(right_dir))}</li>
      </ul>
      <div class="stats">
        <span>{changed_count} changed files</span>
        <span>+{total_added} additions</span>
        <span>-{total_deleted} deletions</span>
      </div>
    </section>
    <section class="files">{file_items}</section>
  </main>
</body>
</html>
'''


def main() -> int:
    args = parse_args()
    left_dir = Path(args.left).resolve()
    right_dir = Path(args.right).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    exts = normalize_exts(args.ext)
    diffs = build_diffs(left_dir, right_dir, exts, args.context)

    patch_text = "\n".join(item.patch for item in diffs if item.patch)
    patch_path = out_dir / "diff.patch"
    patch_path.write_text(patch_text, encoding="utf-8", newline="\n")

    html_text = render_html(diffs, out_dir, args.context, args.left_name, args.right_name, left_dir, right_dir)
    html_path = out_dir / "report.html"
    html_path.write_text(html_text, encoding="utf-8", newline="\n")

    changed_count = sum(1 for item in diffs if item.status != "unchanged")
    print(f"Compared extensions: {', '.join(exts)}")
    print(f"Changed files: {changed_count}")
    print(f"Wrote {patch_path}")
    print(f"Wrote {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
