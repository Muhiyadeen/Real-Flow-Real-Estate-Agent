# Realflow AI Agent Webhook

A simple Flask-based webhook server for the Realflow AI-driven real estate assistant.  
It logs inbound AI call data and displays them as formatted JSON via HTTP endpoints.

## 🚀 Features
- `/webhook` **POST** → Logs incoming call data  
- `/webhook` **GET** → Lists recent logs  
- `/webhook?call_id=<id>` **GET** → Shows one log (pretty JSON)  
- Deployed on **Railway**

## ⚙️ Setup

**Local Run**
```bash
pip install -r requirements.txt
python main.py
```

**Expose via ngrok**
```bash
ngrok http 8080
```

**Deploy to Railway**
- Add `PORT=8080` under Variables  
- Start command: `gunicorn main:app`  
- Optional:
  - `READ_TOKEN=<token>` (secure access)
  - `MASK_PII=true` (hide emails/phones)

## 🔗 Test Commands

**Health check**
```bash
curl https://<your-url>.railway.app/
```

**Post test**
```bash
curl -X POST https://<your-url>.railway.app/webhook   -H "Content-Type: application/json"   -d '{"message":{"call":{"id":"railway-test-1"},"toolCalls":[{"function":{"name":"Set_Lead_Field","arguments":{"field":"full_name","value":"Alex Test"}}}]}}'
```

**View logs**
- All: `https://<your-url>.railway.app/webhook`
- One: `https://<your-url>.railway.app/webhook?call_id=railway-test-1`

## 📎 Example
**Deployed Link:**  
[https://real-flow-real-estate-agent-production.up.railway.app/webhook](https://real-flow-real-estate-agent-production.up.railway.app/webhook)

**Author:** Riyas Muhiyadeen  
**Stack:** Python · Flask · Railway · Gunicorn
