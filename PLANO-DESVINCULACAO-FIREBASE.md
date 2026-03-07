# Plano de Ação — Desvinculação do Firebase para Portfólio

> **Objetivo:** Transformar este projeto em uma versão independente para portfólio pessoal no GitHub, com dados fictícios, sem nenhuma conexão com o Firebase do projeto original (`hokkaido-synchro`).

> **Premissa fundamental:** Nenhuma alteração será feita no projeto original. Este plano se aplica **exclusivamente** a esta cópia independente.

---

## 📋 Diagnóstico Atual

| Dimensão | Situação |
|----------|----------|
| **Serviços Firebase ativos** | Auth, Firestore (30+ coleções), Storage (mínimo), Hosting |
| **SDK utilizado** | v8.10.1 (CDN) + v9.22.0 compat em páginas auxiliares |
| **Arquivos com dependência Firebase** | **46 arquivos** |
| **Config hardcoded** | 4 arquivos (script.js, login.html, dashboard-tv.html, acompanhamento-turno.html) |
| **CI/CD** | GitHub Actions → Firebase Hosting |
| **Listeners real-time (onSnapshot)** | 2 (active_downtimes, pcp_messages) |
| **Dependência npm** | firebase-admin ^13.7.0 |

---

## 🔒 Medidas de Segurança (ANTES de qualquer alteração)

| # | Ação | Prioridade |
|---|------|------------|
| 1 | **Confirmar que este workspace é uma CÓPIA separada** e não o repositório original | CRÍTICA |
| 2 | **Remover o remote `origin`** do git (se apontar para o repo original) | CRÍTICA |
| 3 | **Remover credenciais Firebase** (API key, project ID) do código antes de qualquer push ao GitHub | CRÍTICA |
| 4 | **Adicionar `.firebaserc`, `.github/workflows/firebase-deploy.yml` ao `.gitignore`** | ALTA |
| 5 | **Remover secrets do GitHub Actions** (o novo repo não terá `FIREBASE_SERVICE_ACCOUNT_HOKKAIDO_SYNCHRO`) | ALTA |

---

## 🏗️ Fases do Plano de Ação

### FASE 1 — Isolamento e Limpeza (Segurança)
**Risco: ZERO para o projeto original se executado nesta cópia**

| # | Tarefa | Arquivos Afetados | Detalhes |
|---|--------|--------------------|----------|
| 1.1 | Remover/substituir todas as API keys e credenciais Firebase hardcoded | `script.js`, `login.html`, `dashboard-tv.html`, `acompanhamento-turno.html` | Substituir por placeholders ou config mock |
| 1.2 | Remover `firebase.json` e `.firebaserc` | Raiz do projeto | Não são mais necessários |
| 1.3 | Remover workflow de deploy Firebase | `.github/workflows/firebase-deploy.yml` | Substituir por workflow de GitHub Pages (se desejado) |
| 1.4 | Remover `firebase-admin` do `package.json` | `package.json` | Não será usado |
| 1.5 | Criar `.gitignore` robusto | Raiz | Garantir que nenhuma credencial vaze |
| 1.6 | Criar novo repositório Git limpo | — | `git init` novo, sem histórico do original |

---

### FASE 2 — Camada de Dados Mock (Substituir Firestore)
**Estratégia: Criar uma camada de abstração que simula o Firestore com dados em memória/localStorage**

| # | Tarefa | Detalhes |
|---|--------|----------|
| 2.1 | **Criar `mock-database.js`** | Arquivo central com todos os dados fictícios (JSON em memória) |
| 2.2 | **Criar `mock-firebase.js`** | Objeto que simula a API do `firebase.firestore()` — métodos: `collection()`, `doc()`, `get()`, `set()`, `add()`, `update()`, `delete()`, `where()`, `orderBy()`, `limit()`, `onSnapshot()`, `batch()`, `runTransaction()` |
| 2.3 | **Criar `mock-auth.js`** | Simula `firebase.auth()` — `signInWithEmailAndPassword()`, `onAuthStateChanged()`, `signOut()`, `getIdTokenResult()` com usuários fictícios |
| 2.4 | **Substituir inicialização do Firebase** | Em vez de `firebase.initializeApp(config)`, carregar o mock |
| 2.5 | **Remover CDNs do Firebase** | Remover `<script src="firebase-*.js">` dos HTMLs |

