"""Rebuild portable source indexes after cloning or updating course knowledge."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from beru.knowledge import index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud', action='store_true', help='Build Gemini embeddings using the local API.env key; sends source passages to Google.')
    args = parser.parse_args()
    (ROOT/'knowledge').mkdir(exist_ok=True)
    count = index()
    print(f'Indexed {count} source passages.', flush=True)
    if not count:
        raise SystemExit('No knowledge passages found. Check that knowledge source files were pulled.')
    if args.cloud:
        subprocess.run([sys.executable, str(ROOT/'scripts/build_cloud_index.py')], cwd=ROOT, check=True)
    else:
        print('Keyword retrieval ready. Use --cloud for stronger multilingual retrieval.')
    print('Restart Beru to load the updated knowledge.')


if __name__ == '__main__':
    main()
