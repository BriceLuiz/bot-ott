# 🤖 Bot OTT — RAYUSDT Binance Futures
## Guia Completo de Configuração

---

## O QUE ESSE BOT FAZ

- Recebe sinais do TradingView (GREEN ALERT = LONG, RED ALERT = SHORT)
- Fecha automaticamente a posição aberta
- Abre a posição oposta usando **100% do saldo** com **15x de alavancagem**
- Par: **RAYUSDT** na Binance Futures

---

## PASSO 1 — Criar API Key na Binance

1. Acesse **binance.com → Perfil → Gerenciamento de API**
2. Clique em **Criar API**
3. Dê um nome (ex: "Bot OTT")
4. Ative apenas: ✅ **Negociação de Futuros**
5. NÃO ative saque
6. Anote a **API Key** e **Secret Key**

---

## PASSO 2 — Hospedar o servidor (grátis no Railway)

1. Acesse **railway.app** e crie uma conta grátis
2. Clique em **New Project → Deploy from GitHub**
   - Ou use **New Project → Empty Project → Add Service → GitHub Repo**
3. Faça upload dos arquivos `server.py` e `requirements.txt`
4. Configure as variáveis de ambiente:

```
BINANCE_API_KEY     = sua_api_key_aqui
BINANCE_API_SECRET  = sua_api_secret_aqui
WEBHOOK_TOKEN       = escolha_uma_senha_secreta (ex: raybot2024xz)
```

5. O Railway vai gerar uma URL pública, ex:
   `https://bot-ott-production.up.railway.app`

---

## PASSO 3 — Configurar alertas no TradingView

### Alerta de LONG (GREEN ALERT):

- **Condição:** OTT → GREEN ALERT
- **Webhook URL:** `https://SUA-URL.railway.app/webhook`
- **Mensagem:**
```json
{"sinal": "long", "token": "sua_senha_secreta"}
```

### Alerta de SHORT (RED ALERT):

- **Condição:** OTT → RED ALERT  
- **Webhook URL:** `https://SUA-URL.railway.app/webhook`
- **Mensagem:**
```json
{"sinal": "short", "token": "sua_senha_secreta"}
```

> ⚠️ O token na mensagem deve ser IGUAL ao WEBHOOK_TOKEN configurado no Railway

---

## PASSO 4 — Testar manualmente

Você pode testar enviando uma requisição para o bot antes de ligar os alertas:

```bash
curl -X POST https://SUA-URL.railway.app/webhook \
  -H "Content-Type: application/json" \
  -d '{"sinal": "long", "token": "sua_senha_secreta"}'
```

---

## FLUXO COMPLETO

```
TradingView detecta GREEN ALERT
        ↓
Envia webhook com {"sinal": "long"}
        ↓
Bot fecha SHORT aberto (se houver)
        ↓
Bot abre LONG com 100% saldo × 15x
        ↓
Aguarda próximo sinal...
```

---

## ⚠️ AVISOS IMPORTANTES

- Teste primeiro com **saldo pequeno** antes de usar o saldo total
- O bot usa **ordem a mercado** (execução imediata, sem slippage control)
- Mantenha sua API Key **em segredo** — nunca compartilhe
- O Railway gratuito pode ter limitações de horas mensais — monitore

---

## SUPORTE

Se tiver algum erro, copie a mensagem de erro do Railway (aba Logs)
e peça ajuda com o texto exato do erro.
