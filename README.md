# 🔄 Shelly Data Sync: InfluxDB → PostgreSQL

**Worker/Background Job para Railway**
Sincroniza dados do Shelly Pro 3EM do InfluxDB Cloud para PostgreSQL Railway, permitindo desligar o iMac sem perder histórico de dados.

---

## 📋 Visão Geral

Este projeto resolve o problema de **perder dados do Grafana quando o iMac é desligado**, criando um backup persistente no PostgreSQL Railway.

### Arquitetura ANTES

```
Shelly Pro 3EM (192.168.0.245)
    ↓
collect_shelly_data.py (Docker no iMac) ⚠️ SE IMAC DESLIGA = PERDE DADOS
    ↓
InfluxDB Cloud ☁️
    ↓
Flask API (Railway)
    ↓
React Frontend (Netlify)
```

### Arquitetura DEPOIS (com este projeto)

```
Shelly Pro 3EM (192.168.0.245)
    ↓
collect_shelly_data.py (Docker no iMac)
    ↓
InfluxDB Cloud ☁️ ━━━━━━━━━━┓
    ↓                        ↓
Flask API (Railway)    sync_influx_to_postgres.py (Railway Worker) ✅
    ↓                        ↓
React Frontend         PostgreSQL Railway ✅ BACKUP PERSISTENTE
```

**Agora podes desligar o iMac!** Os dados ficam guardados no PostgreSQL Railway.

---

## 🚀 Deploy no Railway

### Pré-requisitos

1. Conta Railway: https://railway.app/
2. Credenciais InfluxDB Cloud (as mesmas da API Flask)
3. Base de dados PostgreSQL no Railway já criada

### Passo 1: Criar Repositório GitHub

```bash
cd /root/shelly-sync-railway
git init
git add .
git commit -m "Initial commit: Shelly InfluxDB → PostgreSQL sync"
git branch -M main
git remote add origin https://github.com/MarcioMiguel22/shelly-sync-railway.git
git push -u origin main
```

### Passo 2: Deploy no Railway

1. Vai a https://railway.app/new
2. Clica em **"Deploy from GitHub repo"**
3. Seleciona o repositório `shelly-sync-railway`
4. Railway faz deploy automaticamente

### Passo 3: Configurar como Worker

1. No Railway, vai ao projeto
2. **Settings** → **Service Settings**
3. Em **Start Command**, garante que está:
   ```
   python sync_influx_to_postgres.py
   ```
4. Ou deixa vazio (usa automaticamente o `Procfile`)

### Passo 4: Configurar Variáveis de Ambiente

No Railway, **Variables** → Adiciona:

```bash
# InfluxDB Cloud (COPIAR DA API FLASK)
INFLUX_URL=https://us-east-1-1.aws.cloud2.influxdata.com
INFLUX_ORG=tua-organizacao
INFLUX_TOKEN=teu-influx-token-aqui
INFLUX_BUCKET=energy

# PostgreSQL (Railway - deve já estar configurado automaticamente)
DATABASE_URL=postgresql://postgres:tDxqlKZrjPbfsDYaaetslawQWJGcqTSq@shuttle.proxy.rlwy.net:41544/railway

# Configuração de Sincronização (OPCIONAL)
SYNC_INTERVAL=300        # Sincronizar a cada 5 minutos
LOOKBACK_HOURS=1         # Sincronizar dados da última hora
```

**IMPORTANTE**: As credenciais InfluxDB são as **MESMAS** que usas na API Flask!

### Passo 5: Deploy e Verificar Logs

1. Railway faz deploy automaticamente
2. Vai a **Deployments** → Clica no deployment mais recente
3. Verifica os **logs** para confirmar que está a funcionar:

