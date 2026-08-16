# Ficha Anamnese — Refino e Planejamento de Desenvolvimento

> Studio de estética: criação de fichas de anamnese, acompanhamento e atualização de atendimentos.
> Documento de planejamento baseado na análise do repositório `becadev/FichaAnamnese` (API FastAPI + histórias de usuário).

---

## 1. Diagnóstico do estado atual

### 1.1. O que já existe
- **API FastAPI** iniciada (FastAPI 0.111, Uvicorn, Pydantic 2.9, SQLAlchemy 2.0).
- **Modelo de dados** esboçado com abordagem de **formulário dinâmico** (`ficha` → `ficha_pergunta` → `ficha_pergunta_opcao`; `ficha_resposta` → `pergunta_resposta`; `ficha_imagens`).
- **Documentação de negócio muito boa**: modelo completo de ficha de anamnese (23 seções), catálogo de serviços e uma **máquina de estados de status bem definida** (11 estados + regras de transição).
- `docker-compose` com Postgres 16 + pgAdmin.

### 1.2. Problemas que precisam ser corrigidos antes de evoluir

**🔴 Segurança (urgente)**
- O `docker-compose.yml` versiona **senha do banco em texto puro** (`bd!Q@W#E$R1`) e a senha do pgAdmin (`admin`). Como o repositório ficou público, **considere esses segredos comprometidos**: gere novas senhas e nunca mais as versione (use `.env` + `.gitignore`).
- Essa mesma senha tem caracteres especiais (`!@#$`) que **quebram a `DATABASE_URL`** sem URL-encoding (`@` e `#` são delimitadores de URL).

**🔴 A API não sobe hoje (imports quebrados)**
- `app/models.py`: `from ..app.modules.fichas.models import ...` — caminho relativo inválido.
- `modules/fichas/models.py`: importa `from .models import Status` (de si mesmo), `from FichaAnamnese_api.app.models import Tipo` (caminho absoluto que não bate com o pacote) e cria **import circular** com `usuario` e `app.models`.
- `modules/fichas/schema.py`: importa `StatusRead, TipoRead` de `app.models`, mas eles estão em `app/schemas.py`.
- `modules/usuario/models.py`: `from ast import List` (deveria ser `from typing import List`) e **mistura modelos SQLAlchemy com schemas Pydantic** no mesmo arquivo.
- `main.py` é apenas um "hello world"; **nenhum router é incluído** (e todos os `router.py`/`services.py` estão vazios).

**🟠 Modelagem de dados**
- `Pessoa.sobrenome = Column(BigInteger)` e `PessoaBase.sobrenome: int` — sobrenome como número. Deve ser `String`.
- `Tipo.id` está definido como **PK e FK ao mesmo tempo** (`ForeignKey("ficha_pergunta.tipo_id")`) — a direção está invertida. `Tipo` é tabela de domínio; quem aponta para ela é `FichaPergunta`.
- **Não existe tabela `Servico`**, apesar das histórias 2, 8 e 9 exigirem CRUD de serviços. `Ficha.servico` é um `BigInteger` solto (deveria ser FK para `servico`).
- `PerguntaResposta.reposta_texto` (typo) é `NOT NULL` **e** `resposta_opcao_id` também é `NOT NULL` — isso impede respostas só-texto ou só-opção. Elas deveriam ser mutuamente excludentes/nuláveis.
- **Faltam tabelas** para: avaliação do cliente (US 6/7), token de link público (US 1/3/6), histórico de mudança de status e autenticação do profissional (senha).
- Faltam `created_at`/`updated_at` na maioria das tabelas.

**🟠 Infra/base técnica ausente**
- **Sem driver Postgres** no `requirements.txt` (falta `psycopg[binary]`).
- Sem gestão de configuração (`pydantic-settings`/`.env`).
- Sem **migrations** (Alembic) — hoje não há como versionar o schema.
- Sem **CORS** configurado (o frontend não conseguirá chamar a API).
- Sem camada de sessão do banco em `dependencies.py` (está vazio).

---

## 2. Refino das histórias de usuário

### 2.1. Histórias reescritas com critérios de aceite

