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
├── app/
│   ├── main.py              # apenas inicializa o FastAPI e registra os routers
│   ├── routers/             # camada HTTP (um APIRouter por grupo de endpoints)
│   │   ├── operacoes.py
│   │   └── tarefas.py
│   ├── schemas/             # modelos Pydantic (entrada/saída)
│   │   └── tarefa.py
│   └── services/            # regras de negócio, sem dependência de HTTP
│       ├── operacoes.py
│       └── tarefas.py
└── tests/
    ├── unit/                # testes unitários (services e schemas)
    └── integration/         # testes de integração (endpoints via TestClient)
```

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

> As tarefas ficam em memória: são perdidas quando a API é reiniciada.
> A documentação interativa fica em `http://localhost:8000/docs`.

## Práticas

| Prática        | Resumo                                             | Status |
| -------------- | -------------------------------------------------- | ------ |
| Prática 1      | Git/GitHub, Poetry e Makefile                      | ✅ Concluída |
| Prática 2      | Dockerfile, Docker Compose e Makefile              | ✅ Concluída |
| Prática 3      | Testes com Pytest e CI com GitHub Actions          | ✅ Concluída |
| Prática 4      | Organização da API (routers/schemas/services) e CRUD de tarefas | ✅ Concluída |

## Como executar

### Local (sem Docker)

```bash
make install    # instala as dependências do backend
make run        # sobe a API em http://localhost:8000
make help       # lista todos os comandos disponíveis
```

### Docker

```bash
make build      # constrói as imagens
make up         # sobe backend + banco (PostgreSQL)
make logs       # acompanha os logs
make down       # derruba os serviços
```

> O backend expõe a API na porta `8000` e o PostgreSQL na porta `5432`.

## Testes

A suíte de testes usa o **Pytest** (dependência de desenvolvimento) e é
separada por tipo:

- **Testes unitários** (`backend/tests/unit/`): regras de negócio
  (`services`) e modelos Pydantic (`schemas`), sem subir a aplicação;
- **Testes de integração** (`backend/tests/integration/`): todos os endpoints
  da API via `TestClient` do FastAPI.

Para executar os testes:

```bash
make test               # suíte completa
make test-unit          # apenas unitários
make test-integration   # apenas integração
```

A **integração contínua** roda automaticamente no GitHub Actions a cada
`push` e `pull_request` (workflow `ci-backend.yml`), com um job para os
testes unitários, um para os de integração e um para o build da imagem Docker.

## Como contribuir

Todas as práticas são entregues via Pull Request para a branch `aulas`,
seguindo o fluxo de branches `pratica-N` → `aulas`.