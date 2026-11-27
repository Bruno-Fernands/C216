# Controle de Estoque — Projeto Final C216

Projeto Final da disciplina **C216 — Sistemas Distribuídos** (turma L1).

🎬 **Vídeo demonstrativo:** _link a adicionar_

## Objetivo e tema

Aplicação web para **controle de estoque** de um pequeno comércio. O problema
resolvido: saber quanto há de cada produto, registrar o que entra e o que sai
com histórico, e ser avisado quando um produto está acabando.

A regra central é que **o saldo de um produto nunca é editado à mão**: ele só
muda por **movimentações** (entradas e saídas), e uma saída maior que o saldo
disponível é recusada. Assim o saldo sempre bate com o histórico.

## Funcionalidades

- **Produtos (CRUD completo pela interface):** cadastrar, listar, editar e
  excluir. Cada produto tem nome (único, sem diferenciar maiúsculas),
  descrição opcional, preço e estoque mínimo. Todo produto começa com saldo zero.
- **Movimentações:** registrar entradas e saídas com quantidade e observação;
  o saldo é atualizado na mesma transação. Uma saída maior que o saldo
  responde **409** e não grava nada. A linha do produto é travada
  (`SELECT ... FOR UPDATE`) para que duas saídas simultâneas não usem o mesmo
  saldo, e o banco tem um `CHECK (quantidade >= 0)` como garantia final.
- **Histórico** de movimentações por produto (mais recente primeiro).
- **Alerta de estoque baixo:** produtos com saldo abaixo do mínimo recebem
  um selo, e a lista pode ser filtrada só por eles.
- **Busca por nome** na listagem.
- **Resumo do estoque:** total de produtos, unidades, valor em estoque
  (saldo × preço) e quantidade de produtos abaixo do mínimo.
- **Excluir um produto** pede confirmação e apaga também seu histórico
  (cascata no banco).
- Estados de **carregamento, sucesso e erro** na interface, com as mensagens
  de negócio vindas da API (ex.: nome repetido, estoque insuficiente).

## Tecnologias

| Parte          | Tecnologias |
| -------------- | ----------- |
| Backend        | Python 3.12, FastAPI, Pydantic, SQLAlchemy 2, Alembic, Poetry, Ruff |
| Banco de dados | PostgreSQL 16 |
| Frontend       | React 19 (JavaScript), Vite, Tailwind CSS, Biome |
| Testes         | Pytest (unitários + integração com PostgreSQL), Vitest + Testing Library, Playwright (E2E) |
| Infraestrutura | Docker, Docker Compose, nginx (serve o build do frontend), Makefile, GitHub Actions |

## Arquitetura

```
Navegador ──HTTP/JSON──▶ frontend (nginx :5173)      React: páginas e chamadas fetch
    │
    └──────HTTP/JSON──▶ api (FastAPI :8000)          CORS liberado só para a origem do frontend
                              │
                              ▼
                        db (PostgreSQL :5432)        volume pgdata (dados persistem)
```

O navegador carrega o frontend do nginx e chama a API diretamente (por isso
a API configura **CORS** para a origem do frontend, com os métodos
`GET, POST, PUT, DELETE`). Ao iniciar, o container da API roda
`alembic upgrade head` e depois o `uvicorn`, então o banco é criado e
atualizado automaticamente.

Dentro do backend, cada requisição segue
`router → service → repository → PostgreSQL`:

- **routers** (`app/routers/`): camada HTTP; converte erros de negócio em 404/409.
- **services** (`app/services/`): regras de negócio (nome único, saldo
  suficiente etc.); não conhecem HTTP nem SQL.
- **repositories** (`app/repositories/`): única camada que usa a `Session` do SQLAlchemy.
- **schemas** (`app/schemas/`): contrato da API (Pydantic), com validação.
- **models** (`app/models/`): tabelas ORM.

### Estrutura resumida

