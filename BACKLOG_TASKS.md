# Ficha Anamnese — Refinamento Técnico e Backlog para Agentes

> Detalhamento das fases do `PLANEJAMENTO.md` em **tasks executáveis por agentes** (ex.: Claude Code).
> Cada task é atômica, tem critérios de aceite verificáveis e dependências explícitas.

---

## Como os agentes devem trabalhar (convenções)

- **Premissas técnicas:** SQLAlchemy **síncrono** (trocável por async depois); Pydantic v2; Python 3.11; Postgres (Neon em prod, container em dev).
- **Repositórios:** tasks `[API]` no repo `FichaAnamnese`; tasks `[FE]` no repo `FichaAnamnese-Frontend`; tasks `[INFRA]` podem tocar ambos.
- **Fluxo por task:** um branch por task (`feat/F1-T3-auth-login`), commits no padrão *Conventional Commits*, 1 Pull Request por task.
- **Qualidade obrigatória (API):** `ruff` + `black` sem erros; tipagem em funções públicas; testes `pytest` cobrindo o caminho feliz + 1 erro; migrations via Alembic (nunca `create_all` em prod).
- **Segurança:** nenhum segredo em código/commits; tudo via `.env`. Toda rota de gestão exige autenticação; rotas públicas usam token.
- **Definition of Done global:** código + testes passando + lint ok + migration (se aplicável) + PR descrito + sem segredo versionado.
- **Formato de cada task:** Objetivo · Passos · Arquivos · Critérios de aceite · Depende de.

**Legenda de tags:** `[API]` backend · `[FE]` frontend · `[INFRA]` infraestrutura/deploy.

---

## Visão geral das fases

| Fase | Tema | US cobertas | Nº de tasks |
|------|------|-------------|-------------|
| 0 | Fundação técnica | — | 10 |
| 1 | Auth + Serviços | US10, US8, US9 | 6 |
| 2 | Templates de ficha | US2, US12 | 5 |
| 3 | Atendimentos + link público | US1, US3 | 7 |
| 4 | Imagens + Status/Kanban | US4, US5, US15 | 8 |
| 5 | Avaliação | US6, US7 | 4 |
| 6 | LGPD + PDF + hardening/deploy | US11, US13, US14 | 7 |

---

# FASE 0 — Fundação técnica (destravar a API)

### F0-T1 · `[INFRA]` Higiene de segredos e ambiente
- **Objetivo:** remover segredos do repositório e padronizar configuração por ambiente.
- **Passos:** criar `.gitignore` (incluir `.env`, `__pycache__`, `.venv`); criar `.env.example` com chaves sem valores reais; mover credenciais do `docker-compose.yml` para `${VAR}` lidas do `.env`; **rotacionar** senhas do Postgres/pgAdmin já expostas.
- **Arquivos:** `.gitignore`, `.env.example`, `docker-compose.yml`.
- **Critérios de aceite:** `git grep` não encontra senhas literais; `docker compose config` resolve variáveis do `.env`; app sobe local com as novas credenciais.
- **Depende de:** —

### F0-T2 · `[API]` Corrigir estrutura de pacotes e imports quebrados
- **Objetivo:** deixar o pacote importável e sem ciclos.
- **Passos:** adotar a estrutura `app/{core,models,schemas,routers,services}`; **separar** models SQLAlchemy dos schemas Pydantic (hoje misturados em `usuario/models.py`); corrigir imports inválidos (`from ast import List`, `from ..app...`, `from .models import Status`, `StatusRead` importado de `models`); definir `Base` único em `app/core/database.py`.
- **Arquivos:** todo o pacote `app/`.
- **Critérios de aceite:** `python -c "import app.main"` sem erros; `ruff` sem erros de import; nenhum import circular.
- **Depende de:** —