#### Estrutura proposta do Mock:

```
src/
  mock/
    mock-database.js       ← Dados fictícios (30+ coleções)
    mock-firebase.js        ← Simula firebase.firestore() API
    mock-auth.js            ← Simula firebase.auth() API
    mock-storage.js         ← Simula firebase.storage() (se necessário)
    seed-data/
      production-orders.js  ← Dados de ordens de produção
      planning.js           ← Dados de planejamento
      machines.js           ← Dados de máquinas
      downtimes.js          ← Dados de paradas
      operators.js          ← Dados de operadores
      quality.js            ← Dados de qualidade/SPC
      ...
```

---

### FASE 3 — Dados Fictícios Realistas
**Criar dados que demonstrem as funcionalidades do sistema**

| Coleção | Quantidade Sugerida | Dados Fictícios |
|---------|---------------------|-----------------|
| `production_orders` | 20-30 ordens | Ordens com produtos de plástico/injeção fictícios |
| `planning` | 15-20 planejamentos | Alocações em 10 máquinas |
| `production_entries` | 100-150 lançamentos | Produção por hora, 3 turnos |
| `downtime_entries` | 30-50 paradas | Motivos variados (manutenção, setup, falta MP) |
| `active_downtimes` | 2-3 ativas | Simulação de máquinas paradas agora |
| `escalas_operadores` | 15-20 operadores | Nomes fictícios, turnos A/B/C |
| `ferramentaria_moldes` | 10-15 moldes | Moldes com ciclos de vida |
| `quality_measurements` | 50-80 medições | Dados SPC com distribuição normal |
| `system_logs` | 30-50 logs | Ações do sistema |
| `oee_history` | 30 dias | OEE diário por máquina (75-90%) |

**Nomes fictícios sugeridos:**
- Empresa: "Indústria Plásticos Demo Ltda" ou "PlastTech Demo"
- Máquinas: INJ-01 a INJ-10 (Injetoras)
- Produtos: "Tampa Flip-Top 28mm", "Frasco 500ml PET", "Pré-forma 22g", etc.
- Operadores: Nomes brasileiros comuns fictícios

---

### FASE 4 — Autenticação Local
**Substituir Firebase Auth por autenticação simulada**

| # | Tarefa | Detalhes |
|---|--------|----------|
| 4.1 | Criar usuários demo fixos | Admin, Supervisor, Operador, Qualidade, PCP |
| 4.2 | Login sem backend | Validar contra lista local de usuários |
| 4.3 | Manter RBAC funcional | Permissões por role continuam funcionando |
| 4.4 | Auto-login opcional | Para facilitar demonstração no portfólio |

**Usuários demo sugeridos:**

| Usuário | Senha | Role | Permissões |
|---------|-------|------|------------|
| `admin` | `demo1234` | admin | Acesso total |
| `supervisor` | `demo1234` | supervisor | Produção, Qualidade, Relatórios |
| `operador` | `demo1234` | operador | Lançamento, Paradas |
| `qualidade` | `demo1234` | qualidade | Qualidade, SPC |
| `pcp` | `demo1234` | pcp | PCP, Planejamento |

---

### FASE 5 — Adaptações para GitHub Pages
**Hospedar como site estático no GitHub Pages**

| # | Tarefa | Detalhes |
|---|--------|----------|
| 5.1 | Criar workflow GitHub Actions para Pages | Deploy automático na branch `main` |
| 5.2 | Ajustar paths relativos | Garantir que funciona em subpath `/nome-repo/` |
| 5.3 | Criar `README.md` atrativo | Badges, screenshots, features, demo link |
| 5.4 | Adicionar banner "DEMO" | Indicar claramente que são dados fictícios |
| 5.5 | Criar `404.html` | Para SPA routing no GitHub Pages |

---

### FASE 6 — Polimento para Portfólio