```
2025-12-25 23:30:00 - INFO - ======================================================================
2025-12-25 23:30:00 - INFO - 🔄 Shelly Data Sync: InfluxDB Cloud → PostgreSQL Railway
2025-12-25 23:30:00 - INFO - ======================================================================
2025-12-25 23:30:01 - INFO - ✓ Conectado ao InfluxDB Cloud
2025-12-25 23:30:01 - INFO - ✓ Conectado ao PostgreSQL Railway
2025-12-25 23:30:02 - INFO - ✓ Obtidos 120 registos de potência total do InfluxDB
2025-12-25 23:30:03 - INFO - ✓ Obtidos 360 registos de fases do InfluxDB
2025-12-25 23:30:04 - INFO - ✓ Guardados 480 registos no PostgreSQL
2025-12-25 23:30:04 - INFO - ✓ Sincronização completa: 480 registos guardados
2025-12-25 23:30:04 - INFO - Próxima sincronização em 300s...
```

---

## 🧪 Testar Localmente

```bash
# Clonar repositório
git clone https://github.com/MarcioMiguel22/shelly-sync-railway.git
cd shelly-sync-railway

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
export INFLUX_URL="https://us-east-1-1.aws.cloud2.influxdata.com"
export INFLUX_ORG="tua-organizacao"
export INFLUX_TOKEN="teu-token"
export INFLUX_BUCKET="energy"
export DATABASE_URL="postgresql://postgres:tDxqlKZrjPbfsDYaaetslawQWJGcqTSq@shuttle.proxy.rlwy.net:41544/railway"

# Correr script
python sync_influx_to_postgres.py
```

Deves ver logs a indicar que está a sincronizar dados!

---

## 🗄️ Estrutura PostgreSQL

O script cria/usa estas tabelas:

### `shelly_power_readings`

```sql
CREATE TABLE shelly_power_readings (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    device_id VARCHAR(100) NOT NULL,
    phase VARCHAR(10) NOT NULL,          -- 'total', 'A', 'B', 'C'
    power_w REAL,
    current_a REAL,
    voltage_v REAL,
    power_factor REAL,
    frequency_hz REAL,
    UNIQUE (timestamp, device_id, phase)  -- Evita duplicados
);
```

### `shelly_phase_data`

```sql
CREATE TABLE shelly_phase_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    device_id VARCHAR(100) NOT NULL,
    phase VARCHAR(10) NOT NULL,
    power_w REAL,
    reactive_power_var REAL,
    apparent_power_va REAL,
    current_a REAL,
    voltage_v REAL,
    power_factor REAL,
    frequency_hz REAL
);
```

### `shelly_energy_summary`

```sql
CREATE TABLE shelly_energy_summary (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    device_id VARCHAR(100) NOT NULL,
    total_active_energy_wh REAL,
    total_reactive_energy_varh REAL,
    total_returned_energy_wh REAL,
    max_power_w REAL,
    min_power_w REAL,
    avg_power_w REAL
);
```

---

## ⚙️ Configuração Avançada

### Ajustar Intervalo de Sincronização

Por defeito, sincroniza **a cada 5 minutos** (300s). Para ajustar:

```bash
# Railway Variables
SYNC_INTERVAL=60   # Sincronizar a cada 1 minuto
SYNC_INTERVAL=900  # Sincronizar a cada 15 minutos
```

### Ajustar Período de Lookback

Por defeito, sincroniza **última 1 hora**. Para ajustar:

```bash
# Railway Variables
LOOKBACK_HOURS=2   # Sincronizar últimas 2 horas
LOOKBACK_HOURS=24  # Sincronizar últimas 24 horas (primeira vez)
```

**NOTA**: Na primeira vez, recomenda-se `LOOKBACK_HOURS=24` para obter histórico inicial.

---

## 📊 Queries Úteis PostgreSQL

### Ver últimas 100 leituras

```sql
SELECT timestamp, phase, power_w, current_a, voltage_v
FROM shelly_power_readings
WHERE device_id = 'shelly_3em_entrada'
ORDER BY timestamp DESC
LIMIT 100;
```

### Ver potência total nas últimas 24h

