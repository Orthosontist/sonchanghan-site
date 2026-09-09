#!/usr/bin/env bash
set -euo pipefail
python3 -m pip install -r scripts/requirements.txt
python3 scripts/rebuild_site.py