**US1 — Criar cadastro do cliente e gerar link**
*Como esteticista, quero cadastrar os dados gerais do cliente (nome, sobrenome, telefone, e-mail, data de nascimento) e gerar um link para ele preencher a ficha.*
- Dado um cliente novo, consigo cadastrar os dados básicos e o sistema cria um **atendimento** com status inicial `Não iniciado`.
- O sistema gera um **link público com token aleatório e expiração**.
- O link pode ser copiado (e, no futuro, enviado por WhatsApp/e-mail).

**US2 — Templates de ficha vinculados a serviço**
*Como esteticista, quero criar templates de ficha e vinculá-los a um serviço para reutilizar.*
- Consigo criar uma ficha com título, serviço associado e uma lista ordenada de perguntas (tipos: texto, múltipla escolha, seleção única, data, número, checkbox).
- Um template só fica disponível para uso se o serviço estiver **ativo**.

**US3 — Cliente responde online**
*Como cliente, quero abrir o link e responder a ficha pelo navegador.*
- Ao abrir um token válido, vejo o formulário renderizado a partir do template.
- Ao enviar, as respostas são gravadas e o status vai para `Aguardando avaliação`.
- Token expirado/inválido mostra mensagem apropriada.

**US4 — Anexar fotos e evoluir o atendimento**
*Como esteticista, quero anexar fotos ao atendimento para registrar a evolução.*
- Consigo subir 1..N imagens com descrição e data.
- As imagens ficam em **armazenamento de objetos** (não no disco do servidor).

**US5 — Visualizar atendimentos por status**
*Como esteticista, quero listar/filtrar atendimentos por status (visão tipo kanban).*
- Consigo filtrar por status e por serviço.
- Consigo **avançar/retroceder o status respeitando as regras de transição** do documento `status_atendimentos.md`.
- Cada mudança de status é registrada em histórico.

**US6 — Gerar link de avaliação**
*Como esteticista, quero gerar um link para o cliente avaliar um atendimento.*
- O link de avaliação só é gerado quando o status é `Em acompanhamento` ou `Finalizado`.

**US7 — Cliente avalia**
*Como cliente, quero avaliar o serviço (nota + comentário) via link.*
- A avaliação só é aceita nos status permitidos.

**US8/US9 — Gerir serviços**
*Como esteticista, quero adicionar serviços e ativar/desativar.*
- Serviços inativos não aparecem na criação de novas fichas, mas **não somem** de atendimentos históricos.

### 2.2. Histórias que faltavam (recomendo incluir)

| # | História | Por quê |
|---|----------|---------|
| US10 | Login/autenticação da esteticista | Toda a área de gestão precisa ser protegida (hoje `Usuario` nem tem senha). |
| US11 | Consentimento LGPD + termo de imagem no formulário | Dados de saúde são **dados sensíveis** (LGPD). O termo já existe no modelo de ficha; falta registrá-lo com data/versão. |
| US12 | Editar/duplicar template de ficha | Reuso e correção de perguntas. |
| US13 | Exportar ficha preenchida em PDF | Documento clínico/assinatura. |
| US14 | Enviar link por WhatsApp/e-mail | US1 diz "envia o link", mas não define o canal. |
| US15 | Histórico de evolução do atendimento (timeline) | Suporta o acompanhamento clínico (seções 16/19 do modelo). |

### 2.3. Priorização (MoSCoW → MVP)

- **Must (MVP):** US10, US8, US9, US2, US1, US3, US5, US4.
- **Should:** US6, US7, US11, US15.
- **Could:** US12, US13, US14.
- **Won't (por ora):** multi-studio/multi-tenant, app mobile nativo, agenda/calendário, pagamentos.

---

## 3. Decisões de arquitetura

### 3.1. Formulário dinâmico (EAV) vs. schema fixo
O modelo atual é **dinâmico** (perguntas/opções/respostas em tabelas). É a escolha certa para as US2/US12 (a esteticista monta as próprias fichas), mas custa em complexidade de consulta e validação.
**Recomendação:** manter o modelo dinâmico para o corpo da ficha, porém guardar a **identidade do cliente em colunas fixas** (nome, telefone, e-mail, nascimento) — são campos sempre presentes e usados em filtros/buscas.

### 3.2. Modelo de dados revisado (proposta)

