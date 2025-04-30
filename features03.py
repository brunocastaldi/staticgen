########## feature_calculations.py ##########
"""feature_calculations.py

Rotinas puramente funcionais que isolam a lógica de leitura, filtragem SCD 2 e agregação
para cada feature. Cada função recebe:
    * spark
    * pk_ids → DataFrame com a PK já filtrada pelo usuário
    * pk_cols → lista de colunas PK
    * ref_date → datetime base
    * lag_delta → relativedelta que define a janela “até ref_date”

Todas retornam um DataFrame com as colunas PK, ``dreft_sist`` e o valor computado.
"""
from typing import List
from datetime import datetime
from pyspark.sql import DataFrame, SparkSession, functions as F

__all__ = [
    'filter_active_records',
    'vsoma_rtrit_reneg_atvo',
    'vmax_grau_svrdade_rtrit_reneg_atvo',
    'nrtrit_reneg_atvo'
]

# -----------------------------------------------------------------------------
# Utilitário comum ----------------------------------------------------------------

def filter_active_records(df: DataFrame, start_date: datetime, end_date: datetime) -> DataFrame:
    """Filtra registros vigentes no intervalo *[start_date, end_date]* baseado em
    ``__START_AT`` e ``__END_AT``.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        DataFrame de origem contendo colunas ``__START_AT`` e ``__END_AT``.
    start_date, end_date : datetime
        Limites inferior e superior (inclusivo/exclusivo, respectivamente).

    Returns
    -------
    pyspark.sql.DataFrame
        Registros cujo período de vigência cobre algum ponto dentro do intervalo.
    """
    return df.filter(
        (F.col("__START_AT") <= F.lit(end_date)) & (F.col("__END_AT") > F.lit(start_date))
    )

# -----------------------------------------------------------------------------
# Features ---------------------------------------------------------------------

def vsoma_rtrit_reneg_atvo(
    spark: SparkSession,
    pk_ids: DataFrame,
    pk_cols: List[str],
    ref_date: datetime,
    lag_delta,
) -> DataFrame:
    """Soma dos valores monetários de renegociações ativas."""
    table = spark.table("catalog.schema.vrtrit_reneg_atv_table")
    filtered = filter_active_records(table, ref_date - lag_delta, ref_date)
    agg = filtered.groupBy(pk_cols).agg(
        F.sum('vrtrit_reneg_atv').alias('vsoma_rtrit_reneg_atvo')
    )
    return pk_ids.join(agg, on=pk_cols, how='left').withColumn('dreft_sist', F.lit(ref_date))

def vmax_grau_svrdade_rtrit_reneg_atvo(
    spark: SparkSession,
    pk_ids: DataFrame,
    pk_cols: List[str],
    ref_date: datetime,
    lag_delta,
) -> DataFrame:
    """Valor máximo do grau de severidade de renegociações ativas."""
    table = spark.table("catalog.schema.grau_svrdade_rtrit_table")
    filtered = filter_active_records(table, ref_date - lag_delta, ref_date)
    agg = filtered.groupBy(pk_cols).agg(
        F.max('grau_svrdade_rtrit_reneg_atv').alias('vmax_grau_svrdade_rtrit_reneg_atvo')
    )
    return pk_ids.join(agg, on=pk_cols, how='left').withColumn('dreft_sist', F.lit(ref_date))

def nrtrit_reneg_atvo(
    spark: SparkSession,
    pk_ids: DataFrame,
    pk_cols: List[str],
    ref_date: datetime,
    lag_delta,
) -> DataFrame:
    """Contagem de renegociações ativas."""
    table = spark.table("catalog.schema.reneg_count_table")
    filtered = filter_active_records(table, ref_date - lag_delta, ref_date)
    agg = filtered.groupBy(pk_cols).agg(F.count('*').alias('nrtrit_reneg_atvo'))
    return pk_ids.join(agg, on=pk_cols, how='left').withColumn('dreft_sist', F.lit(ref_date))

