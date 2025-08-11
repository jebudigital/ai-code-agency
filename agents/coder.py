import os, subprocess, shutil, requests, json, tempfile
OLLAMA_CLI = shutil.which('ollama')
OLLAMA_HOST = os.environ.get('OLLAMA_HOST','http://localhost:11434')
OPENROUTER_KEY = os.environ.get('OPENROUTER_API_KEY','')
GROQ_KEY = os.environ.get('GROQ_API_KEY','')
FIREWORKS_KEY = os.environ.get('FIREWORKS_API_KEY','')

class CoderAgent:
    def __init__(self, model=None):
        self.model = model or os.environ.get('OLLAMA_MODEL','phi:2.7b')

    def generate_code(self, prompt: str, max_tokens=512):
        # 1) Try Ollama CLI
        if OLLAMA_CLI:
            try:
                p = subprocess.run([OLLAMA_CLI, 'run', self.model, '--', prompt], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
                if p.returncode == 0 and p.stdout.strip():
                    return p.stdout
            except Exception:
                pass
        # 2) Try Ollama HTTP API
        try:
            resp = requests.post(f"{OLLAMA_HOST}/api/generate", json={'model': self.model, 'input': prompt, 'max_tokens': max_tokens}, timeout=10)
            if resp.ok:
                data = resp.json()
                if isinstance(data, dict) and 'text' in data:
                    return data['text']
                if isinstance(data, dict) and 'result' in data:
                    return data['result'].get('output','') or json.dumps(data)
                return str(data)
        except Exception:
            pass
        # 3) Cloud fallbacks (OpenRouter/Groq/Fireworks) - naive wrapping
        if OPENROUTER_KEY:
            try:
                rr = requests.post('https://api.openrouter.ai/v1/generate', headers={'Authorization': f'Bearer {OPENROUTER_KEY}'}, json={'model':self.model,'prompt':prompt}, timeout=10)
                if rr.ok:
                    return rr.text
            except Exception:
                pass
        # GROQ and FIREWORKS placeholders
        if GROQ_KEY:
            pass
        if FIREWORKS_KEY:
            pass
        # Fallback to template
        return f"# Placeholder code for: {prompt[:80]}\nprint('placeholder from CoderAgent')\n"