```
.
├── docker-compose.yml        # db + api + frontend
├── Makefile                  # comandos de execução, testes e manutenção
├── .env.example              # variáveis do Compose (copiar para .env)
├── .github/workflows/        # ci-backend.yml e ci-frontend.yml
├── backend/
│   ├── Dockerfile
│   ├── .env.example          # variáveis da API fora do Docker
│   ├── alembic/versions/     # migrations versionadas
│   ├── app/
│   │   ├── main.py           # cria o FastAPI, CORS e routers
│   │   ├── core/config.py    # configurações via variáveis de ambiente
│   │   ├── db/               # Base, engine e sessão
│   │   ├── models/produto.py
│   │   ├── schemas/produto.py
│   │   ├── repositories/produto_repository.py
│   │   ├── services/produtos.py
│   │   └── routers/produtos.py
│   └── tests/
│       ├── unit/             # regras de negócio com repositório falso (sem banco)
│       └── integration/      # endpoints contra PostgreSQL real
└── frontend/
    ├── Dockerfile            # build com Node, servido pelo nginx
    ├── src/
    │   ├── App.jsx           # estado da tela, filtros e ações
    │   ├── components/       # ProdutoForm, ProdutoList, MovimentacaoPanel, ResumoCards, Campo
    │   ├── services/produtos.js  # chamadas HTTP à API
    │   └── validation.js     # validação dos formulários
    └── tests/
        ├── unit/             # validação, serviço HTTP e componentes
        ├── integration/      # App com a API mockada
        └── e2e/              # Playwright contra a stack completa
```

### Endpoints

| Método   | Rota                                  | Descrição |
| -------- | ------------------------------------- | --------- |
| `GET`    | `/`                                   | Status da API (healthcheck) |
| `GET`    | `/produtos?busca=&abaixo_do_minimo=`  | Lista em ordem alfabética, com busca e filtro opcionais |
| `GET`    | `/produtos/resumo`                    | Totais do estoque |
| `GET`    | `/produtos/{id}`                      | Obtém um produto (`404` se não existir) |
| `POST`   | `/produtos`                           | Cadastra (`201`); `409` se o nome já existir |
| `PUT`    | `/produtos/{id}`                      | Edita dados cadastrais (o saldo não muda por aqui) |
| `DELETE` | `/produtos/{id}`                      | Exclui o produto e seu histórico (`204`) |
| `GET`    | `/produtos/{id}/movimentacoes`        | Histórico do produto |
| `POST`   | `/produtos/{id}/movimentacoes`        | Registra entrada/saída (`201`); `409` se faltar saldo |

Dados inválidos (nome curto, preço negativo, quantidade zero, tipo
desconhecido etc.) respondem **422**. Documentação interativa em
`http://localhost:8000/docs`.

## Pré-requisitos

- **Docker** com o plugin **Docker Compose** e **make** — suficiente para rodar a aplicação.
- Para rodar testes e lint fora do Docker: **Python 3.12** com **Poetry 2**
  e **Node.js 22** com npm.

## Variáveis de ambiente

Nenhum segredo real é versionado. Os valores abaixo são padrões de
desenvolvimento; para trocá-los, copie `.env.example` para `.env` (raiz, lido
pelo Compose) ou `backend/.env.example` para `backend/.env` (API fora do Docker).

| Variável            | Onde é usada                 | Padrão |
| ------------------- | ---------------------------- | ------ |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `docker-compose.yml` | `c216` / `c216` / `c216` |
| `DB_PORT` / `API_PORT` / `FRONTEND_PORT` | Portas publicadas no host | `5432` / `8000` / `5173` |
| `DATABASE_URL`      | API e Alembic                | `postgresql+psycopg://c216:c216@localhost:5432/c216` (no Compose aponta para o serviço `db`) |
| `CORS_ORIGINS`      | API (origens liberadas, separadas por vírgula) | `http://localhost:5173` |
| `VITE_API_URL`      | Build do frontend (URL da API vista pelo navegador) | `http://localhost:8000` |
| `TEST_DATABASE_URL` | Testes de integração do backend | `postgresql+psycopg://c216:c216@localhost:5432/c216_test` |