### F0-T3 · `[API]` Dependências e tooling
- **Objetivo:** completar dependências de runtime e dev.
- **Passos:** adicionar ao `requirements.txt`: `psycopg[binary]`, `pydantic-settings`, `alembic`, `passlib[bcrypt]`, `python-jose[cryptography]`, `python-multipart`; criar `requirements-dev.txt` com `pytest`, `httpx`, `ruff`, `black`; adicionar config de `ruff`/`black` em `pyproject.toml`.
- **Arquivos:** `requirements.txt`, `requirements-dev.txt`, `pyproject.toml`.
- **Critérios de aceite:** `pip install -r requirements.txt -r requirements-dev.txt` sem conflito; `ruff check .` e `black --check .` rodam.
- **Depende de:** —

### F0-T4 · `[API]` Camada de configuração
- **Objetivo:** centralizar settings via `pydantic-settings`.
- **Passos:** criar `app/core/config.py` com classe `Settings` (`DATABASE_URL`, `JWT_SECRET`, `JWT_EXPIRE_MIN`, `CORS_ORIGINS`, credenciais de storage) lendo do `.env`; expor `get_settings()` com cache.
- **Arquivos:** `app/core/config.py`.
- **Critérios de aceite:** teste unitário carrega settings a partir de `.env` de teste; `DATABASE_URL` com senha contendo `@`/`#` é aceita (URL-encoded).
- **Depende de:** F0-T3.

### F0-T5 · `[API]` Camada de banco (engine/session)
- **Objetivo:** conexão e injeção de sessão.
- **Passos:** `app/core/database.py` com `engine` (pool + `pool_pre_ping=True`), `SessionLocal`, `Base` e dependência `get_db()` (yield + close).
- **Arquivos:** `app/core/database.py`.
- **Critérios de aceite:** teste de integração abre e fecha sessão contra Postgres de teste; `get_db` usável como `Depends`.
- **Depende de:** F0-T4.

### F0-T6 · `[API]` Bootstrap do app + CORS + healthcheck
- **Objetivo:** app pronto para receber routers e o frontend.
- **Passos:** reescrever `main.py` para criar o `FastAPI`, configurar `CORSMiddleware` a partir de `CORS_ORIGINS`, registrar routers (inicialmente vazios) e expor `GET /health` retornando status + versão.
- **Arquivos:** `app/main.py`.
- **Critérios de aceite:** `GET /health` responde 200; preflight CORS de origem permitida retorna os headers corretos; Swagger em `/docs` abre.
- **Depende de:** F0-T5.

### F0-T7 · `[API]` Modelo de dados revisado + Alembic
- **Objetivo:** schema versionado conforme a modelagem do plano.
- **Passos:** implementar os models (`profissional`, `cliente`, `servico`, `status`, `tipo_pergunta`, `ficha`, `ficha_pergunta`, `ficha_pergunta_opcao`, `atendimento`, `resposta`, `atendimento_imagem`, `status_historico`, `avaliacao`, `consentimento`) com `created_at/updated_at`; corrigir `sobrenome` → `String`, `Tipo` como domínio puro, `resposta` texto/opção nuláveis com `CHECK`; inicializar Alembic (`alembic init`) apontando para o `Base`; gerar a **migration inicial**.
- **Arquivos:** `app/models/*`, `alembic/`, `alembic.ini`.
- **Critérios de aceite:** `alembic upgrade head` cria todas as tabelas; `alembic downgrade base` reverte; `alembic check` sem *drift* após o upgrade.
- **Depende de:** F0-T5.

### F0-T8 · `[API]` Seeds iniciais
- **Objetivo:** popular dados de domínio.
- **Passos:** script/migration de dados que insere os **11 status** (com `ordem` do `status_atendimentos.md`), os `tipo_pergunta` (texto, textarea, radio, select, checkbox, date, number, file) e o catálogo de serviços de `servicos.md`.
- **Arquivos:** `alembic/versions/*_seed_*.py` ou `scripts/seed.py`.
- **Critérios de aceite:** após o seed, `status`, `tipo_pergunta` e `servico` têm as linhas esperadas; seed é idempotente.
- **Depende de:** F0-T7.

