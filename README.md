# 🌐 Zonemaster API - DNS Health Check Service

Um serviço backend completo em **FastAPI** para verificação automática de saúde de configurações DNS, integrado diretamente com a API do **Zonemaster Backend** via JSON-RPC 2.0.

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://sqlalchemy.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docker.com)

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Arquitetura](#-arquitetura)
- [Recursos](#-recursos)
- [Início Rápido](#-início-rápido)
- [Desenvolvimento](#-desenvolvimento)
- [API Reference](#-api-reference)
- [Testes](#-testes)
- [Deployment](#-deployment)
- [Contribuição](#-contribuição)

## 🎯 Visão Geral

O **Zonemaster API** é um serviço moderno que automatiza verificações de saúde DNS através da integração direta com o [Zonemaster Backend](https://github.com/zonemaster/zonemaster-backend). Em vez de executar comandos CLI, o serviço atua como cliente direto da API Zonemaster, oferecendo:

- **Comunicação robusta** via JSON-RPC 2.0
- **Resultados estruturados** em formato JSON nativo
- **Armazenamento histórico** para análise temporal
- **API REST moderna** com documentação automática
- **Processamento assíncrono** para alta performance

## 🏗️ Arquitetura

### Stack Tecnológico

| Componente | Tecnologia | Versão |
|------------|------------|--------|
| **Backend** | FastAPI | 0.115+ |
| **Database** | PostgreSQL / SQLite | 15+ / 3.8+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **HTTP Client** | HTTPX | 0.28+ |
| **Migration** | Alembic | 1.16+ |
| **Container** | Docker Compose | 3.8+ |

### Arquitetura de Camadas

```
┌─────────────────┐
│   API Layer    │  FastAPI Endpoints + OpenAPI Docs
├─────────────────┤
│ Service Layer   │  Zonemaster Integration + Business Logic  
├─────────────────┤
│   CRUD Layer    │  Database Operations + Async Sessions
├─────────────────┤
│  Model Layer    │  SQLAlchemy Models + Relationships
├─────────────────┤
│ Database Layer  │  PostgreSQL + Alembic Migrations
└─────────────────┘
```

### Estrutura do Projeto

```
zonemaster-api/
├── app/
│   ├── main.py                    # FastAPI app + lifespan events
│   ├── core/
│   │   └── config.py             # Settings + environment config
│   ├── db/
│   │   ├── base.py               # SQLAlchemy declarative base
│   │   └── session.py            # Async database sessions
│   ├── models/
│   │   ├── dns_check.py          # DNSCheck model
│   │   └── dns_result.py         # DNSResult model
│   ├── schemas/
│   │   └── dns_check.py          # Pydantic request/response schemas
│   ├── crud/
│   │   ├── dns_check.py          # DNSCheck CRUD operations
│   │   └── dns_result.py         # DNSResult CRUD operations
│   ├── services/
│   │   └── zonemaster_service.py # Zonemaster API integration
│   └── api/
│       ├── health.py             # Health check endpoint
│       └── v1/
│           ├── api.py            # Main API router
│           └── endpoints/
│               └── dns_check.py  # DNS check endpoints
├── tests/                        # Test suite with mocking
├── alembic/                      # Database migrations
├── docker-compose.yml            # Full stack orchestration
└── pyproject.toml               # Dependencies + project config
```

## ✨ Recursos

### 🔍 Verificação de DNS
- **Análise completa** via Zonemaster Backend
- **Resultados estruturados** por módulo (NAMESERVER, DELEGATION, etc.)
- **Níveis de criticidade** (INFO, WARNING, ERROR)
- **Timeouts configuráveis** (5 minutos default)

### 💾 Persistência de Dados
- **Histórico completo** de verificações
- **Relacionamentos otimizados** entre checks e resultados
- **Consultas com paginação** para performance
- **Migrações automáticas** com Alembic

### 🚀 API Moderna
- **OpenAPI/Swagger** documentação automática
- **Validação automática** com Pydantic
- **Tratamento de erros** padronizado
- **CORS configurado** para integração frontend

### 🐳 DevOps Ready
- **Docker Compose** stack completa
- **Health checks** para todos os serviços
- **Hot reload** para desenvolvimento
- **Ambiente isolado** com volumes persistentes

## 🚀 Início Rápido

### Pré-requisitos

- **Python 3.13+**
- **UV** (gerenciador de dependências)
- **Docker** + **Docker Compose**

### 1. Instalação

```bash
# Clone o repositório
git clone <repository-url>
cd zonemaster-api

# Instalar dependências
uv sync
```

### 2. Configuração

```bash
# Copiar e ajustar variáveis de ambiente
cp .env.example .env

# Editar configurações conforme necessário
vim .env
```

**Principais configurações**:
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dns_health

# Zonemaster API
ZONEMASTER_API_URL=http://localhost:8080/RPC2
ZONEMASTER_API_TIMEOUT=300

# Debug
DEBUG=true
```

### 3. Executar Stack Completa

```bash
# Subir todos os serviços
docker compose up -d

# Verificar status
docker compose ps
```

Serviços disponíveis:
- **API**: http://localhost:8001
- **Documentação**: http://localhost:8001/docs
- **PostgreSQL**: localhost:5432
- **Zonemaster Backend**: localhost:8080

### 4. Executar Desenvolvimento Local

```bash
# Executar migrações
uv run alembic upgrade head

# Iniciar servidor de desenvolvimento
uv run uvicorn app.main:app --reload

# Acessar documentação
open http://localhost:8001/docs
```

## 🛠️ Desenvolvimento

### Comandos Úteis

```bash
# Instalar dependências de desenvolvimento
uv sync --group dev

# Executar testes
uv run pytest

# Executar testes com coverage
uv run pytest --cov=app

# Linting e formatação
uv run ruff check
uv run ruff format

# Type checking
uv run mypy app/

# Executar pre-commit hooks
uv run pre-commit run --all-files
```

### Database Operations

```bash
# Criar nova migração
uv run alembic revision --autogenerate -m "Description"

# Aplicar migrações
uv run alembic upgrade head

# Reverter migração
uv run alembic downgrade -1

# Ver histórico
uv run alembic history
```

### Debug e Logs

```bash
# Logs do container API
docker compose logs -f api

# Logs do Zonemaster
docker compose logs -f zonemaster_backend

# Logs do banco
docker compose logs -f db
```

## 📚 API Reference

### Base URL
```
http://localhost:8001/api/v1
```

### Endpoints

#### 🔍 Criar Verificação DNS
```http
POST /checks/
Content-Type: application/json

{
  "domain": "google.com"
}
```

**Resposta (201 Created)**:
```json
{
  "id": 1,
  "domain": "google.com",
  "created_at": "2025-06-29T13:58:48.347015Z",
  "results": [
    {
      "id": 1,
      "level": "INFO",
      "module": "BASIC",
      "tag": "DNS_QUERY_CHILD_STARTED",
      "message": "DNS query to child nameserver was started."
    },
    {
      "id": 2,
      "level": "INFO",
      "module": "CONNECTIVITY",
      "tag": "IPV4_OK",
      "message": "IPv4 connectivity is working."
    },
    {
      "id": 3,
      "level": "INFO",
      "module": "CONSISTENCY",
      "tag": "NAMES_MATCH",
      "message": "All nameserver names are listed at the parent."
    }
  ]
}
```

#### 📊 Obter Verificação Específica
```http
GET /checks/{check_id}
```

**Resposta (200 OK)**: Same as POST response

#### 📋 Listar Verificações
```http
GET /checks/?skip=0&limit=100
```

**Resposta (200 OK)**:
```json
[
  {
    "id": 1,
    "domain": "google.com",
    "created_at": "2025-06-29T13:58:48.347015Z",
    "results_count": 3
  }
]
```

#### 💚 Health Check
```http
GET /health
```

**Resposta (200 OK)**:
```json
{
  "status": "healthy",
  "service": "zonemaster-api"
}
```

### Códigos de Status

| Status | Descrição |
|--------|-----------|
| **200** | Sucesso |
| **201** | Verificação criada |
| **404** | Verificação não encontrada |
| **422** | Erro de validação |
| **503** | Zonemaster API indisponível |

### Exemplos Práticos

#### cURL
```bash
# Criar verificação
curl -X POST http://localhost:8001/api/v1/checks/ \
  -H "Content-Type: application/json" \
  -d '{"domain": "google.com"}'

# Listar verificações
curl http://localhost:8001/api/v1/checks/

# Obter verificação específica
curl http://localhost:8001/api/v1/checks/1
```

#### Python
```python
import httpx

async with httpx.AsyncClient() as client:
    # Criar verificação
    response = await client.post(
        "http://localhost:8001/api/v1/checks/",
        json={"domain": "google.com"}
    )
    check = response.json()
    
    # Obter resultados
    response = await client.get(f"http://localhost:8001/api/v1/checks/{check['id']}")
    results = response.json()
    
    print(f"Verificação para {results['domain']} concluída!")
    print(f"Total de resultados: {len(results['results'])}")
```

### 🌐 Exemplo Completo com google.com

Como o google.com possui uma infraestrutura DNS robusta e sempre disponível, é o exemplo perfeito para testar a API:

```bash
# 1. Criar verificação DNS para google.com
curl -X POST http://localhost:8001/api/v1/checks/ \
  -H "Content-Type: application/json" \
  -d '{"domain": "google.com"}'

# Resposta esperada:
# {
#   "id": 1,
#   "domain": "google.com",
#   "created_at": "2025-06-29T13:58:48.347015Z",
#   "results": [
#     {
#       "id": 1,
#       "level": "INFO",
#       "module": "BASIC",
#       "tag": "DNS_QUERY_CHILD_STARTED",
#       "message": "DNS query to child nameserver was started."
#     },
#     {
#       "id": 2,
#       "level": "INFO",
#       "module": "CONNECTIVITY", 
#       "tag": "IPV4_OK",
#       "message": "IPv4 connectivity is working."
#     },
#     {
#       "id": 3,
#       "level": "INFO",
#       "module": "CONSISTENCY",
#       "tag": "NAMES_MATCH", 
#       "message": "All nameserver names are listed at the parent."
#     }
#   ]
# }

# 2. Recuperar verificação específica
curl http://localhost:8001/api/v1/checks/1

# 3. Listar todas as verificações
curl http://localhost:8001/api/v1/checks/

# 4. Testar com paginação
curl "http://localhost:8001/api/v1/checks/?limit=10&offset=0"
```

**Por que google.com é ideal para testes:**
- ✅ **Sempre disponível** - Infrastructure DNS robusta 
- ✅ **Resposta consistente** - Resultados previsíveis
- ✅ **Rápido** - Análise completa em < 1 segundo
- ✅ **Universalmente conhecido** - Fácil de lembrar e usar

## 🧪 Testes

O projeto inclui uma suíte abrangente de testes com **mocking da API Zonemaster**.

### Executar Testes

```bash
# Todos os testes
uv run pytest

# Testes específicos
uv run pytest tests/api/v1/test_dns_check.py

# Com verbose e coverage
uv run pytest -v --cov=app --cov-report=html
```

### Estrutura de Testes

- **Unit Tests**: Testes de modelos e CRUD
- **Integration Tests**: Testes de API com mock HTTP
- **Fixtures**: Database setup com SQLite em memória
- **Mocking**: pytest-httpx para simular Zonemaster API

### Cenários Testados

- ✅ **Caminho feliz**: Criação bem-sucedida com resultados
- ✅ **API indisponível**: Connection error → HTTP 503
- ✅ **Erro da API**: JSON-RPC error response
- ✅ **Validação**: Entrada inválida → HTTP 422
- ✅ **Paginação**: Skip/limit funcionando
- ✅ **Not found**: ID inexistente → HTTP 404

## 🚀 Deployment

### Docker Production

1. **Build da imagem**:
```bash
docker build -t zonemaster-api .
```

2. **Run com variáveis de produção**:
```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@db/dns_health \
  -e ZONEMASTER_API_URL=http://zonemaster:8080/RPC2 \
  zonemaster-api
```

### Environment Variables

| Variável | Descrição | Default |
|----------|-----------|---------|
| `DATABASE_URL` | Connection string async | `sqlite+aiosqlite:///./app.db` |
| `DATABASE_URL_SYNC` | Connection string sync (migrations) | `sqlite:///./app.db` |
| `ZONEMASTER_API_URL` | Zonemaster Backend URL | `http://localhost:8080/RPC2` |
| `ZONEMASTER_API_TIMEOUT` | Timeout em segundos | `300` |
| `DEBUG` | Debug mode | `false` |
| `SECRET_KEY` | JWT secret key | `auto-generated` |

### Health Checks

```bash
# Container health
curl http://localhost:8001/api/v1/health

# Database connectivity
docker compose exec api uv run alembic current

# Zonemaster connectivity  
curl http://localhost:8080/
```

## 🤝 Contribuição

### Workflow de Desenvolvimento

1. **Fork** e **clone** o repositório
2. **Criar branch** feature: `git checkout -b feature/nova-funcionalidade`
3. **Desenvolver** seguindo os padrões do projeto
4. **Executar testes**: `uv run pytest`
5. **Commit** seguindo [Conventional Commits](https://conventionalcommits.org/)
6. **Push** e criar **Pull Request**

### Padrões de Código

- **Python 3.13+** com type hints
- **Ruff** para linting e formatação
- **SQLAlchemy 2.0** async patterns
- **Pydantic V2** para validação
- **Conventional Commits** para mensagens

### Estrutura de Commit

```
feat: add new DNS validation endpoint
fix: resolve database connection timeout
docs: update API documentation
test: add integration tests for error handling
```

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- [Zonemaster Project](https://github.com/zonemaster) - Ferramenta de análise DNS
- [FastAPI](https://fastapi.tiangolo.com) - Framework web moderno
- [SQLAlchemy](https://sqlalchemy.org) - ORM Python
- [UV](https://github.com/astral-sh/uv) - Gerenciador de dependências

---

**🌐 Feito com ❤️ para a comunidade DNS**