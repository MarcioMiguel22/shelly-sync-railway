#!/usr/bin/env python3
"""
InfluxDB → PostgreSQL Sync for Shelly Data
Migra dados do InfluxDB Cloud para PostgreSQL Railway
Permite desligar o iMac mantendo histórico de dados
"""

import os
import sys
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient
import psycopg2
from psycopg2.extras import execute_batch
import logging
import time

# Configuração InfluxDB (mesmas credenciais da API Flask)
INFLUX_URL = os.getenv('INFLUX_URL', 'https://us-east-1-1.aws.cloud2.influxdata.com')
INFLUX_ORG = os.getenv('INFLUX_ORG', '')
INFLUX_TOKEN = os.getenv('INFLUX_TOKEN', '')
INFLUX_BUCKET = os.getenv('INFLUX_BUCKET', 'energy')

# Configuração PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:tDxqlKZrjPbfsDYaaetslawQWJGcqTSq@shuttle.proxy.rlwy.net:41544/railway')

# Configuração sync
SYNC_INTERVAL = int(os.getenv('SYNC_INTERVAL', '300'))  # 5 minutos
LOOKBACK_HOURS = int(os.getenv('LOOKBACK_HOURS', '1'))  # Sincronizar última hora

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InfluxToPostgresSync:
    def __init__(self):
        self.influx_client = None
        self.pg_conn = None

    def connect_influx(self):
        """Conecta ao InfluxDB Cloud"""
        try:
            self.influx_client = InfluxDBClient(
                url=INFLUX_URL,
                token=INFLUX_TOKEN,
                org=INFLUX_ORG
            )
            # Testa conexão
            self.influx_client.ping()
            logger.info("✓ Conectado ao InfluxDB Cloud")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao InfluxDB: {e}")
            return False

    def connect_postgres(self):
        """Conecta ao PostgreSQL Railway"""
        try:
            self.pg_conn = psycopg2.connect(DATABASE_URL)
            logger.info("✓ Conectado ao PostgreSQL Railway")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao PostgreSQL: {e}")
            return False

    def get_power_data_from_influx(self, hours=1):
        """Obtém dados de potência do InfluxDB"""
        try:
            query_api = self.influx_client.query_api()

            # Query para potência total
            query_total = f'''
            from(bucket: "{INFLUX_BUCKET}")
              |> range(start: -{hours}h)
              |> filter(fn: (r) => r["_measurement"] == "power")
              |> filter(fn: (r) => r["_field"] == "total_power")
              |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
            '''

            result = query_api.query(query_total)

            data = []
            for table in result:
                for record in table.records:
                    data.append({
                        'timestamp': record.get_time(),
                        'device_id': 'shelly_3em_entrada',
                        'phase': 'total',
                        'power_w': record.get_value(),
                        'current_a': None,
                        'voltage_v': None,
                        'power_factor': None,
                        'frequency_hz': None
                    })

            logger.info(f"✓ Obtidos {len(data)} registos de potência total do InfluxDB")
            return data
        except Exception as e:
            logger.error(f"Erro ao obter dados do InfluxDB: {e}")
            return []

    def get_phase_data_from_influx(self, hours=1):
        """Obtém dados por fase do InfluxDB"""
        try:
            query_api = self.influx_client.query_api()

            phases_data = []

            for phase in ['A', 'B', 'C']:
                # Query para potência por fase
                query_power = f'''
                from(bucket: "{INFLUX_BUCKET}")
                  |> range(start: -{hours}h)
                  |> filter(fn: (r) => r["_measurement"] == "power")
                  |> filter(fn: (r) => r["phase"] == "{phase}")
                  |> filter(fn: (r) => r["_field"] == "power")
                  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
                '''

                # Query para corrente por fase
                query_current = f'''
                from(bucket: "{INFLUX_BUCKET}")
                  |> range(start: -{hours}h)
                  |> filter(fn: (r) => r["_measurement"] == "power")
                  |> filter(fn: (r) => r["phase"] == "{phase}")
                  |> filter(fn: (r) => r["_field"] == "current")
                  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
                '''

                # Query para voltagem por fase
                query_voltage = f'''
                from(bucket: "{INFLUX_BUCKET}")
                  |> range(start: -{hours}h)
                  |> filter(fn: (r) => r["_measurement"] == "power")
                  |> filter(fn: (r) => r["phase"] == "{phase}")
                  |> filter(fn: (r) => r["_field"] == "voltage")
                  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
                '''

                power_result = query_api.query(query_power)
                current_result = query_api.query(query_current)
                voltage_result = query_api.query(query_voltage)

                # Combinar dados por timestamp
                phase_map = {}

                for table in power_result:
                    for record in table.records:
                        ts = record.get_time()
                        if ts not in phase_map:
                            phase_map[ts] = {'power': None, 'current': None, 'voltage': None}
                        phase_map[ts]['power'] = record.get_value()

                for table in current_result:
                    for record in table.records:
                        ts = record.get_time()
                        if ts not in phase_map:
                            phase_map[ts] = {'power': None, 'current': None, 'voltage': None}
                        phase_map[ts]['current'] = record.get_value()

                for table in voltage_result:
                    for record in table.records:
                        ts = record.get_time()
                        if ts not in phase_map:
                            phase_map[ts] = {'power': None, 'current': None, 'voltage': None}
                        phase_map[ts]['voltage'] = record.get_value()

                for ts, values in phase_map.items():
                    phases_data.append({
                        'timestamp': ts,
                        'device_id': 'shelly_3em_entrada',
                        'phase': phase,
                        'power_w': values['power'],
                        'current_a': values['current'],
                        'voltage_v': values['voltage'],
                        'power_factor': None,
                        'frequency_hz': None
                    })

            logger.info(f"✓ Obtidos {len(phases_data)} registos de fases do InfluxDB")
            return phases_data
        except Exception as e:
            logger.error(f"Erro ao obter dados de fases do InfluxDB: {e}")
            return []

    def save_to_postgres(self, data, table='shelly_power_readings'):
        """Guarda dados no PostgreSQL"""
        if not data:
            logger.warning("Sem dados para guardar")
            return 0

        try:
            cursor = self.pg_conn.cursor()

            # Usar UPSERT para evitar duplicados
            insert_query = f"""
                INSERT INTO {table}
                (timestamp, device_id, phase, power_w, current_a, voltage_v, power_factor, frequency_hz)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (timestamp, device_id, phase) DO UPDATE SET
                    power_w = EXCLUDED.power_w,
                    current_a = EXCLUDED.current_a,
                    voltage_v = EXCLUDED.voltage_v,
                    power_factor = EXCLUDED.power_factor,
                    frequency_hz = EXCLUDED.frequency_hz
            """

            # Preparar dados para batch insert
            values = [
                (
                    d['timestamp'],
                    d['device_id'],
                    d['phase'],
                    d['power_w'],
                    d['current_a'],
                    d['voltage_v'],
                    d['power_factor'],
                    d['frequency_hz']
                )
                for d in data
            ]

            execute_batch(cursor, insert_query, values, page_size=100)
            self.pg_conn.commit()
            cursor.close()

            logger.info(f"✓ Guardados {len(data)} registos no PostgreSQL")
            return len(data)
        except Exception as e:
            logger.error(f"Erro ao guardar no PostgreSQL: {e}")
            self.pg_conn.rollback()
            return 0

    def add_unique_constraint(self):
        """Adiciona constraint de unicidade se não existir"""
        try:
            cursor = self.pg_conn.cursor()

            # Verificar se constraint já existe
            cursor.execute("""
                SELECT constraint_name
                FROM information_schema.table_constraints
                WHERE table_name = 'shelly_power_readings'
                AND constraint_type = 'UNIQUE'
            """)

            if cursor.fetchone() is None:
                cursor.execute("""
                    ALTER TABLE shelly_power_readings
                    ADD CONSTRAINT unique_reading
                    UNIQUE (timestamp, device_id, phase)
                """)
                self.pg_conn.commit()
                logger.info("✓ Adicionada constraint de unicidade")

            cursor.close()
        except Exception as e:
            logger.warning(f"Constraint já existe ou erro: {e}")
            self.pg_conn.rollback()

    def sync_data(self):
        """Sincroniza dados do InfluxDB para PostgreSQL"""
        logger.info("=== Iniciando sincronização InfluxDB → PostgreSQL ===")

        # Adicionar constraint de unicidade
        self.add_unique_constraint()

        # Obter dados de potência total
        power_data = self.get_power_data_from_influx(hours=LOOKBACK_HOURS)
        saved_power = self.save_to_postgres(power_data)

        # Obter dados por fase
        phase_data = self.get_phase_data_from_influx(hours=LOOKBACK_HOURS)
        saved_phase = self.save_to_postgres(phase_data)

        total_saved = saved_power + saved_phase
        logger.info(f"✓ Sincronização completa: {total_saved} registos guardados")

        return total_saved

    def close(self):
        """Fecha conexões"""
        if self.influx_client:
            self.influx_client.close()
        if self.pg_conn:
            self.pg_conn.close()
        logger.info("✓ Conexões fechadas")

