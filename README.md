# C216 — Sistemas Distribuídos (Lab 1)

Repositório das atividades práticas da disciplina **C216**, turma L1.

## Estrutura

| Caminho          | Descrição                                             |
| ---------------- | ----------------------------------------------------- |
| `backend/`       | Backend em Python gerenciado com Poetry (FastAPI)     |
| `Makefile`       | Automação de tarefas do projeto                       |
| `docker-compose.yml` | Orquestração dos serviços (`db`, `api` e `frontend`) |
| `.github/workflows/ci-backend.yml` | CI: lint, testes e build das imagens Docker |
| `frontend/`      | Frontend React (Vite + Tailwind) que consome a API `/items/` |
| `.github/workflows/ci-frontend.yml` | CI: Biome, Vitest, build e E2E (Playwright + Compose) |

### Organização do backend

```
backend/
├── alembic.ini              # configuração do Alembic (URL vem de DATABASE_URL)
├── alembic/versions/        # migrations do banco
├── app/
│   ├── main.py              # apenas inicializa o FastAPI e registra os routers
│   ├── core/config.py       # configurações lidas de variáveis de ambiente
│   ├── db/                  # Base declarativa, engine e sessão do SQLAlchemy
│   ├── models/              # modelos ORM (tabelas)
│   ├── repositories/        # acesso aos dados (única camada que usa a Session)
│   ├── services/            # regras de negócio (usam os repositories)
│   ├── schemas/             # modelos Pydantic (contrato da API)
│   └── routers/             # camada HTTP (um APIRouter por grupo de endpoints)
└── tests/
    ├── unit/                # services e schemas, sem banco
    └── integration/         # endpoints e repository contra PostgreSQL
```

Fluxo de uma requisição: `router → service → repository → PostgreSQL`.
O service devolve schemas Pydantic; os modelos ORM não saem da camada de dados.

### Endpoints

| Método   | Rota                    | Descrição                                           |
| -------- | ----------------------- | --------------------------------------------------- |
| `GET`    | `/`                     | Status da API                                       |
| `GET`    | `/saudacao/{nome}`      | Saudação personalizada (path parameter)             |
| `GET`    | `/somar?a=&b=`          | Soma (query parameters)                             |
| `GET`    | `/dividir?a=&b=`        | Divisão; `400` se o divisor for zero                |
| `GET`    | `/tarefas`              | Lista tarefas; filtros `?concluida=` e `?limite=`   |
| `GET`    | `/tarefas/{tarefa_id}`  | Obtém uma tarefa; `404` se não existir              |
| `POST`   | `/tarefas`              | Cria uma tarefa (`201`)                             |
| `PUT`    | `/tarefas/{tarefa_id}`  | Substitui a tarefa inteira                          |
| `PATCH`  | `/tarefas/{tarefa_id}`  | Atualiza apenas os campos enviados                  |
| `DELETE` | `/tarefas/{tarefa_id}`  | Remove a tarefa (`204`)                             |
| `GET`    | `/items/`               | Lista os itens (usado pelo frontend)                |
| `POST`   | `/items/`               | Cria um item (`201`); `409` se o nome já existir    |

> As tarefas e os itens são persistidos no PostgreSQL (volume `pgdata`), então
> continuam lá após reiniciar a API ou os containers.
> A documentação interativa fica em `http://localhost:8000/docs`.

## Práticas

| Prática        | Resumo                                             | Status |
| -------------- | -------------------------------------------------- | ------ |
| Prática 1      | Git/GitHub, Poetry e Makefile                      | ✅ Concluída |
| Prática 2      | Dockerfile, Docker Compose e Makefile              | ✅ Concluída |
| Prática 3      | Testes com Pytest e CI com GitHub Actions          | ✅ Concluída |
| Prática 4      | Organização da API (routers/schemas/services) e CRUD de tarefas | ✅ Concluída |
| Prática 5      | PostgreSQL com SQLAlchemy, Repository, Alembic e Ruff | ✅ Concluída |
| Prática 6      | Frontend: gerenciador de itens (React, Tailwind, Biome, Vitest, Playwright) | ✅ Concluída |
| Prática 7      | Integração frontend + API (fetch, CORS, frontend no Compose, E2E com persistência) | ✅ Concluída |

## Como executar

### Docker (recomendado)

```bash
make up-build   # constrói as imagens e sobe db, api e frontend (espera ficarem healthy)
make ps         # status dos serviços (todos devem estar "healthy")
make db-upgrade # aplica as migrations dentro do container da api
make db-current # mostra a revisão atual do banco, que deve terminar em "(head)"
make logs       # acompanha os logs
make down       # derruba os serviços (os dados ficam no volume pgdata)
```

- Interface: `http://localhost:5173`
- API e documentação: `http://localhost:8000/docs`