### F0-T9 · `[INFRA]` CI (GitHub Actions)
- **Objetivo:** portão de qualidade automático.
- **Passos:** workflow que roda em PR: `ruff`, `black --check`, `pytest` (com Postgres de serviço) e `alembic upgrade head` num banco limpo.
- **Arquivos:** `.github/workflows/ci.yml`.
- **Critérios de aceite:** PR só fica verde com lint + testes + migration ok.
- **Depende de:** F0-T3, F0-T7.

### F0-T10 · `[INFRA]` Ambiente de desenvolvimento
- **Objetivo:** subir tudo local com um comando.
- **Passos:** ajustar `docker-compose.yml` (api + db + pgadmin) usando variáveis do `.env` e `healthcheck`; documentar no `README` como rodar (`docker compose up`, migrations, seed).
- **Arquivos:** `docker-compose.yml`, `Dockerfile`, `README.md`.
- **Critérios de aceite:** `docker compose up` sobe a API saudável conectada ao Postgres; passos do README reproduzem o ambiente do zero.
- **Depende de:** F0-T6, F0-T8.

---

# FASE 1 — Autenticação + Serviços (US10, US8, US9)

### F1-T1 · `[API]` Segurança: hashing + JWT
- **Objetivo:** utilidades de auth.
- **Passos:** `app/core/security.py` com `hash_senha`/`verificar_senha` (bcrypt via passlib) e `criar_access_token`/`decodificar_token` (jose); dependência `get_current_professional`.
- **Arquivos:** `app/core/security.py`.
- **Critérios de aceite:** testes de hash (round-trip) e de token (emissão/validação/expiração); token inválido → 401.
- **Depende de:** F0-T7.

### F1-T2 · `[API]` Endpoints de autenticação
- **Objetivo:** login e sessão do profissional.
- **Passos:** router `auth` com `POST /auth/login` (OAuth2 password → JWT) e `GET /auth/me`; criação do 1º profissional via script/seed protegido (sem auto-registro público no MVP).
- **Arquivos:** `app/routers/auth.py`, `app/services/auth.py`, `scripts/create_admin.py`.
- **Critérios de aceite:** login com credenciais válidas retorna JWT; `/auth/me` exige token; credencial errada → 401.
- **Depende de:** F1-T1.

### F1-T3 · `[API]` CRUD de serviços (service layer)
- **Objetivo:** regras de negócio de serviços.
- **Passos:** `services/servico.py` com criar/listar/obter/atualizar e **ativar/desativar** (soft toggle via campo `ativo`); listagem com filtro `ativo`.
- **Arquivos:** `app/services/servico.py`, `app/schemas/servico.py`.
- **Critérios de aceite:** testes cobrindo criação, edição, ativar/desativar e filtro por `ativo`.
- **Depende de:** F0-T7.

### F1-T4 · `[API]` Router de serviços (protegido)
- **Objetivo:** expor o CRUD.
- **Passos:** router `servicos` com `GET/POST/PUT /servicos`, `PATCH /servicos/{id}/ativar` e `/desativar`, todos sob `get_current_professional`.
- **Arquivos:** `app/routers/servicos.py`.
- **Critérios de aceite:** endpoints exigem auth; desativar não apaga; serviço inativo continua acessível por id.
- **Depende de:** F1-T2, F1-T3.

### F1-T5 · `[FE]` Login + gestão de serviços
- **Objetivo:** telas iniciais autenticadas.
- **Passos:** setup React+Vite+TS, Tailwind, TanStack Query, cliente HTTP com bearer token; tela de login; tela de listagem/CRUD de serviços com toggle ativar/desativar.
- **Arquivos:** repo `FichaAnamnese-Frontend`.
- **Critérios de aceite:** login persiste sessão; lista mostra serviços; toggle reflete no backend; rota protegida redireciona sem token.
- **Depende de:** F1-T4.

### F1-T6 · `[API]` Testes de auth e serviços
- **Objetivo:** cobertura da fase.
- **Passos:** suíte de integração para login, acesso protegido e CRUD de serviços.
- **Arquivos:** `tests/test_auth.py`, `tests/test_servicos.py`.
- **Critérios de aceite:** suíte verde no CI.
- **Depende de:** F1-T4.

---

# FASE 2 — Templates de ficha (US2, US12)

