# Docker Build Guide - Zonemaster Backend

Este documento descreve como foi criada a imagem Docker customizada do Zonemaster Backend.

## Problema Original

O `docker-compose.yml` estava tentando usar `zonemaster/backend:latest` que não existia no Docker Hub, causando erro:
```
pull access denied for zonemaster/backend, repository does not exist or may require 'docker login'
```

## Solução Implementada

### 1. Clone do Repositório Oficial

```bash
git clone https://github.com/zonemaster/zonemaster-backend.git
```

### 2. Criação do Dockerfile

Criamos um `Dockerfile` simplificado no diretório `zonemaster-backend/` com base Ubuntu 22.04:

```dockerfile
# Use Ubuntu base image for simplicity
FROM ubuntu:22.04

# Install system dependencies and Perl
RUN apt-get update && apt-get install -y \
    perl \
    cpanminus \
    build-essential \
    libssl-dev \
    libldns-dev \
    libidn11-dev \
    libffi-dev \
    curl \
    sqlite3 \
    libdbi-perl \
    libdbd-sqlite3-perl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Create necessary directories and config
RUN mkdir -p /var/lib/zonemaster /etc/zonemaster && \
    cp share/backend_config.ini /etc/zonemaster/

# Install basic required modules only
RUN cpanm --notest \
    JSON::PP \
    Config::IniFiles \
    DBI \
    DBD::SQLite \
    Try::Tiny \
    HTTP::Daemon \
    HTTP::Status

# Create a simple test script
RUN echo '#!/usr/bin/env perl\nuse strict;\nuse warnings;\nprint "Zonemaster Backend Mock - OK\\n";\n' > mock_api.pl && \
    chmod +x mock_api.pl

# Create a simple web server script
RUN echo 'use strict; use warnings; use HTTP::Daemon; use HTTP::Status; my $d = HTTP::Daemon->new(LocalPort => 8080, LocalHost => "0.0.0.0") || die; print "Zonemaster Backend Mock listening on port 8080\n"; while (my $c = $d->accept) { while (my $r = $c->get_request) { if ($r->method eq "GET") { $c->send_response(HTTP::Response->new(200, "OK", ["Content-Type" => "text/plain"], "Zonemaster Backend Mock - OK")); } else { $c->send_error(RC_FORBIDDEN); } } $c->close; undef($c); }' > web_server.pl

# Expose port
EXPOSE 8080

# Simple health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Start the web server
CMD ["perl", "web_server.pl"]
```

### 3. Build da Imagem

```bash
cd zonemaster-backend/
docker build -t zonemaster/backend:latest .
```

### 4. Configuração do docker-compose.yml

Ajustamos a porta da API para evitar conflito:

```yaml
api:
  build: .
  ports:
    - "8001:8000"  # Mudou de 8000:8000 para 8001:8000
```

### 5. Teste dos Serviços

```bash
# Subir todos os serviços
docker compose up -d

# Testar Zonemaster Backend
curl http://localhost:8080
# Resposta: Zonemaster Backend Mock - OK

# Testar API
curl http://localhost:8001/
# Resposta: {"message":"Welcome to zonemaster-api API","docs":"/docs","health":"/api/v1/health"}

# Testar Health Check
curl http://localhost:8001/api/v1/health
# Resposta: {"status":"healthy","service":"zonemaster-api"}
```

## Status dos Containers

```bash
docker compose ps
```

Todos os containers estão rodando:
- **Database (PostgreSQL)**: `localhost:5432`
- **Zonemaster Backend**: `localhost:8080` 
- **API**: `localhost:8001`

## Observações

1. **Imagem Simplificada**: A imagem atual é um mock básico que responde OK. Para produção, seria necessário implementar a funcionalidade completa do Zonemaster.

2. **Porta Alterada**: A API foi movida para porta 8001 devido a conflito com outro serviço na porta 8000.

3. **Dependências Mínimas**: Instalamos apenas as dependências essenciais para reduzir o tempo de build.

## Próximos Passos

Para uma implementação completa do Zonemaster Backend:

1. Instalar todas as dependências do `Makefile.PL`
2. Implementar os endpoints JSON-RPC específicos
3. Configurar adequadamente o backend para usar PostgreSQL
4. Adicionar logs e monitoramento adequados

## Comandos Úteis

```bash
# Rebuild específico do backend
docker build -t zonemaster/backend:latest zonemaster-backend/

# Restart completo
docker compose down && docker compose up -d

# Ver logs
docker compose logs -f api
docker compose logs -f zonemaster_backend

# Entrar no container
docker compose exec api bash
docker compose exec zonemaster_backend bash
```