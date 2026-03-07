# Synchro MES — Guia de Deploy

> Instruções para deploy em desenvolvimento e produção.

---

## Ambientes

| Ambiente | Backend | Banco | Frontend |
|----------|---------|-------|----------|
| **Dev** | `uvicorn --reload` | SQLite | `vite dev` |
| **Docker** | Dockerfile | PostgreSQL 16 | Dockerfile (Nginx) |
| **Produção** | Docker Compose | PostgreSQL 16 | Docker Compose |

---

## 1. Desenvolvimento Local

### Backend

```bash
cd synchro-mes/backend
python -m venv venv
venv\Scripts\activate              # Windows
# source venv/bin/activate         # Linux/Mac
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

O backend usará **SQLite** automaticamente (`synchro_mes_v2.db`).

Docs Swagger: http://localhost:8000/docs

### Frontend

```bash
cd synchro-mes/frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

### ML Service (opcional)

```bash
cd synchro-mes/ml-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

---

## 2. Docker Compose

### Subir todos os serviços

```bash
cd synchro-mes
docker compose up -d
```

### Serviços

| Serviço | Porta | Imagem |
|---------|-------|--------|
| `db` | 5432 | postgres:16-alpine |
| `backend` | 8000 | ./backend (FastAPI) |
| `ml-service` | 8001 | ./ml-service (FastAPI) |
| `frontend` | 5173 | ./frontend (Vite/Nginx) |

### Verificar status

```bash
docker compose ps
docker compose logs backend -f
docker compose logs frontend -f
```

### Rebuild após mudanças

```bash
docker compose up -d --build
```

### Parar tudo

```bash
docker compose down
```

### Remover volumes (reset do banco)

```bash
docker compose down -v
```

---

## 3. Variáveis de Ambiente

### Backend

Criar arquivo `backend/.env` ou exportar variáveis:

```env
# Banco de dados
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/synchro_mes
# DATABASE_URL=sqlite+aiosqlite:///./synchro_mes_v2.db  # Dev

# JWT
SECRET_KEY=sua-chave-secreta-aqui-mude-em-producao

# Auth
DEV_BYPASS_AUTH=True   # Desativar em produção: False

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# App
APP_NAME=Synchro MES
APP_VERSION=2.1.0
```

### Frontend

Criar arquivo `frontend/.env`:

```env
# API
VITE_API_URL=http://localhost:8000

# Firebase
VITE_FIREBASE_API_KEY=sua-api-key
VITE_FIREBASE_AUTH_DOMAIN=seu-projeto.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=seu-projeto
VITE_FIREBASE_STORAGE_BUCKET=seu-projeto.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abc123
```

---

## 4. Firebase Setup

### 4.1 Criar Projeto

1. Acesse [Firebase Console](https://console.firebase.google.com)
2. Criar novo projeto
3. Desativar Google Analytics (opcional)

### 4.2 Criar Firestore Database

1. Build → Firestore Database → Create Database
2. Selecionar "Start in **test mode**"
3. Região: `southamerica-east1` (São Paulo)

### 4.3 Registrar App Web

1. Project Settings → General → Add app → Web
2. Copiar credenciais para `frontend/.env`

### 4.4 Popular Dados

1. Iniciar o frontend
2. Acessar `http://localhost:5173/seed`
3. Clicar **"Executar Seed Completo"**
4. Aguardar: ~1500 documentos serão criados em 32 coleções

### 4.5 Regras de Segurança (Produção)

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

---

## 5. PostgreSQL (Produção)

### Via Docker (recomendado)

Já incluído no `docker-compose.yml`:

```yaml
db:
  image: postgres:16-alpine
  environment:
    POSTGRES_DB: synchro_mes
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
  ports:
    - "5432:5432"
  volumes:
    - pgdata:/var/lib/postgresql/data
```

### Instalação local

```bash
# Criar banco
createdb synchro_mes

# Configurar URL
export DATABASE_URL=postgresql+asyncpg://postgres:senha@localhost:5432/synchro_mes
```

### Migrações com Alembic

```bash
cd backend

# Gerar migração a partir dos modelos
alembic revision --autogenerate -m "descrição da mudança"

# Aplicar migrações
alembic upgrade head

# Reverter última migração
alembic downgrade -1

# Ver histórico
alembic history
```

---

## 6. Checklist de Produção

### Segurança

- [ ] `DEV_BYPASS_AUTH=False`
- [ ] `SECRET_KEY` com valor forte (32+ caracteres aleatórios)
- [ ] CORS restrito aos domínios autorizados
- [ ] Firestore rules com autenticação
- [ ] HTTPS habilitado

### Performance

- [ ] PostgreSQL em vez de SQLite
- [ ] Frontend com build de produção (`npm run build`)
- [ ] Nginx como reverse proxy
- [ ] Uvicorn com múltiplos workers: `uvicorn app.main:app --workers 4`

### Monitoramento

- [ ] Logs de auditoria habilitados (automático via middleware)
- [ ] Health check: `GET /health`
- [ ] Docker health checks configurados

---

## 7. Nginx (Reverse Proxy)

Configuração de exemplo para servir frontend + proxy backend:

```nginx
server {
    listen 80;
    server_name meu-dominio.com;

    # Frontend (SPA)
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Health
    location /health {
        proxy_pass http://backend:8000;
    }

    # ML Service
    location /predictions/ {
        proxy_pass http://ml-service:8001;
    }
    location /ml/ {
        proxy_pass http://ml-service:8001;
    }
}
```

---

## 8. Estrutura Docker Compose

```yaml
version: "3.8"

services:
  db:
    image: postgres:16-alpine
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [db]
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/synchro_mes

  ml-service:
    build: ./ml-service
    ports: ["8001:8001"]

  frontend:
    build: ./frontend
    ports: ["5173:80"]
    depends_on: [backend]

volumes:
  pgdata:
```
