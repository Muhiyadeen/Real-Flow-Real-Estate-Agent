# Realflow Real Estate AI Agent 

A simple Flask-based webhook server for the Realflow AI-driven real estate assistant.  
It logs inbound AI call data and displays them as formatted JSON via HTTP endpoints.

## 🚀 Features
- `/webhook` **POST** → Logs incoming call data  
- `/webhook` **GET** → Lists recent logs  
- `/webhook?call_id=<id>` **GET** → Shows one log (pretty JSON)  
- Deployed on **Railway**

## 🔗 Test Commands

**Health check**
```bash
curl https://real-flow-real-estate-agent-production.up.railway.app/
```

**Post test**
```bash
curl -X POST https://real-flow-real-estate-agent-production.up.railway.app/webhook   -H "Content-Type: application/json"   -d '{"message":{"call":{"id":"railway-testing"},"toolCalls":[{"function":{"name":"Set_Lead_Field","arguments":{"field":"full_name","value":"Realflow Test"}}}]}}'
```

**View logs**
- All: `https://real-flow-real-estate-agent-production.up.railway.app/webhook`
- One: `https://<your-url>.railway.app/webhook?call_id=railway-testing`
- View a previous Vapi call logs: `https://real-flow-real-estate-agent-production.up.railway.app/webhook?call_id=caller_id_019a49ed-ade3-7bb6-8178-6d89428ffcde`

## 📎 Example
**Deployed Link:**  
[https://real-flow-real-estate-agent-production.up.railway.app/webhook](https://real-flow-real-estate-agent-production.up.railway.app/webhook)

**Author:** Muhiyadeen  
**Stack:** Python · Flask · Railway · Gunicorn