```
profissional        (id, nome, email [unique], senha_hash, registro_profissional, ativo, created_at, updated_at)
cliente             (id, nome, sobrenome [String], telefone, email, data_nascimento, created_at, updated_at)
servico             (id, nome, descricao, ativo [bool], created_at, updated_at)
status              (id, codigo, descricao, ordem)                      -- seed com os 11 estados
tipo_pergunta       (id, codigo, descricao)                             -- texto, textarea, radio, select, checkbox, date, number, file

ficha               (id, titulo, servico_id → servico, ativo, created_at, updated_at)
ficha_pergunta      (id, ficha_id → ficha, titulo, tipo_id → tipo_pergunta, ordem, obrigatoria [bool])
ficha_pergunta_opcao(id, ficha_pergunta_id → ficha_pergunta, titulo, ordem)

atendimento         (id, ficha_id → ficha, cliente_id → cliente, status_id → status,
                     token_publico [unique], token_expira_em, created_at, updated_at)
resposta            (id, atendimento_id → atendimento, ficha_pergunta_id → ficha_pergunta,
                     resposta_texto [nullable], ficha_pergunta_opcao_id [nullable])   -- CHECK: um dos dois preenchido
atendimento_imagem  (id, atendimento_id → atendimento, url, descricao, created_at)
status_historico    (id, atendimento_id → atendimento, status_anterior_id, status_novo_id, observacao, created_at)
avaliacao           (id, atendimento_id → atendimento, nota [1..5], comentario, token_publico, created_at)
consentimento       (id, atendimento_id → atendimento, versao_termo, aceito_em, ip)   -- LGPD
```

Principais correções embutidas: `Servico` como entidade, `sobrenome` como texto, `Tipo` como domínio puro, resposta texto/opção nuláveis, tokens de link, histórico de status, autenticação e trilha de consentimento.

### 3.3. Máquina de estados
Implementar as **regras de transição** de `status_atendimentos.md` como validação no backend (um dicionário `TRANSICOES_PERMITIDAS`), rejeitando saltos inválidos com HTTP 409/422. Estados de exceção (`Pausado`, `Cancelado`, `Abandonado`) tratados conforme o documento.

### 3.4. Estrutura de pastas sugerida (API)
```
app/
  core/        config.py (pydantic-settings), security.py (JWT/hash), database.py (engine/session)
  models/      um arquivo por agregado
  schemas/     Pydantic separado dos models
  routers/     auth, servicos, fichas, atendimentos, avaliacoes, imagens
  services/    regras de negócio (transição de status, geração de token)
  main.py      cria app, inclui routers, configura CORS
alembic/       migrations
```

---

## 4. Stack recomendada e deploy gratuito / baixo custo

### 4.1. Frontend
- **React + Vite + TypeScript** (você já domina React; Vite dá build rápido e estático).
- UI: **Tailwind CSS** + um kit acessível (shadcn/ui ou Chakra).
- Dados/estado de servidor: **TanStack Query**; formulários: **React Hook Form + Zod**.
- **Deploy: Cloudflare Pages ou Vercel** (free, site estático, **sem "dormir"**).

### 4.2. Backend (a sua FastAPI)
- **Render (free web service)** para começar com custo zero.
- **Ressalva importante:** no plano free o serviço **hiberna após ~15 min de inatividade** e o primeiro acesso demora ~30–60s (cold start). Para uso interno é aceitável; para os **links públicos ao cliente**, considere migrar a API para um plano pago (~US$ 7/mês) quando o cold start incomodar.

### 4.3. Banco de dados
- **Neon (Postgres serverless, free)** — combina bem com Render, tem *scale-to-zero* e branching. Precisa do driver `psycopg[binary]` e da `DATABASE_URL` com senha **URL-encoded**.
- Alternativa: **Supabase**, que entrega Postgres + Auth + Storage no mesmo lugar (bom se você quiser terceirizar autenticação e armazenamento de imagens). Contrapartida: no free o projeto **pausa após ~1 semana** de inatividade e há mais *lock-in*.

### 4.4. Armazenamento de imagens (US4)
- **Não** salve arquivos no disco do servidor (o filesystem do Render free é efêmero e some a cada redeploy/hibernação).
- **Cloudflare R2** (free, sem taxa de egress) ou **Supabase Storage** (free) ou **Backblaze B2**.

