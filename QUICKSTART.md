# ⚡ QUICKSTART - Deploy em 5 minutos

## 🎯 Objetivo

Guardar dados do Shelly no PostgreSQL Railway para poderes **desligar o iMac** sem perder dados do Grafana.

---

## 📦 Passo 1: Criar Repositório GitHub

```bash
cd /root/shelly-sync-railway
git init
git add .
git commit -m "Shelly sync: InfluxDB → PostgreSQL"
git branch -M main
git remote add origin https://github.com/MarcioMiguel22/shelly-sync-railway.git
git push -u origin main
```

---

## 🚀 Passo 2: Deploy no Railway

1. Vai a https://railway.app/new
2. **"Deploy from GitHub repo"**
3. Seleciona `shelly-sync-railway`
4. Aguarda deploy automático

---

## ⚙️ Passo 3: Configurar Variáveis (IMPORTANTE!)

No Railway, vai a **Variables** e adiciona:

```bash
INFLUX_URL=https://us-east-1-1.aws.cloud2.influxdata.com
INFLUX_ORG=tua-organizacao
INFLUX_TOKEN=teu-token-aqui
INFLUX_BUCKET=energy
DATABASE_URL=postgresql://postgres:tDxqlKZrjPbfsDYaaetslawQWJGcqTSq@shuttle.proxy.rlwy.net:41544/railway
```

**DICA**: Copia as credenciais InfluxDB da tua **API Flask** (são as mesmas!)

---

## ✅ Passo 4: Verificar que Está a Funcionar

1. Vai a **Deployments** → Clica no deployment ativo
2. Abre **Logs**
3. Deves ver:

```
✓ Conectado ao InfluxDB Cloud
✓ Conectado ao PostgreSQL Railway
✓ Guardados 480 registos no PostgreSQL
✓ Sincronização completa
Próxima sincronização em 300s...
```

---

## 🎉 PRONTO!

Agora os dados do Shelly são guardados automaticamente no PostgreSQL Railway a cada 5 minutos.

**PODES DESLIGAR O IMAC!** 🚀

---

## 🔍 Testar PostgreSQL

```sql
-- Ver últimas leituras
SELECT timestamp, phase, power_w, current_a
FROM shelly_power_readings
WHERE device_id = 'shelly_3em_entrada'
ORDER BY timestamp DESC
LIMIT 50;
```

---

## ⚙️ Configurações Opcionais

### Sincronizar mais frequentemente (1 minuto)

```bash
SYNC_INTERVAL=60
```

### Obter histórico de 24h (primeira vez)

```bash
LOOKBACK_HOURS=24
```

---

## 🐛 Problemas?

### Erro 401 (InfluxDB)

- Verifica se `INFLUX_TOKEN` está correto
- Token deve ter permissão de **leitura** no bucket `energy`

### Sem dados a sincronizar

- Verifica se `collect_shelly_data.py` está a correr no iMac
- Testa InfluxDB Cloud UI manualmente

### Worker crashou

- Vai a **Deployments** → Logs
- Procura erros
- Verifica se TODAS as variáveis estão configuradas

---

**Documentação completa**: Ver `README.md`
