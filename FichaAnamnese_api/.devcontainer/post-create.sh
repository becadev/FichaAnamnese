#!/usr/bin/env bash
# Ajustes que só fazem sentido com o container já de pé.
set -euo pipefail

SOCKET=/var/run/docker.sock

# O GID do grupo dono do socket muda de máquina para máquina (nesta é 999), então
# não dá para fixá-lo no Dockerfile. Alinhar aqui é o que permite ao usuário
# falar com o daemon do host sem sudo. Vale a partir do próximo shell — os
# terminais do VS Code abrem depois deste script, então já pegam o grupo.
if [ -S "$SOCKET" ]; then
  sock_gid="$(stat -c '%g' "$SOCKET")"
  if ! getent group "$sock_gid" >/dev/null; then
    sudo groupadd --gid "$sock_gid" docker-host
  fi
  sudo usermod --append --groups "$sock_gid" "$(id -un)"
  echo "docker: daemon do host liberado para $(id -un) (GID $sock_gid)"
else
  echo "docker: $SOCKET nao esta montado — o CLI nao vai achar o daemon do host"
fi
