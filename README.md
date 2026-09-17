# C216 — Sistemas Distribuídos (Lab 1)

Repositório das atividades práticas da disciplina **C216**, turma L1.

## Estrutura

| Caminho          | Descrição                                             |
| ---------------- | ----------------------------------------------------- |
| `backend/`       | Backend em Python gerenciado com Poetry (FastAPI)     |
| `Makefile`       | Automação de tarefas do projeto                       |
| `docker-compose.yml` | Orquestração dos serviços (backend + banco)       |
| `.github/workflows/ci-backend.yml` | CI: testes e build Docker                  |

## Práticas

| Prática        | Resumo                                             | Status |
| -------------- | -------------------------------------------------- | ------ |
| Prática 1      | Git/GitHub, Poetry e Makefile                      | ✅ Concluída |
| Prática 2      | Dockerfile, Docker Compose e Makefile              | ✅ Concluída |
| Prática 3      | Testes com Pytest e CI com GitHub Actions          | ✅ Concluída |

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

A suíte de testes usa o **Pytest** (dependência de desenvolvimento) e cobre:

- **Testes unitários** (`backend/tests/test_services.py`): funções de negócio,
  com `assert`, casos de erro (`pytest.raises`), parametrização e fixtures;
- **Testes de integração** (`backend/tests/test_app.py`): endpoints da API via
  `TestClient` do FastAPI.

Para executar os testes:

```bash
make test                              # via Makefile
cd backend && poetry run pytest -v     # diretamente
```

A **integração contínua** roda automaticamente no GitHub Actions a cada
`push` e `pull_request` (workflow `ci-backend.yml`), executando:
`poetry install` → `poetry run pytest -v`, além do build da imagem Docker.

## Como contribuir

Todas as práticas são entregues via Pull Request para a branch `aulas`,
seguindo o fluxo de branches `pratica-N` → `aulas`.