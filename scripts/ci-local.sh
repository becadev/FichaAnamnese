#!/usr/bin/env bash
# Reproduz localmente os jobs do .github/workflows/ci.yml.
# Uso: ./scripts/ci-local.sh [testes|lint|duplicacao|imagem]
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
  executar lint bash -c "cd '$RAIZ' && '$PY' -m ruff format --check && '$PY' -m ruff check"
fi

if [[ "$ALVO" == "tudo" || "$ALVO" == "duplicacao" ]]; then
  # Arquivos listados um a um: o Pylint não entra em pastas sem __init__.py (ex.: app/modules).
  # --cached --others inclui arquivos novos ainda não commitados.
  executar duplicacao bash -c "cd '$RAIZ' && '$PY' -m pylint \$(git ls-files --cached --others --exclude-standard 'FichaAnamnese_api/app/*.py' 'FichaAnamnese_api/tests/*.py')"
fi

# No CI, o job imagem tem `needs: [testes, lint, duplicacao]`: só roda se os dois passaram.
if [[ "$ALVO" == "tudo" && ${#FALHAS[@]} -gt 0 ]]; then
  echo ""
  echo "===> imagem"
  echo "PULADO (depende de: ${FALHAS[*]})"
elif [[ "$ALVO" == "tudo" || "$ALVO" == "imagem" ]]; then
  executar imagem bash -c "cd '$API' && docker build -t ficha-anamnese-api:local ."
fi

echo ""
if (( ${#FALHAS[@]} )); then
  echo "Jobs com falha: ${FALHAS[*]}"
  exit 1
fi
echo "Todos os jobs passaram."
