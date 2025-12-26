# ⚡ DEPLOY RAILWAY - 2 MINUTOS (MANUAL)

## 📦 Repositório já está pronto!

✅ **GitHub**: https://github.com/MarcioMiguel22/shelly-sync-railway

Agora só precisas de fazer o deploy no Railway (super rápido via interface web).

---

## 🚀 PASSO A PASSO (2 minutos)

### 1️⃣ Abrir Railway e Criar Projeto

1. Vai a: **https://railway.app/new**
2. Clica em **"Deploy from GitHub repo"**
3. Procura por **"MarcioMiguel22/shelly-sync-railway"**
4. Clica em **"Deploy Now"**

Aguarda 1 minuto... O deploy inicial vai **FALHAR** (é normal - faltam as variáveis de ambiente).

---

### 2️⃣ Configurar Variáveis de Ambiente

No Railway, clica no serviço que acabou de ser criado:

1. Vai ao separador **"Variables"**
2. Clica em **"New Variable"**
3. Cola TODAS estas variáveis (uma a uma ou usar "Raw Editor"):

#### ⚠️ ATENÇÃO: Precisas de obter as credenciais InfluxDB!

**ONDE ENCONTRAR**: Vai ao teu projeto da **API Flask** no Railway:
- Railway Dashboard → Procura projeto "shelly-api" ou similar
- Clica no serviço → Separador **"Variables"**
- Copia os valores de `INFLUX_URL`, `INFLUX_ORG`, `INFLUX_TOKEN`, `INFLUX_BUCKET`

#### Variáveis para copiar:

```bash
# InfluxDB (COPIAR DA API FLASK - Railway → Projeto API → Variables)
INFLUX_URL=https://us-east-1-1.aws.cloud2.influxdata.com
INFLUX_ORG=SEU_VALOR_AQUI
INFLUX_TOKEN=SEU_TOKEN_AQUI
INFLUX_BUCKET=energy

# PostgreSQL (COPIA ISTO TAL QUAL ESTÁ)
DATABASE_URL=postgresql://postgres:tDxqlKZrjPbfsDYaaetslawQWJGcqTSq@shuttle.proxy.rlwy.net:41544/railway

# Configuração (OPCIONAL - pode deixar estes valores)
SYNC_INTERVAL=300
LOOKBACK_HOURS=1
```

**DICA RÁPIDA**: No Railway, clica em **"RAW Editor"** e cola tudo de uma vez!

---

### 3️⃣ Fazer Redeploy

Depois de adicionar as variáveis:

1. Vai ao separador **"Deployments"**
2. Clica nos **3 pontos (...)** do deployment mais recente
3. Clica em **"Redeploy"**
4. Aguarda 1-2 minutos

---

### 4️⃣ VERIFICAR QUE ESTÁ A FUNCIONAR

1. No separador **"Deployments"**, clica no deployment ativo (verde)
2. Vê os **Logs** - deves ver:

```
✓ Conectado ao InfluxDB Cloud
✓ Conectado ao PostgreSQL Railway
✓ Adicionada constraint de unicidade
✓ Obtidos 120 registos de potência total do InfluxDB
✓ Obtidos 360 registos de fases do InfluxDB
✓ Guardados 480 registos no PostgreSQL
✓ Sincronização completa: 480 registos guardados
Próxima sincronização em 300s...
```

---

## ✅ TESTE FINAL: Verificar PostgreSQL

Conecta ao PostgreSQL e executa:

```sql
SELECT COUNT(*) as total_records
FROM shelly_power_readings
WHERE device_id = 'shelly_3em_entrada';
```

**Se tiver registos** = ✅ **FUNCIONOU!**

---

## 🎉 PRONTO! AGORA PODES:

✅ Desligar o iMac sem medo
✅ Dados do Shelly guardados no PostgreSQL a cada 5 minutos
✅ Histórico preservado permanentemente
✅ Consultar dados via SQL

---

## 🐛 ERROS COMUNS

### ❌ "401 Unauthorized" nos logs

**Solução**: O `INFLUX_TOKEN` está errado ou expirou
- Vai à API Flask no Railway → Variables
- Copia o token EXATO

### ❌ "Bucket not found"

**Solução**: Verifica `INFLUX_BUCKET=energy` (tem de ser exatamente "energy")

### ❌ "Connection refused" (PostgreSQL)

**Solução**: Verifica o `DATABASE_URL` completo:
```
postgresql://postgres:tDxqlKZrjPbfsDYaaetslawQWJGcqTSq@shuttle.proxy.rlwy.net:41544/railway
```

### ❌ Worker continua a crashar

**Solução**: Confirma que TODAS as 6 variáveis foram adicionadas

---

## 📊 QUERIES ÚTEIS (depois de funcionar)

### Ver últimas 20 leituras

```sql
SELECT timestamp, phase, power_w, current_a, voltage_v
FROM shelly_power_readings
WHERE device_id = 'shelly_3em_entrada'
ORDER BY timestamp DESC
LIMIT 20;
```

### Potência média por fase (hoje)

```sql
SELECT
    phase,
    ROUND(AVG(power_w)::numeric, 2) as avg_power_w,
    ROUND(MAX(power_w)::numeric, 2) as max_power_w
FROM shelly_power_readings
WHERE device_id = 'shelly_3em_entrada'
  AND phase IN ('A', 'B', 'C')
  AND timestamp::date = CURRENT_DATE
GROUP BY phase;
```

---

## 💰 Custo

- **Railway Worker**: $5/mês (Hobby Plan) ou grátis (trial 500h/mês)
- **PostgreSQL**: Incluído
- **InfluxDB**: Grátis (Free tier)

**Total**: ~$5/mês ou GRÁTIS se estiver em trial

---

## 🔗 Links

- **GitHub Repo**: https://github.com/MarcioMiguel22/shelly-sync-railway
- **Railway Dashboard**: https://railway.app/dashboard
- **PostgreSQL**: `shuttle.proxy.rlwy.net:41544`

---

**É ISTO! 2 minutos e está feito!** 🚀

Se tiveres problemas, verifica os logs no Railway (Deployments → Logs).
