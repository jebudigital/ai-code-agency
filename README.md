# Autonomous Coding Agency — Full Package (Final)

This is the full package with implementations for:
- Planner, Coder (Ollama CLI + HTTP + cloud fallbacks), Reviewer (auto-approve support)
- Model hot-swapping helpers
- Quality gates for local vs cloud routing
- Monitoring blueprint + small static monitor UI
- GitHub Actions: pr-review.yml and auto-merge.yml
- Scripts to install, pull models, and package the project

See `.env.example` for configuration. Minimal commands to run on macOS (Apple Silicon)
are included at the top of this README.

---
Quickstart (minimal commands)

1. Create venv and install deps
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Copy .env.example -> .env and fill secrets (GH_PAT, GITHUB_REPO, etc.)

3. Start services (each in own terminal):
```bash
OLLAMA_NUM_GPU_LAYERS=99 ollama serve
redis-server
chroma run --path ./.chroma_data
python main.py
```

4. (Optional) ngrok http 5000 -> configure webhook to point to https://<ngrok-id>.ngrok.io/webhook

---
