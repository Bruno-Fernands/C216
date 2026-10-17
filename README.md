# C216 — Sistemas Distribuídos (Lab 1)

Repositório das atividades práticas da disciplina **C216**, turma L1.

## Estrutura

| Caminho          | Descrição                                             |
| ---------------- | ----------------------------------------------------- |
| `backend/`       | Backend em Python gerenciado com Poetry (FastAPI)     |
| `Makefile`       | Automação de tarefas do projeto                       |
| `docker-compose.yml` | Orquestração dos serviços (backend + banco)       |
| `.github/workflows/ci-backend.yml` | CI: testes e build Docker                  |

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

> As tarefas são persistidas no PostgreSQL (volume `pgdata`), então
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

## Como executar

### Docker (recomendado)

```bash
make build      # constrói as imagens
make up         # sobe backend + PostgreSQL e espera ficarem saudáveis
make logs       # acompanha os logs
make down       # derruba os serviços (os dados ficam no volume pgdata)
```

Ao iniciar, o container do backend roda `alembic upgrade head` antes do
`uvicorn`, então o banco é criado/atualizado automaticamente.

### Local (sem Docker para a API)

```bash
make install    # instala as dependências do backend
make migrate    # sobe o PostgreSQL do Compose e aplica as migrations
make run        # sobe a API em http://localhost:8000
make help       # lista todos os comandos disponíveis
```

> O backend expõe a API na porta `8000` e o PostgreSQL na porta `5432`.

### Variáveis de ambiente

| Variável            | Onde é usada                 | Padrão                                                  |
| ------------------- | ---------------------------- | ------------------------------------------------------- |
| `DATABASE_URL`      | API e Alembic                | `postgresql+psycopg://c216:c216@localhost:5432/c216`   |
| `TEST_DATABASE_URL` | Testes de integração         | `postgresql+psycopg://c216:c216@localhost:5432/c216_test` |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `docker-compose.yml` | `c216` / `c216` / `c216` |

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
  Alembic).

```bash
make test               # suíte completa (sobe o PostgreSQL do Compose)
make test-unit          # apenas unitários
make test-integration   # apenas integração (sobe o PostgreSQL do Compose)
make lint               # Ruff: lint + verificação de formatação
make format             # Ruff: corrige e formata
```

A **integração contínua** roda no GitHub Actions a cada `push` e
`pull_request` (workflow `ci-backend.yml`), com jobs de lint, testes
unitários, testes de integração (com um serviço PostgreSQL) e build da
imagem Docker.

## Como contribuir

Todas as práticas são entregues via Pull Request para a branch `aulas`,
seguindo o fluxo de branches `pratica-N` → `aulas`.