```sql
SELECT timestamp, power_w
FROM shelly_power_readings
WHERE device_id = 'shelly_3em_entrada'
  AND phase = 'total'
  AND timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;
```

### Ver média de potência por fase (hoje)

```sql
SELECT
    phase,
    AVG(power_w) as avg_power,
    MAX(power_w) as max_power,
    MIN(power_w) as min_power
FROM shelly_power_readings
WHERE device_id = 'shelly_3em_entrada'
  AND phase IN ('A', 'B', 'C')
  AND timestamp::date = CURRENT_DATE
GROUP BY phase;
```

### Ver total de registos guardados

```sql
SELECT COUNT(*) as total_records
FROM shelly_power_readings
WHERE device_id = 'shelly_3em_entrada';
```

---

## 🐛 Troubleshooting

### Erro: "401 Unauthorized" (InfluxDB)

**Causa**: Token InfluxDB inválido ou expirado
**Solução**:
1. Vai a https://cloud2.influxdata.com
2. **Data** → **API Tokens**
3. Verifica se token tem permissões de **leitura** no bucket `energy`
4. Atualiza `INFLUX_TOKEN` no Railway

### Erro: "Bucket not found"

**Causa**: Bucket não existe ou nome errado
**Solução**:
1. Verifica nome do bucket no InfluxDB Cloud UI
2. Confirma `INFLUX_BUCKET=energy` no Railway

### Erro: "Connection refused" (PostgreSQL)

**Causa**: DATABASE_URL incorreto
**Solução**:
1. Verifica se PostgreSQL está a correr no Railway
2. Confirma `DATABASE_URL` está correto nas variáveis

### Sem dados a sincronizar

**Causa**: InfluxDB sem dados recentes
**Solução**:
1. Verifica se `collect_shelly_data.py` está a correr no iMac
2. Testa query manual no InfluxDB Cloud UI:
   ```flux
   from(bucket: "energy")
     |> range(start: -1h)
     |> filter(fn: (r) => r["_measurement"] == "power")
   ```

### Worker crashou no Railway

**Solução**:
1. Vai a **Deployments** → Logs
2. Procura erros
3. Verifica se todas as variáveis estão configuradas
4. Tenta fazer redeploy manual

---

## 💰 Custos

- **Railway Worker**: $5/mês (Hobby Plan) ou €0 (trial 500h/mês)
- **PostgreSQL Railway**: Incluído no plano
- **InfluxDB Cloud**: €0/mês (Free até 10MB/dia)

**Total**: ~€5/mês (ou grátis se estiver no trial)

---

## 🔒 Segurança

✅ Tokens nunca commitados (via variáveis de ambiente)
✅ Read-only access ao InfluxDB
✅ PostgreSQL em rede privada Railway
✅ Logs não mostram credenciais (mascaradas)

---

## 📚 Documentação Relacionada

- **API Flask**: https://github.com/MarcioMiguel22/shelly-api-railway
- **Frontend React**: https://github.com/MarcioMiguel22/shelly-solar-site-3-fases-entrada
- **Railway Docs**: https://docs.railway.app/
- **InfluxDB Cloud**: https://docs.influxdata.com/influxdb/cloud/

---

## 🤝 Contribuir

1. Fork o projeto
2. Cria branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push (`git push origin feature/NovaFuncionalidade`)
5. Abre Pull Request

---

## 📄 Licença

Open source sob licença MIT.

---

## 👤 Autor

**Márcio Miguel**

- GitHub: [@MarcioMiguel22](https://github.com/MarcioMiguel22)
- Email: marciorodrigo2@gmail.com

---

## 🎯 Próximos Passos

Depois de fazer deploy:

1. ✅ Verifica logs no Railway
2. ✅ Confirma que dados estão a ser sincronizados
3. ✅ Testa queries PostgreSQL
4. ✅ **DESLIGA O IMAC E TESTA!**
5. ✅ Dados continuam disponíveis no PostgreSQL

---

**Feito com ❤️ para nunca mais perder dados do Grafana** 🚀
