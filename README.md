# furto-roubo-bot 🔍

> **Monitor automático de ocorrências de roubo e furto no estado de São Paulo**, com base nos dados públicos da Secretaria de Segurança Pública (SSP-SP), histórico persistido em CSV e alertas configuráveis por e-mail.

---

## Índice

- [Sobre o projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Como executar](#como-executar)
- [Execução agendada](#execução-agendada)
- [Estrutura de diretórios](#estrutura-de-diretórios)
- [Próximas melhorias](#próximas-melhorias)
- [Licença](#licença)

---

## Sobre o projeto

O **furto-roubo-bot** lê planilhas `.xlsx` disponibilizadas pela SSP-SP, extrai e contabiliza automaticamente as ocorrências de **roubo** e **furto** por município, armazena o histórico localmente e, quando o número de incidentes ultrapassa um limiar configurável, dispara um **alerta por e-mail** para o responsável.

O projeto foi concebido para uso em **segurança pessoal, logística urbana e monitoramento de risco** — qualquer cenário em que acompanhar a evolução da criminalidade em uma área específica seja relevante para a tomada de decisão.

---

## Funcionalidades

| # | Funcionalidade | Status |
|---|----------------|--------|
| 1 | Leitura e normalização de planilhas SSP-SP (`.xlsx`) | ✅ |
| 2 | Filtragem por município (config.json) | ✅ |
| 3 | Filtro geográfico por raio (Haversine, requer lat/lon nos dados) | ✅ |
| 4 | Persistência de histórico em `LOGS/history.csv` | ✅ |
| 5 | Log estruturado (console + arquivo `LOGS/bot.log`) | ✅ |
| 6 | Alerta por e-mail via SMTP com retry/backoff | ✅ |
| 7 | Execução periódica automática via `schedule` | ✅ |
| 8 | Suporte a e-mail HTML | ✅ |
| 9 | Visualização geográfica com Folium | 🔜 |
| 10 | Dashboard com gráficos de tendência | 🔜 |

---

## Arquitetura

```
config.json + .env
       │
       ▼
    bot.py  ──────────────────────────────────────────────────┐
       │                                                       │
       ├─► api_client.py          Lê e normaliza planilha SSP-SP
       │        └─► pandas / openpyxl
       │
       ├─► scraper.py             Filtra por município / raio geográfico
       │
       ├─► utils.py               Logging, timestamp, escrita atômica em CSV
       │        └─► LOGS/history.csv
       │
       └─► email_alert.py         Envio SMTP com retry
                └─► smtplib / .env
```

---

## Pré-requisitos

- Python **3.11** ou superior
- Arquivo `.xlsx` da SSP-SP ([download oficial](https://www.ssp.sp.gov.br/estatistica/pesquisa.aspx))
- Conta de e-mail com SMTP habilitado (ex: Gmail com senha de aplicativo), **se quiser alertas**

---

## Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/furto-roubo-bot.git
cd furto-roubo-bot

# 2. Crie e ative um ambiente virtual (recomendado)
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt
```

---

## Configuração

### 1. Variáveis de ambiente (alertas por e-mail)

```bash
cp .env.example .env
# Edite .env com seu editor favorito e preencha os valores
```

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `EMAIL_SENDER` | Remetente do alerta | `bot@gmail.com` |
| `EMAIL_PASSWORD` | Senha de aplicativo | `abcd efgh ijkl mnop` |
| `SMTP_HOST` | Servidor SMTP | `smtp.gmail.com` |
| `SMTP_PORT` | Porta SMTP (TLS) | `587` |

> **Dica Gmail:** Acesse [Senhas de app](https://myaccount.google.com/apppasswords) para gerar uma senha de 16 caracteres sem precisar desativar a verificação em duas etapas.

### 2. `config.json`

```json
{
  "ssp_xlsx_path": "dados/ssp_sp_roubo_furto.xlsx",
  "area": {
    "municipio": "São Paulo",
    "center_lat": -23.5505,
    "center_lon": -46.6333,
    "radius_km": null
  },
  "alert_threshold": 10,
  "email": {
    "enabled": false,
    "receiver": "destinatario@exemplo.com"
  },
  "schedule": {
    "enabled": false,
    "interval_hours": 24
  }
}
```

| Chave | Tipo | Descrição |
|-------|------|-----------|
| `ssp_xlsx_path` | string | Caminho para a planilha SSP-SP |
| `area.municipio` | string | Município de interesse (filtragem exata, case-insensitive) |
| `area.center_lat/lon` | float | Coordenadas para filtro por raio (opcional) |
| `area.radius_km` | float \| null | Raio em km (null = sem filtro de raio) |
| `alert_threshold` | int | Mínimo de ocorrências para disparar alerta |
| `email.enabled` | bool | Ativa/desativa envio de e-mail |
| `email.receiver` | string | Destinatário do alerta |
| `schedule.enabled` | bool | Ativa execução periódica automática |
| `schedule.interval_hours` | int | Intervalo entre execuções (horas) |

---

## Como executar

```bash
# A partir da raiz do projeto
python -m src.bot
```

Saída esperada no console:

```
2025-11-10 18:00:00 [INFO] src.bot — Iniciando coleta de dados — 2025-11-10 18:00:00
2025-11-10 18:00:01 [INFO] src.api_client — Registros encontrados (roubo/furto): 12
2025-11-10 18:00:01 [INFO] src.bot — Total de ocorrências (roubo/furto): 670521
2025-11-10 18:00:01 [INFO] src.bot — Histórico atualizado em LOGS/history.csv
2025-11-10 18:00:01 [INFO] src.bot — Execução concluída — 2025-11-10 18:00:01
```

---

## Execução agendada

Para rodar o bot automaticamente a cada N horas, ative o agendador no `config.json`:

```json
"schedule": {
  "enabled": true,
  "interval_hours": 24
}
```

Com isso, o bot executa imediatamente ao iniciar e depois a cada 24 horas enquanto o processo estiver ativo.

Alternativamente, você pode usar o **cron** (Linux/macOS) ou o **Agendador de Tarefas** (Windows) para maior controle:

```bash
# Exemplo cron — executa todo dia às 8h
0 8 * * * /caminho/para/.venv/bin/python -m src.bot
```

---

## Estrutura de diretórios

```
furto-roubo-bot/
├── .env.example          # Modelo de variáveis de ambiente
├── .gitignore
├── config.json           # Configurações do bot
├── requirements.txt
├── README.md
├── LICENSE
├── dados/
│   └── ssp_sp_roubo_furto.xlsx   # Planilha SSP-SP (não versionada)
├── LOGS/
│   ├── history.csv       # Histórico de execuções
│   └── bot.log           # Log detalhado
└── src/
    ├── bot.py            # Entrypoint e pipeline principal
    ├── api_client.py     # Leitura e normalização da planilha
    ├── scraper.py        # Filtragem geográfica
    ├── utils.py          # Logging, timestamp, CSV
    └── email_alert.py    # Envio de alertas por e-mail
```

---

## Próximas melhorias

- [ ] **Dashboard interativo** com Folium/Plotly mostrando ocorrências por região no mapa
- [ ] **Relatório PDF** automático para compartilhamento com equipes de segurança/logística
- [ ] **Integração com API de trânsito** (Google Maps / HERE) para correlacionar horários de pico
- [ ] **Integração com OpenWeatherMap** para análise preditiva (clima × criminalidade)
- [ ] **Suporte a múltiplas fontes** (outros estados, portais de segurança pública)
- [ ] **Testes automatizados** com `pytest` e cobertura mínima de 80%
- [ ] **Containerização** com Docker para facilitar o deploy

---

## Licença

Distribuído sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

> Dados públicos fornecidos pela [Secretaria de Segurança Pública do Estado de São Paulo](https://www.ssp.sp.gov.br).
