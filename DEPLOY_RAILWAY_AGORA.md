# 🚀 DEPLOY NO RAILWAY - PASSO A PASSO

## ✅ Status: Repositório GitHub Criado!

**URL**: https://github.com/MarcioMiguel22/shelly-sync-railway

---

## 📋 Passos para Deploy (5 minutos)

### 1️⃣ Ir ao Railway

Abre no browser: **https://railway.app/new**

### 2️⃣ Deploy from GitHub

1. Clica em **"Deploy from GitHub repo"**
2. Procura por **"shelly-sync-railway"**
3. Clica em **"Deploy"**
4. Aguarda o deploy inicial (pode falhar - é normal, faltam as variáveis)

### 3️⃣ Configurar Variáveis de Ambiente

No Railway, vai ao projeto que acabou de criar:

1. Clica no serviço **"shelly-sync-railway"**
2. Vai ao separador **"Variables"**
3. Clica em **"+ New Variable"**
4. Adiciona as seguintes variáveis **UMA A UMA**:

#### Variáveis InfluxDB (copiar da API Flask existente)

```bash
INFLUX_URL=https://us-east-1-1.aws.cloud2.influxdata.com
INFLUX_ORG=<VER NA API FLASK - Settings → Variables>
INFLUX_TOKEN=<VER NA API FLASK - Settings → Variables>
INFLUX_BUCKET=energy
```

**ONDE ENCONTRAR**: Vai ao teu projeto da API Flask no Railway → Settings → Variables

#### Variáveis PostgreSQL

```bash
DATABASE_URL=postgresql://postgres:tDxqlKZrjPbfsDYaaetslawQWJGcqTSq@shuttle.proxy.rlwy.net:41544/railway
```

#### Variáveis de Configuração (OPCIONAL)

```bash
SYNC_INTERVAL=300
LOOKBACK_HOURS=1
```

### 4️⃣ Fazer Redeploy

Depois de adicionar TODAS as variáveis:

1. Vai ao separador **"Deployments"**
2. Clica nos **3 pontos (...)** no deployment mais recente
3. Clica em **"Redeploy"**
4. Aguarda o deploy (1-2 minutos)

### 5️⃣ Verificar Logs

1. Vai ao separador **"Deployments"**
2. Clica no deployment ativo (verde)
3. Verifica os **logs** - deves ver:

```
✓ Conectado ao InfluxDB Cloud
✓ Conectado ao PostgreSQL Railway
✓ Adicionada constraint de unicidade
✓ Obtidos 120 registos de potência total do InfluxDB
✓ Obtidos 360 registos de fases do InfluxDB
✓ Guardados 120 registos no PostgreSQL
✓ Guardados 360 registos no PostgreSQL
✓ Sincronização completa: 480 registos guardados
Próxima sincronização em 300s...
```

---

## ✅ Testes de Verificação

### Teste 1: Ver dados no PostgreSQL

Conecta ao PostgreSQL e executa:

```sql
SELECT COUNT(*) as total_records
FROM shelly_power_readings
WHERE device_id = 'shelly_3em_entrada';
```

Deves ter registos!

### Teste 2: Ver últimas leituras

```sql
SELECT timestamp, phase, power_w, current_a, voltage_v
FROM shelly_power_readings
WHERE device_id = 'shelly_3em_entrada'
ORDER BY timestamp DESC
LIMIT 10;
```

### Teste 3: DESLIGAR O IMAC

1. Desliga o iMac (ou para o Docker)
2. Aguarda 10 minutos
3. Verifica PostgreSQL - **os dados CONTINUAM a ser guardados!** ✅
4. Verifica logs Railway - **sincronização continua a funcionar!** ✅

---

## 🐛 Troubleshooting

### Erro: "401 Unauthorized"

**Causa**: INFLUX_TOKEN inválido
**Solução**: Copia o token EXATO da API Flask (Railway → Settings → Variables)

### Erro: "Bucket not found"

**Causa**: INFLUX_BUCKET incorreto
**Solução**: Confirma que o bucket se chama "energy" no InfluxDB Cloud

### Erro: "Connection refused" (PostgreSQL)

**Causa**: DATABASE_URL incorreto
**Solução**: Verifica o URL completo (deve começar com postgresql://)

### Sem dados a sincronizar

**Causa**: InfluxDB sem dados recentes
**Solução**:
1. Verifica se collect_shelly_data.py está a correr no iMac
2. Testa query no InfluxDB Cloud UI manualmente

### Worker para constantemente

**Causa**: Falta alguma variável de ambiente
**Solução**: Verifica que TODAS as 6 variáveis estão configuradas

---

## 🎯 Resultado Esperado

Depois do deploy bem-sucedido:

✅ Worker a correr no Railway
✅ Sincronização automática a cada 5 minutos
✅ Dados guardados no PostgreSQL
✅ Podes desligar o iMac
✅ Dados históricos preservados
✅ Custo: ~€5/mês (Railway Hobby Plan)

---

## 📊 Queries Úteis PostgreSQL

### Potência total nas últimas 24h

```sql
SELECT timestamp, power_w
FROM shelly_power_readings
WHERE device_id = 'shelly_3em_entrada'
  AND phase = 'total'
  AND timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;
```

### Média por fase (hoje)

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

### Total de registos

```sql
SELECT
    COUNT(*) FILTER (WHERE phase = 'total') as total_records,
    COUNT(*) FILTER (WHERE phase = 'A') as phase_a_records,
    COUNT(*) FILTER (WHERE phase = 'B') as phase_b_records,
    COUNT(*) FILTER (WHERE phase = 'C') as phase_c_records,
    COUNT(*) as all_records
FROM shelly_power_readings
WHERE device_id = 'shelly_3em_entrada';
```

---

## 🔗 Links Úteis

- **Repositório GitHub**: https://github.com/MarcioMiguel22/shelly-sync-railway
- **Railway Dashboard**: https://railway.app/dashboard
- **InfluxDB Cloud**: https://cloud2.influxdata.com
- **PostgreSQL DB**: Conecta via psql ou cliente GUI

---

**Feito! Agora tens backup persistente dos dados Shelly!** 🎉
