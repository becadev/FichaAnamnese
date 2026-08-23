# Imagem de DEV do Dev Container.
#
# Por que existe: as features OCI (ghcr.io/devcontainers/*) baixam um tarball do
# GHCR a cada rebuild, e essa rede vem cortando com ECONNRESET no meio do
# download — qualquer soluço derruba o build inteiro, sem retry. Aqui a mesma
# ferramentaria vem de repositórios apt, que respondem de forma estável.
#
# Usa a MESMA base do ../Dockerfile de produção para os dois não divergirem.
FROM python:3.11-slim

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

# UID/GID do dono do bind mount `.:/workspace`. Se a máquina usar outros
# valores, o VS Code reajusta em runtime (updateRemoteUserUID, ligado por padrão).
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000

# Acompanha o `postgres:16-alpine` do compose: cliente e servidor na mesma major
# evita a recusa do pg_dump ao falar com um servidor mais novo que ele.
ARG PG_MAJOR=16

# --------------------------------------------------------------------------
# 1. Base — o que a feature common-utils entregava.
#    python:3.11-slim roda como root e não traz git nem sudo.
# --------------------------------------------------------------------------
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      git \
      openssh-client \
      sudo \
      zsh \
      less \
      procps \
 && rm -rf /var/lib/apt/lists/*

# Usuário não-root com sudo sem senha (o remoteUser do devcontainer.json).
RUN groupadd --gid "${USER_GID}" "${USERNAME}" \
 && useradd --uid "${USER_UID}" --gid "${USER_GID}" --create-home --shell /bin/bash "${USERNAME}" \
 && echo "${USERNAME} ALL=(root) NOPASSWD:ALL" > "/etc/sudoers.d/${USERNAME}" \
 && chmod 0440 "/etc/sudoers.d/${USERNAME}"

# --------------------------------------------------------------------------
# 2. psql — o cliente que a imagem da API não tem, para falar com o `db`.
#    Vem do repositório oficial do Postgres (PGDG), que é quem publica a major
#    16 para bookworm. Se o PGDG estiver fora do ar, cai no cliente do Debian:
#    uma major defasada ainda conecta, e o build não morre por causa disso.
# --------------------------------------------------------------------------
RUN . /etc/os-release \
 && install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL --retry 3 --retry-connrefused \
      https://www.postgresql.org/media/keys/ACCC4CF8.asc \
      -o /etc/apt/keyrings/pgdg.asc \
 && echo "deb [signed-by=/etc/apt/keyrings/pgdg.asc] https://apt.postgresql.org/pub/repos/apt ${VERSION_CODENAME}-pgdg main" \
      > /etc/apt/sources.list.d/pgdg.list \
 && { apt-get update && apt-get install -y --no-install-recommends "postgresql-client-${PG_MAJOR}" ; } \
    || { echo ">> PGDG indisponivel: usando o postgresql-client do Debian" \
         && rm -f /etc/apt/sources.list.d/pgdg.list \
         && apt-get update \
         && apt-get install -y --no-install-recommends postgresql-client ; } \
 && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------------------------
# 3. Docker CLI — o que a feature docker-outside-of-docker entregava.
#    Só o cliente: o daemon é o do host, alcançado pelo socket montado no
#    docker-compose.yml deste diretório. Assim `docker compose` de dentro do
#    container enxerga os mesmos db e pgadmin.
# --------------------------------------------------------------------------
RUN . /etc/os-release \
 && install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL --retry 3 --retry-connrefused \
      https://download.docker.com/linux/debian/gpg \
      -o /etc/apt/keyrings/docker.asc \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian ${VERSION_CODENAME} stable" \
      > /etc/apt/sources.list.d/docker.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
      docker-ce-cli \
      docker-compose-plugin \
      docker-buildx-plugin \
 && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------------------------
# 4. Dependências Python. Ficam na imagem, e não num postCreateCommand, para
#    serem cacheadas: o container abre pronto em vez de instalar tudo de novo
#    a cada criação.
# --------------------------------------------------------------------------
# Extras de dev, antes do requirements porque mudam menos (aproveita o cache).
RUN pip install --no-cache-dir pytest httpx ruff

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
 && rm /tmp/requirements.txt

# Sem USER: o container sobe como root (o `sleep infinity` do compose) e o
# VS Code entra como vscode via remoteUser, que é o que permite o ajuste de UID.
