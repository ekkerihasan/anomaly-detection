"""
Downloads a CPPP mirror SQLite dump with resume support and verifies its
SHA-256 against the checksum published on https://tender.sarthaksidhant.com/
before anything is allowed to read it.

Usage:
    python scripts/download_verify.py aoc_tenders
    python scripts/download_verify.py tenders_vps

Per CLAUDE.md: the mirror's SHA-256 must be verified before use. Checksums
below were pulled from the raw HTML of the source page (not summarized by
an LLM) on 2026-09-15.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

SOURCES = {
    "aoc_tenders": {
        "url": "https://mirror.s3.surf/aoc_tenders.db",
        "sha256": "ec8ef7711a17b7cae9e0414c2403b119a0a31c4dec49ed7055b38ec0df5f7586",
    },
    "tenders_vps": {
        "url": "https://mirror.s3.surf/tenders_vps.db",
        "sha256": "b1994cfb6dd2d5da9ed1d9ac8d6bbc7083178f155e92a65628e87a38e4c64d01",
    },
}

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


def download(name: str) -> Path:
    src = SOURCES[name]
    dest = RAW_DIR / f"{name}.db"
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # curl handles resume (-C -), redirects, and retries far more robustly
    # than a hand-rolled urllib loop for a multi-GB file over a flaky link.
    cmd = [
        "curl", "-L", "--fail", "--retry", "5", "--retry-delay", "5",
        "-A", USER_AGENT,
        "-C", "-",  # resume if dest already has bytes
        "-o", str(dest),
        src["url"],
    ]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError(f"curl exited {result.returncode} downloading {name}")
    return dest


def verify(name: str, path: Path) -> bool:
    expected = SOURCES[name]["sha256"]
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            buf = f.read(1024 * 1024 * 8)
            if not buf:
                break
            h.update(buf)
    actual = h.hexdigest()
    ok = actual == expected
    print(f"{name}: expected sha256={expected}")
    print(f"{name}: actual   sha256={actual}")
    print(f"{name}: {'MATCH' if ok else 'MISMATCH -- DO NOT USE THIS FILE'}")
    return ok


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in SOURCES:
        print(f"usage: python {sys.argv[0]} <{'|'.join(SOURCES)}>")
        sys.exit(1)
    name = sys.argv[1]
    path = download(name)
    ok = verify(name, path)
    marker = path.with_suffix(".verified" if ok else ".FAILED_VERIFICATION")
    marker.write_text(SOURCES[name]["sha256"])
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
