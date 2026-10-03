#!/usr/bin/env bash
# Reproduz localmente os jobs do .github/workflows/ci.yml.
# Uso: ./scripts/ci-local.sh [testes|lint|imagem]
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API="$RAIZ/FichaAnamnese_api"
PY="${PY:-$RAIZ/.venv/bin/python}"
ALVO="${1:-tudo}"
FALHAS=()

executar() {
  local nome="$1"
  shift
  echo ""
  echo "===> $nome"
  if "$@"; then
    echo "OK"
  else
    echo "FALHOU"
    FALHAS+=("$nome")
  fi
}

if [[ "$ALVO" == "tudo" || "$ALVO" == "testes" ]]; then
  executar testes bash -c "cd '$API' && '$PY' -m pytest -q"
fi

if [[ "$ALVO" == "tudo" || "$ALVO" == "lint" ]]; then
  # A ruff-action roda na raiz do repositório, não dentro da API.
  executar lint bash -c "cd '$RAIZ' && '$PY' -m ruff check"
fi

if [[ "$ALVO" == "tudo" || "$ALVO" == "imagem" ]]; then
  executar imagem bash -c "cd '$API' && docker build -t ficha-anamnese-api:local ."
fi

echo ""
if (( ${#FALHAS[@]} )); then
  echo "Jobs com falha: ${FALHAS[*]}"
  exit 1
fi
echo "Todos os jobs passaram."