## Como executar

```bash
cp .env.example .env   # opcional: sem .env, o Compose usa os mesmos padrões
make up-build          # constrói as imagens e sobe db, api e frontend (espera ficarem healthy)
make ps                # os três serviços devem aparecer como "healthy"
```

Acesse:

- **Aplicação:** http://localhost:5173
- **API / documentação:** http://localhost:8000/docs

Outros comandos:

```bash
make logs   # acompanha os logs
make down   # derruba os serviços (os dados continuam no volume pgdata)
make clean  # derruba, apaga o volume (zera o banco), .venv, node_modules e dist
make help   # lista todos os comandos
```

Para rodar a API fora do Docker (com o PostgreSQL do Compose):

```bash
make install   # dependências do backend (Poetry)
make migrate   # sobe o PostgreSQL e aplica as migrations
make run       # API em http://localhost:8000
make front-install && make front-dev   # frontend em http://localhost:5173
```

## Migrações (Alembic)

As migrations ficam em `backend/alembic/versions/` e são aplicadas
automaticamente quando o container da API inicia.

```bash
make db-current                       # revisão atual do banco no container (deve terminar em "(head)")
make db-upgrade                       # aplica as migrations dentro do container da api
make migrate                          # aplica as migrations a partir do host
make migration msg="descricao"        # gera uma nova migration a partir dos modelos ORM
```

A migration do domínio (`..._estoque_produtos_e_movimentacoes_...`) cria as
tabelas `produtos` e `movimentacoes` e remove as tabelas do laboratório das
práticas, que vieram antes no histórico.

## Testes

```bash
# Backend (Pytest)
make test               # unitários + integração (sobe o PostgreSQL; usa o banco c216_test)
make test-unit          # só regras de negócio, sem banco
make test-integration   # só endpoints contra PostgreSQL
make lint               # Ruff: lint + formatação

# Frontend
make front-install      # npm ci
make frontend-test      # Vitest + Testing Library
make frontend-check     # Biome: lint + formatação
make frontend-build     # build de produção

# E2E (Playwright: navegador → frontend → API → PostgreSQL)
(cd frontend && npx playwright install chromium)   # só na primeira vez
make e2e

# Tudo de uma vez
make check-all
```

O que cada suíte cobre:

- **Backend unitário:** saldo inicial zero, nome único sem diferenciar
  maiúsculas (também ao editar), saída maior que o saldo recusada sem gravar,
  estoque mínimo e validações dos schemas.
- **Backend integração:** CRUD completo, respostas 404/409/422, busca e filtro,
  histórico, cascata ao excluir, resumo e CORS.
- **Frontend (Vitest):** validação, serviço HTTP (URLs, métodos, 204, erros),
  componentes e fluxos do App com a API mockada (cadastrar, editar, excluir,
  movimentar, erro de estoque insuficiente).
- **E2E (Playwright, desktop e mobile):** cadastra um produto, registra
  entrada e saída, **recarrega a página e confere que saldo e histórico
  continuam lá**; saída sem saldo; edição e exclusão; busca; layout responsivo.

O `make e2e` sobe uma cópia isolada da stack (projeto `estoque-e2e`, portas
5174/8001/5433, banco novo), roda o Playwright e remove tudo no fim, mesmo se
algum teste falhar — dá para rodar com a stack de desenvolvimento no ar.

## Integração contínua

O GitHub Actions roda em todo `push` e `pull_request`:

- **CI - Backend** (`ci-backend.yml`): Ruff, testes unitários, testes de
  integração com um serviço PostgreSQL e build das imagens Docker.
- **CI - Frontend** (`ci-frontend.yml`): Biome, Vitest, build e o E2E com
  Playwright contra a stack do Compose.

## Histórico

O projeto partiu da base construída nas práticas 1 a 7 (estrutura em camadas,
Compose, CI) e evoluiu na branch `projeto-final` para o domínio de estoque.
A entrega é o Pull Request `projeto-final → main`.
