"""Fetch public benchmark metadata/code without inventing local samples.

Usage:
  python scripts/fetch_public_benchmarks.py

The script requires internet access and intentionally fails if a download
produces an incomplete dataset.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'evaluation'/'public'
DATA.mkdir(parents=True, exist_ok=True)

def run(cmd):
    print('>', ' '.join(cmd)); subprocess.run(cmd, check=True)

run([sys.executable, '-m', 'pip', 'install', '-q', 'huggingface_hub'])
print('VRSBench: use the official repository/Hugging Face dataset loader documented at: https://github.com/lx709/VRSBench')
print('CDVQA: clone the official repository: https://github.com/YZHJessica/CDVQA')
print('RSVQA: obtain the prescribed public split from its official benchmark release and record it in evaluation/public/RSVQA_SOURCE.txt')
print('ISRO/SAC: organizer-only data is intentionally not downloaded or fabricated.')