################################################################################
########## features.py #########################################################
"""features.py

Classe *Features* + wrapper *ComputedFeatures* com:
- cálculo de features em múltiplos lags/datas;
- armazenamento do resultado em ``self.computed_features``;
- geração automática de *description_map* via introspecção das colunas.
"""

from __future__ import annotations

import re
from typing import List, Union, Optional, Dict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pyspark.sql import DataFrame, SparkSession

from feature_calculations import (
    vsoma_rtrit_reneg_atvo,
    vmax_grau_svrdade_rtrit_reneg_atvo,
    nrtrit_reneg_atvo,
)

__all__ = ['Features', 'ComputedFeatures']

# -----------------------------------------------------------------------------
# Wrapper de resultado ---------------------------------------------------------

class ComputedFeatures:
    """Empacota o DataFrame computado e produz DDL Delta Lake.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Resultado final das features.
    pk_cols : list[str]
        Colunas que formam a PK.
    description_map : dict, optional
        Texto descritivo por coluna. Caso ausente é gerado automaticamente.
    """

    def __init__(self, df: DataFrame, pk_cols: List[str], description_map: Optional[Dict[str, str]] = None):
        self.df = df
        self.pk_cols = pk_cols
        self.description_map = description_map or self._auto_describe()

    # ---------------------------------------------------------------------
    def _auto_describe(self) -> Dict[str, str]:
        """Cria descrições genéricas baseadas no esquema do DataFrame."""
        return {f.name: f"Coluna {f.name} ({f.dataType.simpleString()})" for f in self.df.schema.fields}

    # ---------------------------------------------------------------------
    def print_ddl_schema(self) -> str:
        """Retorna string DDL Delta Lake com **NOT NULL/PK** e comentários."""
        lines = []
        for field in self.df.schema.fields:
            col = field.name
            dtype = field.dataType.simpleString()
            not_null = 'NOT NULL' if col in self.pk_cols else ''
            comment = self.description_map.get(col, '')
            lines.append(f"`{col}` {dtype} {not_null} COMMENT '{comment}'")
        pk_stmt = f"PRIMARY KEY ({', '.join([f'`{c}`' for c in self.pk_cols])})"
        return "(\n  " + ",\n  ".join(lines) + f",\n  {pk_stmt}\n) USING DELTA"

# -----------------------------------------------------------------------------
# Classe principal -------------------------------------------------------------