### F2-T1 · `[API]` Service layer de templates
- **Objetivo:** criar/editar template com perguntas e opções aninhadas.
- **Passos:** `services/ficha.py` para criar `ficha` + `ficha_pergunta[]` (com `tipo`, `ordem`, `obrigatoria`) + `ficha_pergunta_opcao[]`; validar que o `servico` existe e está **ativo** ao criar; edição preservando integridade da ordem.
- **Arquivos:** `app/services/ficha.py`, `app/schemas/ficha.py`.
- **Critérios de aceite:** cria template completo em uma chamada; recusa serviço inativo/inexistente; ordem das perguntas respeitada.
- **Depende de:** F1-T3.

### F2-T2 · `[API]` Router de templates
- **Objetivo:** expor CRUD de fichas.
- **Passos:** `GET/POST/PUT /fichas`, `GET /fichas/{id}` (com perguntas/opções), protegido.
- **Arquivos:** `app/routers/fichas.py`.
- **Critérios de aceite:** retorna template aninhado; auth exigida; validação de payload (tipos permitidos).
- **Depende de:** F2-T1.

### F2-T3 · `[API]` Duplicar e (des)ativar template
- **Objetivo:** reuso (US12).
- **Passos:** `POST /fichas/{id}/duplicar` (cópia profunda) e `PATCH /fichas/{id}/ativar|desativar`.
- **Arquivos:** `app/routers/fichas.py`, `app/services/ficha.py`.
- **Critérios de aceite:** cópia gera novo id sem referenciar o original; template inativo não aparece na criação de atendimento.
- **Depende de:** F2-T2.

### F2-T4 · `[FE]` Construtor de fichas
- **Objetivo:** UI para montar templates.
- **Passos:** tela de builder (adicionar/reordenar perguntas, definir tipo, opções, obrigatoriedade, vincular serviço); listar/duplicar/(des)ativar.
- **Arquivos:** repo `FichaAnamnese-Frontend`.
- **Critérios de aceite:** cria e edita template completo; drag-and-drop de ordem persiste; preview do formulário.
- **Depende de:** F2-T3.

### F2-T5 · `[API]` Testes de templates
- **Objetivo:** cobertura da fase.
- **Arquivos:** `tests/test_fichas.py`.
- **Critérios de aceite:** cobre criação aninhada, duplicação e regra de serviço ativo.
- **Depende de:** F2-T2.

---

# FASE 3 — Atendimentos + link público (US1, US3)

### F3-T1 · `[API]` Cadastro de cliente
- **Objetivo:** identidade fixa do cliente.
- **Passos:** `services/cliente.py` + router `clientes` (criar/buscar/listar) com campos nome, sobrenome, telefone, e-mail, data_nascimento; deduplicação por e-mail/telefone (aviso, não bloqueio).
- **Arquivos:** `app/services/cliente.py`, `app/routers/clientes.py`, `app/schemas/cliente.py`.
- **Critérios de aceite:** CRUD funcional e protegido; validação de e-mail.
- **Depende de:** F1-T2.

### F3-T2 · `[API]` Criar atendimento + token público
- **Objetivo:** iniciar atendimento e gerar link.
- **Passos:** `POST /atendimentos` cria atendimento (ficha + cliente, status `Não iniciado`), gera `token_publico` com `secrets.token_urlsafe(32)` e `token_expira_em`; endpoint para (re)gerar token.
- **Arquivos:** `app/services/atendimento.py`, `app/routers/atendimentos.py`, `app/schemas/atendimento.py`.
- **Critérios de aceite:** token único e aleatório; expiração configurável; atendimento nasce no status inicial.
- **Depende de:** F2-T2, F3-T1.

### F3-T3 · `[API]` Endpoint público — obter formulário por token
- **Objetivo:** cliente vê a ficha sem login.
- **Passos:** `GET /publico/atendimentos/{token}` retorna o template renderizável (perguntas/opções) **sem** dados sensíveis do profissional; valida token/expiração.
- **Arquivos:** `app/routers/publico.py`.
- **Critérios de aceite:** token válido → 200 com formulário; expirado/inexistente → 410/404; rota sem auth.
- **Depende de:** F3-T2.