### 4.5. Autenticação
- MVP simples: **JWT no FastAPI** (`passlib[bcrypt]` para hash + `python-jose`/`pyjwt`). Um único perfil (esteticista) já cobre o MVP.
- Se adotar Supabase, pode usar o **Supabase Auth** e validar o JWT na API.

### 4.6. Comparativo das plataformas (panorama meados de 2026)

> ⚠️ Free tiers mudam com frequência — confirme os limites na página oficial antes de fechar a escolha.

| Camada | Opção recomendada | Free? | Observação principal |
|--------|-------------------|-------|----------------------|
| Frontend | Cloudflare Pages / Vercel | Sim, estável | Estático não hiberna |
| Backend | Render (web service) | Sim | Hiberna após 15 min; cold start 30–60s; 750 h/mês |
| Backend (pago) | Render Starter | ~US$ 7/mês | Always-on, sem cold start |
| Banco | Neon | Sim | Serverless, scale-to-zero, 0,5 GB/projeto |
| Banco (alt.) | Supabase | Sim | DB+Auth+Storage juntos; pausa após ~7 dias ocioso |
| Imagens | Cloudflare R2 | Sim | 10 GB, sem egress |

**Caminho de custo:**
- **Fase inicial:** tudo free → **US$ 0/mês** (aceitando cold start no backend).
- **Quando incomodar:** só o backend vira pago → **~US$ 7/mês**, mantendo front, banco e imagens no free.

---

## 5. Roadmap de desenvolvimento (por fases)

**Fase 0 — Fundação técnica** *(destravar a API)*
- Corrigir imports/estrutura; separar models × schemas.
- Adicionar `psycopg[binary]`, `pydantic-settings`, `alembic`, `passlib`, `python-jose`.
- `core/database.py` (engine + `get_db`), `core/config.py` (.env), CORS no `main.py`.
- Trocar segredos expostos; criar `.env.example` e `.gitignore`.
- Primeira migration + seed de `status`, `tipo_pergunta` e `servico` (catálogo inicial).

**Fase 1 — Autenticação + Serviços** (US10, US8, US9)
- Login JWT; CRUD de serviços com ativar/desativar.

**Fase 2 — Templates de ficha** (US2, US12)
- CRUD de `ficha`/`ficha_pergunta`/`ficha_pergunta_opcao` vinculado a serviço.

**Fase 3 — Atendimentos + link público** (US1, US3)
- Cadastro de cliente, geração de atendimento e token; endpoint público de preenchimento.

**Fase 4 — Imagens + Status/Kanban** (US4, US5, US15)
- Upload para object storage; listagem por status; transições validadas + histórico.

**Fase 5 — Avaliação** (US6, US7)
- Link e submissão de avaliação nos status permitidos.

**Fase 6 — LGPD + PDF + hardening de deploy** (US11, US13, US14)
- Registro de consentimento versionado; exportação em PDF; envio de link; rate limiting e backups.

---

## 6. Segurança e LGPD (não pular)

- **Dado sensível:** ficha de anamnese contém dados de saúde → tratamento especial na LGPD. Defina **base legal (consentimento)**, finalidade, prazo de retenção e descarte.
- **Consentimento** registrado com data, versão do termo e (opcional) IP; termo de uso de imagem separado.
- **Tokens de link:** aleatórios (`secrets.token_urlsafe`), com **expiração** e, de preferência, uso único.
- **Senhas:** hash com bcrypt/argon2; nunca em texto.
- **Segredos:** só em variáveis de ambiente; **rotacionar os que já vazaram** no repositório.
- **HTTPS** (as plataformas fornecem) e **CORS restrito** ao domínio do frontend.
- **Backups** do banco e política de acesso mínimo.

---

## 7. Próximos passos imediatos

1. **Rotacionar** a senha do Postgres e do pgAdmin; remover segredos do `docker-compose` e mover para `.env`.
2. Executar a **Fase 0** (destravar a API + Alembic + conexão + CORS).
3. Aplicar o **modelo de dados revisado** na primeira migration.
4. Provisionar as contas: **Vercel/Cloudflare Pages + Render + Neon + R2**.
5. Iniciar **Fase 1 (auth + serviços)** — a base de tudo que vem depois.
