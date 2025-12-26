# ⚡ DEPLOY ULTRA-RÁPIDO (1 MINUTO)

## 🎯 O QUE TENS DE FAZER:

### 1️⃣ CLICA AQUI PARA COMEÇAR:
👉 **https://railway.app/new/template?template=https://github.com/MarcioMiguel22/shelly-sync-railway**

OU

👉 **https://railway.app/new** e seleciona "Deploy from GitHub" → `shelly-sync-railway`

---

### 2️⃣ OBTER CREDENCIAIS (30 SEGUNDOS):

Abre noutra tab: **https://railway.app/dashboard**

**Procura este projeto na lista:**
- Pode chamar-se: "shelly-api-railway" ou
- Qualquer projeto que tenha a API Flask do Shelly

**Como identificar:** É o projeto que tem estas variáveis:
- `INFLUX_URL`
- `INFLUX_ORG`
- `INFLUX_TOKEN`
- `INFLUX_BUCKET`

**Quando encontrares:**
1. Clica no projeto
2. Vai a **Variables**
3. **COPIA os 4 valores** acima

---

### 3️⃣ COLAR VARIÁVEIS (30 SEGUNDOS):

Volta ao projeto **shelly-sync-railway** que está a fazer deploy:

1. Clica em **Variables** ou **Environment**
2. Clica em **"Raw Editor"** (se disponível)
3. **COLA ISTO** (substitui com os valores que copiaste):

```env
INFLUX_URL=https://us-east-1-1.aws.cloud2.influxdata.com
INFLUX_ORG=COLA_O_VALOR_AQUI
INFLUX_TOKEN=COLA_O_TOKEN_AQUI
INFLUX_BUCKET=energy
DATABASE_URL=postgresql://postgres:tDxqlKZrjPbfsDYaaetslawQWJGcqTSq@shuttle.proxy.rlwy.net:41544/railway
SYNC_INTERVAL=300
LOOKBACK_HOURS=1
```

4. Guarda/Add

---

### 4️⃣ AGUARDAR DEPLOY:

O Railway vai fazer deploy automaticamente.

**Aguarda 2 minutos** e depois verifica os **Logs**.

---

## ✅ VERIFICAR SE FUNCIONOU:

### Logs devem mostrar:
```
✓ Conectado ao InfluxDB Cloud
✓ Conectado ao PostgreSQL Railway
✓ Guardados XXX registos no PostgreSQL
Próxima sincronização em 300s...
```

### Depois de 5 minutos, testa PostgreSQL:
```sql
SELECT COUNT(*) FROM shelly_power_readings;
```

**Se COUNT > 0** = ✅ **FUNCIONOU!**

---

## 🎉 PRONTO!

Agora podes **desligar o iMac** sem perder dados do Grafana!

Os dados são guardados automaticamente no PostgreSQL Railway a cada 5 minutos.

---

## 🚨 SE TIVERES PROBLEMAS:

**Não encontro o projeto com credenciais InfluxDB:**
- Procura na lista de projetos Railway por qualquer um que pareça ser a API
- Abre cada um e vai a Variables
- Procura por `INFLUX_URL` - quando encontrares, é esse!

**Worker crashou:**
- Verifica se TODAS as 7 variáveis foram adicionadas
- Verifica se `INFLUX_TOKEN` está correto (sem espaços extra)

**401 Unauthorized:**
- Token InfluxDB expirou ou está errado
- Copia novamente da API Flask

---

## 📱 LINKS DIRETOS:

- **Deploy agora**: https://railway.app/new
- **Dashboard Railway**: https://railway.app/dashboard
- **GitHub Repo**: https://github.com/MarcioMiguel22/shelly-sync-railway

---

**COMEÇA AGORA!** Só demora 1 minuto! 🚀
