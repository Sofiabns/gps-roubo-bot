# GPS Inteligente de Previsão de Roubos/Furtos - furto-roubo-bot

**Descrição breve:**  
Monitoramento inteligente de roubos e furtos em uma área específica de São Paulo, integrando dados públicos, análise de proximidade e alertas por e-mail. Ideal para segurança pessoal, logística ou monitoramento urbano.

---

## Funcionalidades

- Consulta automática de dados de crimes recentes (SSP-SP ou outras fontes públicas)  
- Filtragem por raio geográfico em torno de um ponto central  
- Armazenamento histórico em CSV (`LOGS/history.csv`)  
- Alertas por e-mail quando o número de incidentes ultrapassa limite definido  
- Console intuitivo com resultados em tempo real  
- Preparado para integrar clima, trânsito e APIs externas  

---

## Tecnologias

- Python 3.11+  
- Pandas  
- Requests  
- Geopy  
- Folium (para futuras visualizações)  
- Selenium/Webdriver (opcional para extensões futuras)  
- Python-dotenv (variáveis de ambiente)

---

## Estrutura do Projeto

gps-roubo-bot/
├── README.md
├── requirements.txt
├── config.json
├── LOGS/
│ └── history.csv
└── src/
├── bot.py
├── scraper.py
├── api_client.py
├── utils.py
└── email_alert.py


---

## Instalação e Setup

1. Clone o repositório:

```bash
git clone https://github.com/Sofiabns/gps-roubo-bot.git
cd gps-roubo-bot
```

2. Crie e ative um ambiente virtual (opcional, recomendado):

python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

3. Instale dependências:

pip install -r requirements.txt

4. Configure o .env (para envio de alertas por e-mail):

copy .env.example .env
# preencha EMAIL_SENDER, EMAIL_PASSWORD, SMTP_HOST, SMTP_PORT

5. Configure config.json com sua área de interesse e limites de alerta.

6. Como Executar

python -m src.bot

7. Customizações

- Alterar raio de monitoramento e coordenadas no config.json

- Ajustar alert_threshold para enviar alertas somente quando necessário

- Integrar OpenWeather API ou dados de trânsito para análise preditiva avançada

- Criar mapa interativo com Folium para visualização geográfica dos incidentes

8. Próximos Passos

- Dashboard interativo com gráficos de risco por região

- Rotina automática usando schedule para atualização periódica

- Melhorias de scraping de dados e integração com múltiplas fontes públicas

- Exportação de relatórios PDF para logística ou segurança
