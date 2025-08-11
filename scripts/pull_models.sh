#!/usr/bin/env bash
ollama pull phi:2.7b || true
ollama pull codellama:7b-code-q4_K_M || true
ollama pull phind-codellama:34b-v2-q4_K_M || true