class Features:
    """Pipeline de cálculo de features autorregressivas.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Sessão Spark (timezone é forçado para *America/Sao_Paulo*).
    base_descriptions : dict, optional
        Descrições humanas para features *base* (sem sufixo de lag).
    """

    _lag_regex = re.compile(r"^(.+?)(_ultim_(\d+)([dwmy]))?$")
    _unit_pt = {'d': 'dia', 'w': 'semana', 'm': 'mês', 'y': 'ano'}

    def __init__(self, spark: SparkSession, base_descriptions: Optional[Dict[str, str]] = None):
        self.spark = spark
        self.spark.conf.set('spark.sql.session.timeZone', 'America/Sao_Paulo')
        self.base_descriptions = base_descriptions or {
            'vsoma_rtrit_reneg_atvo': 'Soma dos valores monetários de renegociações ativas',
            'vmax_grau_svrdade_rtrit_reneg_atvo': 'Valor máximo do grau de severidade de renegociações ativas',
            'nrtrit_reneg_atvo': 'Contagem de renegociações ativas',
        }
        self.feature_funcs = {
            'vsoma_rtrit_reneg_atvo': vsoma_rtrit_reneg_atvo,
            'vmax_grau_svrdade_rtrit_reneg_atvo': vmax_grau_svrdade_rtrit_reneg_atvo,
            'nrtrit_reneg_atvo': nrtrit_reneg_atvo,
        }
        self.computed_features: Optional[ComputedFeatures] = None

    # ---------------------------------------------------------------------
    def list(self) -> List[str]:
        return list(self.feature_funcs.keys())

    # ---------------------------------------------------------------------
    def compute(
        self,
        feature_names: List[str],
        pk_ids: DataFrame,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        freq: str = '1w',
        lags: List[Union[int, str]] | None = None,
    ) -> DataFrame:
        """Executa o cálculo e guarda resultado em ``self.computed_features``.

        Parameters
        ----------
        feature_names : list[str]
            Features desejadas.
        pk_ids : pyspark.sql.DataFrame
            Relação de chaves (qualquer cardinalidade).
        start_date, end_date : str, optional
            Limites do calendário de referência (``YYYY/MM/DD``). Se
            ``start_date`` for ``None`` → usa ``end_date``. Se ``end_date`` for
            ``None`` → hoje.
        freq : str, default '1w'
            Step para gerar datas de referência.
        lags : list[int | str], optional
            Lags a aplicar. Se ``None`` → ``[0]``.

        Returns
        -------
        pyspark.sql.DataFrame
            DataFrame com PKs, ``dreft_sist`` e cada feature.
        """
        if lags is None:
            lags = [0]
        pk_cols = pk_ids.columns
        # datas de referência
        end_dt = datetime.strptime(end_date, '%Y/%m/%d') if end_date else datetime.today()
        start_dt = datetime.strptime(start_date, '%Y/%m/%d') if start_date else end_dt
        freq_delta = self._to_reldelta(freq)
        reference_dates = []
        cur = start_dt
        while cur <= end_dt:
            reference_dates.append(cur)
            cur += freq_delta

        result_df = None
        for ref in reference_dates:
            for lag in lags:
                lag_delta = self._to_reldelta(lag)
                for feat in feature_names:
                    if feat not in self.feature_funcs:
                        raise ValueError(f'Feature {feat} não implementada')
                    df_feat = self.feature_funcs[feat](self.spark, pk_ids, pk_cols, ref, lag_delta)
                    result_df = df_feat if result_df is None else result_df.join(
                        df_feat, on=pk_cols + ['dreft_sist'], how='left'
                    )
        # ---------------- guarda resultado ----------------
        desc_map = self._generate_description_map(result_df, pk_cols)
        self.computed_features = ComputedFeatures(result_df, pk_cols, desc_map)
        return result_df

    # ---------------------------------------------------------------------
    def _generate_description_map(self, df: DataFrame, pk_cols: List[str]) -> Dict[str, str]:
        """Gera description_map combinando base_descriptions + derivação de lag."""
        desc: Dict[str, str] = {c: f'Chave primária: {c}' for c in pk_cols}
        desc['dreft_sist'] = 'Data de referência para cálculo das features'
        for col in df.columns:
            if col in desc:
                continue
            m = self._lag_regex.match(col)
            if not m:
                desc[col] = f'Coluna {col}'
                continue
            base, _, val, unit = m.groups()
            base_descr = self.base_descriptions.get(base, f'Feature {base}')
            if val and unit:
                periodo = f"{val} {self._unit_pt[unit]}{'s' if int(val) > 1 else ''}"
                desc[col] = f"{base_descr} nos últimos {periodo}"
            else:
                desc[col] = base_descr
        return desc

    # ---------------------------------------------------------------------
    @staticmethod
    def _to_reldelta(spec: Union[int, str]) -> relativedelta:
        if isinstance(spec, int):
            return relativedelta(days=spec)
        m = re.fullmatch(r'(\d+)([dwmy])', str(spec))
        if not m:
            raise ValueError(f'Formato de tempo inválido: {spec}')
        value, unit = int(m.group(1)), m.group(2)
        return {
            'd': relativedelta(days=value),
            'w': relativedelta(weeks=value),
            'm': relativedelta(months=value),
            'y': relativedelta(years=value),
        }[unit]