### F3-T4 · `[API]` Endpoint público — submeter respostas
- **Objetivo:** gravar respostas e evoluir status.
- **Passos:** `POST /publico/atendimentos/{token}/respostas` valida obrigatórias e tipos, grava `resposta[]` (texto **ou** opção), muda status para `Aguardando avaliação`, registra histórico.
- **Arquivos:** `app/routers/publico.py`, `app/services/atendimento.py`.
- **Critérios de aceite:** respostas persistidas corretamente; obrigatória ausente → 422; reenvio após preenchido é bloqueado.
- **Depende de:** F3-T3, F0-T7.

### F3-T5 · `[API]` Regras de token
- **Objetivo:** segurança do link.
- **Passos:** utilitário central de validação (expiração, uso único opcional); rate limit básico por token.
- **Arquivos:** `app/services/token.py`.
- **Critérios de aceite:** testes de expiração e reuso; brute force mitigado.
- **Depende de:** F3-T2.

### F3-T6 · `[FE]` Fluxo de atendimento + formulário público
- **Objetivo:** UI da esteticista e do cliente.
- **Passos:** tela para criar atendimento e copiar link; **página pública** (sem login) que renderiza o formulário a partir do token e envia respostas (React Hook Form + Zod).
- **Arquivos:** repo `FichaAnamnese-Frontend`.
- **Critérios de aceite:** link abre formulário; validação client-side; envio confirma sucesso; token inválido mostra estado apropriado.
- **Depende de:** F3-T4.

### F3-T7 · `[API]` Testes de atendimento/público
- **Objetivo:** cobertura da fase.
- **Arquivos:** `tests/test_atendimentos.py`, `tests/test_publico.py`.
- **Critérios de aceite:** cobre criação, token válido/expirado, submissão e transição de status.
- **Depende de:** F3-T4.

---

# FASE 4 — Imagens + Status/Kanban (US4, US5, US15)

### F4-T1 · `[INFRA]` Integração com object storage
- **Objetivo:** armazenar imagens fora do servidor.
- **Passos:** cliente S3-compatível (`boto3`) para **Cloudflare R2**; funções de *presigned upload/download*; configs no `Settings`.
- **Arquivos:** `app/core/storage.py`, `app/core/config.py`.
- **Critérios de aceite:** gera URL assinada de upload e leitura; testes com storage mockado.
- **Depende de:** F0-T4.

### F4-T2 · `[API]` Upload de imagem do atendimento
- **Objetivo:** anexar fotos (US4).
- **Passos:** `POST /atendimentos/{id}/imagens` (presigned ou multipart) grava `atendimento_imagem` (url, descricao); `GET` lista; `DELETE` remove do storage + registro.
- **Arquivos:** `app/routers/imagens.py`, `app/services/imagem.py`.
- **Critérios de aceite:** valida tipo/tamanho; imagens vinculadas ao atendimento; delete remove do bucket.
- **Depende de:** F4-T1, F3-T2.

### F4-T3 · `[API]` Máquina de estados (transições)
- **Objetivo:** validar mudanças de status conforme `status_atendimentos.md`.
- **Passos:** definir `TRANSICOES_PERMITIDAS` (dict origem→destinos) incluindo exceções `Pausado`/`Cancelado`/`Abandonado`; função `pode_transicionar()`.
- **Arquivos:** `app/services/status.py`.
- **Critérios de aceite:** transição válida ok; inválida → 409/422; tabela de transições coberta por testes.
- **Depende de:** F0-T8.

### F4-T4 · `[API]` Mudar status + histórico
- **Objetivo:** evoluir atendimento com trilha.
- **Passos:** `PATCH /atendimentos/{id}/status` aplica `pode_transicionar`, grava `status_historico` (anterior, novo, observação, timestamp).
- **Arquivos:** `app/routers/atendimentos.py`, `app/services/atendimento.py`.
- **Critérios de aceite:** cada mudança gera 1 registro de histórico; transição inválida não altera o estado.
- **Depende de:** F4-T3.