def main():
    """Loop principal de sincronização"""
    logger.info("=" * 70)
    logger.info("🔄 Shelly Data Sync: InfluxDB Cloud → PostgreSQL Railway")
    logger.info("=" * 70)
    logger.info(f"InfluxDB: {INFLUX_URL}")
    logger.info(f"PostgreSQL: {DATABASE_URL.split('@')[1]}")  # Esconde credenciais
    logger.info(f"Intervalo de sincronização: {SYNC_INTERVAL}s")
    logger.info(f"Lookback period: {LOOKBACK_HOURS}h")
    logger.info("Pressiona Ctrl+C para parar")
    logger.info("=" * 70)

    # Verificar variáveis de ambiente
    if not INFLUX_TOKEN or not INFLUX_ORG:
        logger.error("❌ INFLUX_TOKEN e INFLUX_ORG são obrigatórios!")
        logger.error("Configure as variáveis de ambiente no Railway")
        sys.exit(1)

    syncer = InfluxToPostgresSync()

    try:
        # Conectar aos serviços
        if not syncer.connect_influx():
            logger.error("❌ Falha ao conectar ao InfluxDB")
            sys.exit(1)

        if not syncer.connect_postgres():
            logger.error("❌ Falha ao conectar ao PostgreSQL")
            sys.exit(1)

        # Loop de sincronização
        sync_count = 0
        while True:
            sync_count += 1
            logger.info(f"\n--- Sync #{sync_count} ---")

            try:
                syncer.sync_data()
            except Exception as e:
                logger.error(f"Erro durante sincronização: {e}")

            logger.info(f"Próxima sincronização em {SYNC_INTERVAL}s...")
            time.sleep(SYNC_INTERVAL)

    except KeyboardInterrupt:
        logger.info("\n⏹ Parando sincronização...")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
    finally:
        syncer.close()

if __name__ == "__main__":
    main()