Ao iniciar, o container da api roda `alembic upgrade head` antes do
`uvicorn`, então o banco é criado/atualizado automaticamente.

### Local (sem Docker para a API)

```bash
make install    # instala as dependências do backend
make migrate    # sobe o PostgreSQL do Compose e aplica as migrations
make run        # sobe a API em http://localhost:8000
make help       # lista todos os comandos disponíveis
```

> Portas padrão: frontend `5173`, API `8000` e PostgreSQL `5432` (variáveis `FRONTEND_PORT`, `API_PORT` e `DB_PORT`).

### Variáveis de ambiente

| Variável            | Onde é usada                 | Padrão                                                  |
| ------------------- | ---------------------------- | ------------------------------------------------------- |
| `DATABASE_URL`      | API e Alembic                | `postgresql+psycopg://c216:c216@localhost:5432/c216`   |
| `TEST_DATABASE_URL` | Testes de integração         | `postgresql+psycopg://c216:c216@localhost:5432/c216_test` |
| `CORS_ORIGINS`      | API (CORS), separadas por vírgula | `http://localhost:5173`                         |
| `VITE_API_URL`      | Build do frontend (URL da API) | `http://localhost:8000`                           |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `docker-compose.yml` | `c216` / `c216` / `c216` |
| `DB_PORT` / `API_PORT` / `FRONTEND_PORT` | `docker-compose.yml` (portas no host) | `5432` / `8000` / `5173` |

Para trocar os valores, copie `.env.example` (raiz, usado pelo Compose) ou
`backend/.env.example` (usado pela API fora do Docker) para `.env`.

### Migrations (Alembic)

```bash
make migrate                              # aplica as migrations pendentes
make migration msg="adiciona campo x"     # gera uma migration a partir dos modelos ORM
```

## Testes e lint

A suíte de testes usa o **Pytest** e é separada por tipo:

- **Testes unitários** (`backend/tests/unit/`): regras de negócio
  (`services`, com um repositório falso em memória) e modelos Pydantic
  (`schemas`). Não precisam de banco;
- **Testes de integração** (`backend/tests/integration/`): todos os endpoints
  via `TestClient` e o `TarefaRepository`, contra um **PostgreSQL real**
  (banco `c216_test`, criado automaticamente e montado com as migrations do
  Alembic). Inclui os testes de CORS (preflight da origem permitida e
  bloqueio de origem desconhecida).

```bash
make test               # suíte completa (sobe o PostgreSQL do Compose)
make test-unit          # apenas unitários
make test-integration   # apenas integração (sobe o PostgreSQL do Compose)
make lint               # Ruff: lint + verificação de formatação
make format             # Ruff: corrige e formata
```

A **integração contínua** roda no GitHub Actions a cada `push` e
`pull_request` (workflow `ci-backend.yml`), com jobs de lint, testes
unitários, testes de integração (com um serviço PostgreSQL) e build das
imagens Docker (`api` e `frontend`).

## Frontend

Gerenciador de itens (nome + descrição) em **React** com **Vite** e
**Tailwind CSS**. Os itens são lidos e gravados na API (`GET`/`POST /items/`),
com mensagens de carregamento e de erro (por exemplo, "Já existe um item com
esse nome"). No Compose, o build é servido pelo **nginx** (`frontend/Dockerfile`).

```
frontend/
├── src/
│   ├── components/ItemForm.jsx   # formulário (nome + descrição)
│   ├── components/ItemList.jsx   # listagem e estado vazio
│   ├── services/items.js         # listItems e createItem (fetch)
│   ├── App.jsx                   # carrega/cria itens, carregamento e erros
│   └── validation.js             # regras de validação (função pura)
└── tests/
    ├── unit/                     # Vitest: validação, services (fetch mockado) e componentes
    ├── integration/              # Vitest: App com fetch mockado (carregando, sucesso, erro)
    └── e2e/                      # Playwright contra a stack real (persistência após reload)
```

```bash
make front-install   # npm ci
make front-dev       # Vite em http://localhost:5173 (com a API rodando)
make frontend-check  # Biome: lint + formatação
make frontend-test   # Vitest: unitários e integração
make frontend-build  # build de produção
make e2e             # Playwright contra db + api + frontend no projeto lab-e2e
make check-all       # tudo: lint/testes do backend, frontend e E2E
```

O `make e2e` sobe uma cópia isolada da stack (projeto `lab-e2e`, portas
5174/8001/5433, banco novo), roda o Playwright e remove containers e volume
no fim, **mesmo se algum teste falhar**. Por isso dá para rodar com a stack
de desenvolvimento no ar.

## Como contribuir

Todas as práticas são entregues via Pull Request para a branch `aulas`,
seguindo o fluxo de branches `pratica-N` → `aulas`.