### F4-T5 · `[API]` Listagem/filtro de atendimentos (kanban)
- **Objetivo:** visão por status (US5).
- **Passos:** `GET /atendimentos` com filtros `status`, `servico`, `cliente`, paginação e ordenação; agregação por status para a coluna do kanban.
- **Arquivos:** `app/routers/atendimentos.py`.
- **Critérios de aceite:** filtros combináveis; contagem por status correta; paginação estável.
- **Depende de:** F3-T2.

### F4-T6 · `[API]` Timeline do atendimento (US15)
- **Objetivo:** evolução consolidada.
- **Passos:** `GET /atendimentos/{id}/timeline` unindo respostas, mudanças de status e imagens em ordem cronológica.
- **Arquivos:** `app/routers/atendimentos.py`, `app/services/atendimento.py`.
- **Critérios de aceite:** retorna eventos ordenados por data com tipo do evento.
- **Depende de:** F4-T2, F4-T4.

### F4-T7 · `[FE]` Kanban + detalhe do atendimento
- **Objetivo:** UI de acompanhamento.
- **Passos:** board por status com mover-card (dispara `PATCH status`); tela de detalhe com respostas, upload/galeria de imagens e timeline.
- **Arquivos:** repo `FichaAnamnese-Frontend`.
- **Critérios de aceite:** mover card respeita transições (erro tratado); upload aparece na galeria; timeline renderiza.
- **Depende de:** F4-T4, F4-T5, F4-T6.

### F4-T8 · `[API]` Testes de imagens e status
- **Objetivo:** cobertura da fase.
- **Arquivos:** `tests/test_imagens.py`, `tests/test_status.py`.
- **Critérios de aceite:** cobre upload/delete, todas as transições válidas e algumas inválidas, filtros do kanban.
- **Depende de:** F4-T4, F4-T2.

---

# FASE 5 — Avaliação (US6, US7)

### F5-T1 · `[API]` Gerar link de avaliação
- **Objetivo:** habilitar avaliação só nos status permitidos.
- **Passos:** `POST /atendimentos/{id}/avaliacao/link` gera `token_publico` da avaliação **apenas** se status ∈ {`Em acompanhamento`, `Finalizado`}.
- **Arquivos:** `app/services/avaliacao.py`, `app/routers/avaliacoes.py`.
- **Critérios de aceite:** status permitido → token; status diferente → 409; token com expiração.
- **Depende de:** F4-T4.

### F5-T2 · `[API]` Submissão pública de avaliação
- **Objetivo:** cliente avalia (US7).
- **Passos:** `GET/POST /publico/avaliacao/{token}` (nota 1–5 + comentário); grava `avaliacao`; impede avaliação duplicada.
- **Arquivos:** `app/routers/publico.py`, `app/services/avaliacao.py`.
- **Critérios de aceite:** nota fora de 1–5 → 422; token inválido/expirado tratado; 1 avaliação por token.
- **Depende de:** F5-T1.

### F5-T3 · `[FE]` Página de avaliação + visualização
- **Objetivo:** UI de avaliação.
- **Passos:** página pública de avaliação (estrelas + comentário); exibição da nota no detalhe do atendimento para a esteticista.
- **Arquivos:** repo `FichaAnamnese-Frontend`.
- **Critérios de aceite:** envio confirma; nota aparece no detalhe.
- **Depende de:** F5-T2.

### F5-T4 · `[API]` Testes de avaliação
- **Objetivo:** cobertura da fase.
- **Arquivos:** `tests/test_avaliacao.py`.
- **Critérios de aceite:** cobre regra de status, faixa da nota e unicidade.
- **Depende de:** F5-T2.

---

# FASE 6 — LGPD + PDF + hardening/deploy (US11, US13, US14)

### F6-T1 · `[API]` Consentimento LGPD versionado
- **Objetivo:** registrar consentimento de dados sensíveis (US11).
- **Passos:** exigir aceite no fluxo público (F3-T4) gravando `consentimento` (versão do termo, `aceito_em`, IP); bloquear submissão sem aceite; endpoint para consultar histórico de consentimentos.
- **Arquivos:** `app/services/consentimento.py`, `app/routers/publico.py`.
- **Critérios de aceite:** submissão sem aceite → 422; registro contém versão + timestamp; termo de imagem tratado separadamente.
- **Depende de:** F3-T4.

