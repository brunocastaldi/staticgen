import dlt
from datetime import date
from engine import FeaturesEngine

spark = dlt.spark
engine = FeaturesEngine(
    spark,
    source_tables = {"tb_rtrit_reneg": spark.table("silver.tb_rtrit_reneg")}
)

# 1. Crie o destino apenas uma vez (DLT gerencia a tabela):
dlt.create_streaming_table(
    name   = "feat_fin_reneg_snapshot",
    comment= "Snapshot mensal de features de renegociações"
)

# 2. Flow de *backfill* (executa uma vez e depois é removido/desabilitado):
@dlt.append_flow(target="feat_fin_reneg_snapshot",
                 name="historical_backfill")
def backfill():
    return engine.compute(
        features=["vsoma_rtrit_reneg_atvo","vmax_grau_svrdade_rtrit_reneg_atvo","nrtrit_reneg_atvo"],
        start   ="2020-01-01",
        end     =date.today(),
        freq    ="1m",
        lags    =[0,"1m","3m","6m"],
        business_day_rule="first"
    )

# 3. Flow incremental mensal (permanece ativo):
@dlt.append_flow(target="feat_fin_reneg_snapshot",
                 name="monthly_increment")
def monthly():
    today = date.today().isoformat()
    return engine.compute(
        features=["vsoma_rtrit_reneg_atvo","vmax_grau_svrdade_rtrit_reneg_atvo","nrtrit_reneg_atvo"],
        start   =today,
        end     =today,     # snapshot único
        freq    ="1d",
        lags    =[0,"1m","3m","6m"],
        business_day_rule="first"
    )
