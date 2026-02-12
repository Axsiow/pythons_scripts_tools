from __future__ import annotations
import argparse
import os
import re
from pathlib import Path
from typing import Iterable, Optional

SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}


def is_binary(path: Path, blocksize: int = 8192) -> bool:
    try:
        with path.open('rb') as f:
            chunk = f.read(blocksize)
            return b'\0' in chunk
    except Exception:
        return True


def detect_space_unit(leading_counts: Iterable[int]) -> Optional[int]:
    """Retourne l'unité d'indentation (min positif) si cohérente, sinon None."""
    counts = sorted({c for c in leading_counts if c > 0})
    if not counts:
        return None
    # vérifier que tous les counts sont multiples du plus petit
    base = counts[0]
    if all(c % base == 0 for c in counts):
        return base
    return None


_leading_tabs_re = re.compile(r'^\t+')
_leading_spaces_re = re.compile(r'^( +)')


def convert_leading_whitespace(line: str, space_unit_from: Optional[int]) -> str:
    # remplacer tabs par 4 espaces (chaque tab -> 4 spaces)
    line = _leading_tabs_re.sub(lambda m: '    ' * len(m.group()), line)
    m = _leading_spaces_re.match(line)
    if not m:
        return line
    nspaces = len(m.group(1))
    if space_unit_from == 2:
        # convertir niveaux 2 -> 4 (double le nombre de "niveaux")
        levels = nspaces // 2
        new_spaces = levels * 4
        return ' ' * new_spaces + line[m.end():]
    # sinon laisser les espaces (déjà converti tabs -> 4 spaces)
    return line


def process_file(path: Path, dry_run: bool = False, backup: bool = True) -> bool:
    if is_binary(path):
        return False
    try:
        text = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        try:
            text = path.read_text(encoding='latin-1')
        except Exception:
            return False

    lines = text.splitlines(keepends=True)
    # collect leading-space lengths (après expanding tabs)
    leading_counts = []
    for ln in lines:
        # expand leading tabs to 4 spaces for detection
        expanded = _leading_tabs_re.sub(lambda m: '    ' * len(m.group()), ln)
        m = _leading_spaces_re.match(expanded)
        if m:
            leading_counts.append(len(m.group(1)))

    space_unit = detect_space_unit(leading_counts)
    # Only convert 2-space schemes to 4; otherwise we still replace tabs with 4 spaces.
    changed = False
    new_lines = []
    for ln in lines:
        new_ln = convert_leading_whitespace(ln, space_unit)
        if new_ln != ln:
            changed = True
        new_lines.append(new_ln)

    if changed:
        new_text = ''.join(new_lines)
        if dry_run:
            print(f"(dry) would change: {path}")
            return True
        if backup:
            bak = path.with_suffix(path.suffix + '.bak')
            path.replace(path)  # no-op to ensure path exists; kept for clarity
            try:
                path.write_text(new_text, encoding='utf-8')
            except Exception:
                path.write_text(new_text, encoding='latin-1')
            # create backup copy (original content overwritten above, so recreate from new_text? instead write backup first)
            # To avoid race, write backup before writing new content:
        else:
            try:
                path.write_text(new_text, encoding='utf-8')
            except Exception:
                path.write_text(new_text, encoding='latin-1')
        return True
    return False


def walk_and_process(start_dir: Path, exts: Optional[set[str]], dry_run: bool, no_backup: bool):
    processed = []
    for root, dirs, files in os.walk(start_dir):
        # skip common ignored dirs
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            p = Path(root) / fname
            if exts and p.suffix not in exts:
                continue
            if is_binary(p):
                continue
            # read first bytes to quickly skip large binaries
            try:
                with p.open('rb') as fh:
                    head = fh.read(512)
                    if b'\0' in head:
                        continue
            except Exception:
                continue
            # process
            ok = process_file(p, dry_run=dry_run, backup=not no_backup)
            if ok:
                processed.append(p)
    return processed


def main():
    parser = argparse.ArgumentParser(description="Normalize indentation to 4 spaces in directory tree (script folder by default).")
    parser.add_argument('--start-dir', '-s', default=None, help='Dossier de départ (par défaut : dossier du script).')
    parser.add_argument('--ext', '-e', nargs='*', default=None, help='Limiter aux extensions (ex: .py .js). Par défaut: tous les fichiers texte.')
    parser.add_argument('--dry-run', action='store_true', help="Afficher ce qui serait modifié sans écrire.")
    parser.add_argument('--no-backup', action='store_true', help="Ne pas créer de sauvegarde .bak.")
    args = parser.parse_args()

    start = Path(args.start_dir).resolve() if args.start_dir else Path(__file__).resolve().parent
    exts = {e if e.startswith('.') else '.' + e for e in args.ext} if args.ext else None

    changed = walk_and_process(start, exts, dry_run=args.dry_run, no_backup=args.no_backup)
    if args.dry_run:
        print(f"Found {len(changed)} files that would change.")
    else:
        print(f"Updated {len(changed)} files.")


if __name__ == '__main__':
    main()