### F6-T2 · `[API]` Exportar ficha preenchida em PDF (US13)
- **Objetivo:** documento clínico.
- **Passos:** `GET /atendimentos/{id}/pdf` gera PDF com identificação, respostas, imagens e termos (usar a skill/documentação de PDF do ambiente).
- **Arquivos:** `app/services/pdf.py`, `app/routers/atendimentos.py`.
- **Critérios de aceite:** PDF válido baixável, protegido por auth, com respostas e imagens.
- **Depende de:** F4-T6.

### F6-T3 · `[API]` Envio do link (e-mail/WhatsApp) (US14)
- **Objetivo:** distribuir links.
- **Passos:** abstração `notificador` com provedor de e-mail (ex.: Resend/SMTP) e *link* de WhatsApp (`wa.me` pré-preenchido); `POST /atendimentos/{id}/enviar-link`.
- **Arquivos:** `app/services/notificacao.py`, `app/routers/atendimentos.py`.
- **Critérios de aceite:** e-mail enviado em teste (provider mockado); link de WhatsApp válido gerado.
- **Depende de:** F3-T2.

### F6-T4 · `[API]` Hardening de segurança
- **Objetivo:** endurecer a API.
- **Passos:** rate limiting (ex.: `slowapi`) nas rotas públicas/login; headers de segurança; CORS restrito ao domínio do front; tamanho máximo de upload; logs sem dados sensíveis.
- **Arquivos:** `app/main.py`, `app/core/security.py`.
- **Critérios de aceite:** brute force em `/auth/login` limitado; headers presentes; CORS só permite o domínio configurado.
- **Depende de:** F1-T2.

### F6-T5 · `[INFRA]` Deploy backend + banco
- **Objetivo:** produção da API.
- **Passos:** provisionar **Neon** (Postgres) e rodar `alembic upgrade head`; deploy da API no **Render** (build via Dockerfile, env vars, `/health` como health check); documentar cold start e opção de upgrade para Starter.
- **Arquivos:** `render.yaml` (ou docs), `README` de deploy.
- **Critérios de aceite:** API pública responde `/health`; migrations aplicadas em prod; segredos só em env do Render.
- **Depende de:** F0-T7.

### F6-T6 · `[INFRA]` Deploy frontend + storage + observabilidade
- **Objetivo:** produção do front e operação.
- **Passos:** deploy do front em **Cloudflare Pages/Vercel** apontando para a API; bucket **R2** de produção; backups do Neon; monitoramento básico (uptime + logs).
- **Arquivos:** repo `FichaAnamnese-Frontend`, docs de operação.
- **Critérios de aceite:** front em prod consome a API (CORS ok); upload de imagem funciona ponta a ponta; backup configurado.
- **Depende de:** F6-T5, F4-T1.

---

## Ordem de execução e paralelização

- **Sequencial crítico:** F0 → F1 → F2 → F3 → F4 → F5. Cada fase depende de artefatos da anterior.
- **Dentro da Fase 0, em paralelo:** F0-T1, F0-T2, F0-T3 (independentes) antes de F0-T4/T5.
- **Trilhas paralelas por fase:** assim que a task `[API]` do endpoint estiver pronta, a task `[FE]` correspondente pode rodar em paralelo com os testes `[API]`.
- **Fase 6** é majoritariamente transversal: F6-T5/T6 (deploy) podem começar cedo (após F0-T7) como pipeline; F6-T1 depende da Fase 3; F6-T2 da Fase 4.

## Sugestão de prompt para o agente executor

> "Implemente a task **{ID}** do `BACKLOG_TASKS.md`. Siga as convenções do topo do arquivo (branch, Conventional Commits, ruff/black, pytest, Alembic, zero segredos). Entregue: código + testes + migration (se houver) + descrição de PR. Não avance para outra task."
