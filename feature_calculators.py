# Module: feature_calculators.py
# Funções individuais de cálculo de cada feature

from pyspark.sql import DataFrame, functions as F
from datetime import datetime

def vsoma_rtrit_reneg_atvo(df: DataFrame, id_col: str, ref_date: datetime,
                           start_window: datetime, end_window: datetime) -> DataFrame:
    """
    Soma dos valores dos registros de renegociação restritiva ativos.
    """
    return df.groupBy(id_col).agg(
        F.sum(F.col("valor_rtrit_reneg_atvo")).alias("vsoma_rtrit_reneg_atvo")
    )

def vmax_grau_svrdade_rtrit_reneg_atvo(df: DataFrame, id_col: str, ref_date: datetime,
                                        start_window: datetime, end_window: datetime) -> DataFrame:
    """
    Valor máximo do grau de severidade dos registros de renegociação restritiva ativos.
    """
    return df.groupBy(id_col).agg(
        F.max(F.col("grau_svrdade_rtrit_reneg_atvo")).alias("vmax_grau_svrdade_rtrit_reneg_atvo")
    )

def nrtrit_reneg_atvo(df: DataFrame, id_col: str, ref_date: datetime,
                       start_window: datetime, end_window: datetime) -> DataFrame:
    """
    Contagem de registros de renegociação restritiva ativos.
    """
    return df.groupBy(id_col).agg(
        F.count(F.lit(1)).alias("nrtrit_reneg_atvo")
    )