| # | Tarefa | Detalhes |
|---|--------|----------|
| 6.1 | Remover referências à empresa real | "Hokkaido" → nome fictício |
| 6.2 | Remover documentação interna sensível | Análises de custo, ROI, dados reais |
| 6.3 | Criar README profissional | Tecnologias, arquitetura, screenshots |
| 6.4 | Adicionar LICENSE | MIT ou outra licença open-source |
| 6.5 | Limpar arquivos desnecessários | Remover docs internos, análises, testes específicos |
| 6.6 | Adicionar meta tags OG | Para preview bonito ao compartilhar link |

---

## 📁 Arquivos que Precisam ser Modificados (por fase)

### Fase 1 — Limpeza de Credenciais (4 arquivos)
- `script.js` (linhas ~420-427 — config Firebase)
- `login.html` (linhas ~136-142 — config Firebase)
- `dashboard-tv.html` (linhas ~2829-2834 — config Firebase)
- `acompanhamento-turno.html` (linhas ~462-467 — config Firebase)

### Fase 2 — Substituição da camada Firebase (8 arquivos core + 5 novos)
**Criar novos:**
- `src/mock/mock-firebase.js`
- `src/mock/mock-auth.js`
- `src/mock/mock-database.js`
- `src/mock/mock-storage.js`
- `src/mock/seed-data/*.js`

**Modificar:**
- `script.js` — Trocar `firebase.initializeApp()` + `firebase.firestore()` por mock
- `src/services/firebase-client.js` — Redirecionar para mock
- `src/services/base.service.js` — Ajustar referências
- `src/services/firebase-cache.service.js` — Ajustar referências
- `src/services/active-downtimes-live.service.js` — Mock do onSnapshot
- `index.html` — Remover CDN scripts, carregar mocks
- `login.html` — Remover CDN scripts, carregar mock-auth
- `dashboard-tv.html` — Remover CDN scripts, carregar mocks

### Fase 3 — Dados (arquivos novos em `src/mock/seed-data/`)

### Fase 4 — Auth (2-3 arquivos)
- `auth.js` — Adaptar para mock
- `login.html` — Adaptar fluxo de login
- `index.html` — Adaptar troca de senha

### Fase 5 — GitHub Pages (2-3 arquivos novos)
- `.github/workflows/deploy-pages.yml`
- `404.html`
- `README.md`

---

## ⏱️ Estimativa de Esforço

| Fase | Esforço Estimado | Complexidade |
|------|------------------|--------------|
| Fase 1 — Isolamento | 1-2 horas | Baixa |
| Fase 2 — Mock Firebase | 4-6 horas | Alta |
| Fase 3 — Dados Fictícios | 3-4 horas | Média |
| Fase 4 — Auth Local | 1-2 horas | Média |
| Fase 5 — GitHub Pages | 1 hora | Baixa |
| Fase 6 — Polimento | 2-3 horas | Baixa |
| **TOTAL** | **12-18 horas** | — |

---

## ⚠️ Riscos e Mitigações

| Risco | Probabilidade | Mitigação |
|-------|---------------|-----------|
| Publicar credenciais Firebase no GitHub | Alta (se não limpar antes) | **FASE 1 é obrigatória antes de qualquer push** |
| Mock não cobrir todos os métodos usados | Média | Implementar mock progressivamente, testando cada aba |
| Dados fictícios inconsistentes | Baixa | Gerar dados com relações corretas (ordem → planejamento → entries) |
| Quebrar funcionalidades ao remover Firebase | Média | Testar cada módulo após substituição |
| Listeners onSnapshot não funcionarem no mock | Média | Simular com `setInterval` ou eventos customizados |

---

## 🎯 Resultado Esperado

Ao final deste plano, o projeto será:

1. **100% desvinculado do Firebase** — nenhuma credencial, nenhuma conexão
2. **Funcional com dados fictícios** — todas as telas carregam e exibem dados
3. **Hospedado no GitHub Pages** — acessível publicamente via URL
4. **Seguro** — sem dados reais ou credenciais expostas
5. **Profissional** — README atrativo, dados realistas, demonstração funcional

---

## 📌 Próximo Passo

> **Confirme que este workspace é uma cópia independente do projeto original e que o repositório original NÃO será afetado.**
> 
> Após confirmação, iniciaremos pela **Fase 1 — Isolamento e Limpeza de Credenciais**.

---

*Documento criado em: 04/03/2026*  
*Última atualização: 04/03/2026*
