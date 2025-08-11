#!/usr/bin/env bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install pre-commit || true
pre-commit install || true
echo "Dev env ready. Activate with: source venv/bin/activate"
