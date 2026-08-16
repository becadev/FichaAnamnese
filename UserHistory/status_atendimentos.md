# Fluxo de Status do Atendimento Estético

## Fluxo Principal

```text
┌─────────────────────┐
│    NÃO INICIADO     │
└──────────┬──────────┘
           ↓
┌─────────────────────────────┐
│   AGUARDANDO AVALIAÇÃO      │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│    AVALIAÇÃO REALIZADA      │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│   AGUARDANDO PROCEDIMENTO   │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│        EM ANDAMENTO         │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│     AGUARDANDO RETORNO      │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│     EM ACOMPANHAMENTO       │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│         FINALIZADO          │
└─────────────────────────────┘
```

## Fluxos Alternativos

```text
                         ┌──────────────┐
                         │   PAUSADO    │
                         └──────▲───────┘
                                │
                                │
                         ┌──────┴───────┐
                         │ EM ANDAMENTO │
                         └──────┬───────┘
                                │
                                ↓
                         ┌──────────────┐
                         │  CANCELADO   │
                         └──────────────┘
```

### Abandono do tratamento

```text
┌─────────────────────────┐
│   AGUARDANDO RETORNO    │
└────────────┬────────────┘
             │
             │ Cliente não retorna
             ↓
┌─────────────────────────┐
│       ABANDONADO        │
└─────────────────────────┘
```

---

# Descrição dos Status

| Status                      | Descrição                                                                           |
| --------------------------- | ----------------------------------------------------------------------------------- |
| **Não iniciado**            | Atendimento cadastrado, mas nenhuma avaliação ou procedimento foi iniciado.         |
| **Aguardando avaliação**    | Cliente aguarda a realização da anamnese e avaliação estética.                      |
| **Avaliação realizada**     | Anamnese e avaliação foram concluídas e a conduta está sendo definida/registrada.   |
| **Aguardando procedimento** | Procedimento ou tratamento foi definido, mas ainda não foi realizado.               |
| **Em andamento**            | Procedimento ou tratamento está sendo realizado.                                    |
| **Aguardando retorno**      | Uma sessão foi concluída e existe um retorno previsto.                              |
| **Em acompanhamento**       | O cliente está sendo acompanhado após uma sessão ou após a conclusão do tratamento. |
| **Pausado**                 | Tratamento temporariamente interrompido, mas ainda pode ser retomado.               |
| **Finalizado**              | Atendimento ou tratamento foi concluído e não existem ações previstas.              |
| **Cancelado**               | Atendimento cancelado antes de sua conclusão.                                       |
| **Abandonado**              | Cliente deixou de comparecer ou continuar o tratamento sem encerramento formal.     |

---

# Regras de Transição

```text
NÃO INICIADO
    └──→ AGUARDANDO AVALIAÇÃO

AGUARDANDO AVALIAÇÃO
    └──→ AVALIAÇÃO REALIZADA

AVALIAÇÃO REALIZADA
    └──→ AGUARDANDO PROCEDIMENTO

AGUARDANDO PROCEDIMENTO
    └──→ EM ANDAMENTO

EM ANDAMENTO
    ├──→ AGUARDANDO RETORNO
    ├──→ PAUSADO
    └──→ CANCELADO

AGUARDANDO RETORNO
    ├──→ EM ANDAMENTO
    ├──→ EM ACOMPANHAMENTO
    └──→ ABANDONADO

EM ACOMPANHAMENTO
    ├──→ EM ANDAMENTO
    └──→ FINALIZADO

PAUSADO
    ├──→ EM ANDAMENTO
    └──→ CANCELADO
```

## Fluxo resumido

```text
Não iniciado
      ↓
Aguardando avaliação
      ↓
Avaliação realizada
      ↓
Aguardando procedimento
      ↓
Em andamento
      ↓
Aguardando retorno
      ↓
Em acompanhamento
      ↓
Finalizado
```

**Estados de exceção:** `Pausado`, `Cancelado` e `Abandonado`.
