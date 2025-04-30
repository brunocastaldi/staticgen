# feature_calculations.py

import numpy as np
from datetime import datetime
from typing import List
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def filter_active_records(df: DataFrame, start_date: datetime, end_date: datetime) -> DataFrame:
    """
    Filtra registros ativos entre `start_date` e `end_date` em uma tabela SCD Type 2.

    Parameters
    ----------
    df : DataFrame
        DataFrame contendo colunas __START_AT e __END_AT como Timestamps.
    start_date : datetime
        Início do intervalo de vigência.
    end_date : datetime
        Fim do intervalo de vigência.

    Returns
    -------
    DataFrame
        Subconjunto de `df` com apenas registros ativos no intervalo.
    """
    return df.filter(
        (F.col("__START_AT") <= F.lit(end_date)) &
        (F.col("__END_AT") > F.lit(start_date))
    )


def vsoma_rtrit_reneg_atvo(
    df: DataFrame,
    pk_ids: DataFrame,
    pk_cols: List[str],
    ref_date: datetime,
    lag
) -> DataFrame:
    """
    Soma os valores monetários de renegociações ativas no período filtrado.

    Parameters
    ----------
    df : DataFrame
        DataFrame já filtrado por `filter_active_records`.
    pk_ids : DataFrame
        DataFrame contendo as PKs do público-alvo.
    pk_cols : list[str]
        Colunas que formam a chave primária composta.
    ref_date : datetime
        Data de referência para gravação em dreft_sist.
    lag : int or str
        Intervalo de lag (não usado diretamente aqui, mas passado para uniformidade).

    Returns
    -------
    DataFrame
        PKs + coluna vsoma_rtrit_reneg_atvo + coluna dreft_sist.    
    """
    agg = df.groupBy(pk_cols).agg(
        F.sum("vrtrit_reneg_atv").alias("vsoma_rtrit_reneg_atvo")
    )
    out = pk_ids.join(agg, on=pk_cols, how="left").fillna({ "vsoma_rtrit_reneg_atvo": np.nan })
    return out.withColumn("dreft_sist", F.lit(ref_date))


def vmax_grau_svrdade_rtrit_reneg_atvo(
    df: DataFrame,
    pk_ids: DataFrame,
    pk_cols: List[str],
    ref_date: datetime,
    lag
) -> DataFrame:
    """
    Máximo do grau de severidade de renegociações ativas no período.

    Parameters
    ----------
    df : DataFrame
        DataFrame já filtrado por `filter_active_records`.
    pk_ids : DataFrame
        DataFrame contendo as PKs do público-alvo.
    pk_cols : list[str]
        Colunas que formam a chave primária composta.
    ref_date : datetime
        Data de referência para gravação em dreft_sist.
    lag : int or str
        Intervalo de lag (não usado diretamente aqui, mas passado para uniformidade).

    Returns
    -------
    DataFrame
        PKs + coluna vmax_grau_svrdade_rtrit_reneg_atvo + coluna dreft_sist.    
    """
    agg = df.groupBy(pk_cols).agg(
        F.max("grau_svrdade_rtrit_reneg_atv")
         .alias("vmax_grau_svrdade_rtrit_reneg_atvo")
    )
    out = pk_ids.join(agg, on=pk_cols, how="left").fillna({ "vmax_grau_svrdade_rtrit_reneg_atvo": np.nan })
    return out.withColumn("dreft_sist", F.lit(ref_date))


def nrtrit_reneg_atvo(
    df: DataFrame,
    pk_ids: DataFrame,
    pk_cols: List[str],
    ref_date: datetime,
    lag
) -> DataFrame:
    """
    Contagem de renegociações ativas no período.

    Parameters
    ----------
    df : DataFrame
        DataFrame já filtrado por `filter_active_records`.
    pk_ids : DataFrame
        DataFrame contendo as PKs do público-alvo.
    pk_cols : list[str]
        Colunas que formam a chave primária composta.
    ref_date : datetime
        Data de referência para gravação em dreft_sist.
    lag : int or str
        Intervalo de lag (não usado diretamente aqui, mas passado para uniformidade).

    Returns
    -------
    DataFrame
        PKs + coluna nrtrit_reneg_atvo + coluna dreft_sist.    
    """
    agg = df.groupBy(pk_cols).agg(
        F.count("*").alias("nrtrit_reneg_atvo")
    )
    out = pk_ids.join(agg, on=pk_cols, how="left").fillna({ "nrtrit_reneg_atvo": np.nan })
    return out.withColumn("dreft_sist", F.lit(ref_date))


# features.py

import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import List, Union, Optional, Dict
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from feature_calculations import (
    filter_active_records,
    vsoma_rtrit_reneg_atvo,
    vmax_grau_svrdade_rtrit_reneg_atvo,
    nrtrit_reneg_atvo
)


def gerar_description_map(
    df: DataFrame,
    pk_cols: List[str],
    base_descriptions: Dict[str, str]
) -> Dict[str, str]:
    """
    Gera automaticamente o description_map para cada coluna de `df`.

    Parameters
    ----------
    df : DataFrame
        DataFrame resultante com todas as features já calculadas.
    pk_cols : list[str]
        Colunas que compõem a chave primária composta.
    base_descriptions : dict
        Descrições para cada feature base (sem lag), ex.:
        {'vsoma_rtrit_reneg_atvo': 'Soma monetária de renegociações ativas', ...}

    Returns
    -------
    dict
        Mapeamento coluna -> descrição (para uso no DDL).
    """
    desc_map: Dict[str, str] = {}
    # PKs
    for c in pk_cols:
        desc_map[c] = f"Chave primária: {c}"
    # Data de referência
    desc_map["dreft_sist"] = "Data de referência para cálculo das features"

    # Regex para identificar base + lag
    pattern = re.compile(r"^(.+?)(?:_ultim_(\d+)([dwmy]))?$")
    unit_map = {'d': 'dia', 'w': 'semana', 'm': 'mês', 'y': 'ano'}

    for col in df.columns:
        if col in desc_map:
            continue
        m = pattern.match(col)
        if not m:
            desc_map[col] = col
            continue
        base, val, uni = m.groups()
        base_desc = base_descriptions.get(base, f"Feature {base}")
        if val and uni:
            period = f"{val} {unit_map[uni]}{'s' if int(val)>1 else ''}"
            desc_map[col] = f"{base_desc} nos últimos {period}"
        else:
            desc_map[col] = base_desc

    return desc_map


class ComputedFeatures:
    """
    Wrapper que guarda o DataFrame de features calculadas e gera DDL para Delta Lake.
    """

    def __init__(
        self,
        df: DataFrame,
        pk_cols: List[str],
        description_map: Optional[Dict[str, str]] = None
    ):
        self.df = df
        self.pk_cols = pk_cols
        self.description_map = description_map or {}

    def print_ddl_schema(self) -> str:
        """
        Gera um DDL string para criação de tabela Delta com NOT NULL, PRIMARY KEY e COMMENTS.

        Returns
        -------
        str
            DDL completo para uso em Databricks Delta Lake.
        """
        def spark_to_sql(s: str) -> str:
            m = {
                'timestamp': 'TIMESTAMP',
                'double':    'DOUBLE',
                'long':      'BIGINT',
                'int':       'INT',
                'string':    'STRING'
            }
            return m.get(s, s.upper())

        lines = []
        for f in self.df.schema.fields:
            sql_type = spark_to_sql(f.dataType.simpleString())
            not_null = " NOT NULL" if f.name in self.pk_cols else ""
            comment = self.description_map.get(f.name, "")
            comment_clause = f" COMMENT '{comment}'" if comment else ""
            lines.append(f"  {f.name} {sql_type}{not_null}{comment_clause}")

        pk_line = f"  PRIMARY KEY ({', '.join(self.pk_cols)})"
        ddl = (
            "CREATE TABLE your_delta_table (\n"
            + ",\n".join(lines) + ",\n"
            + pk_line + "\n"
            + ") USING DELTA"
        )
        return ddl


class Features:
    """
    Classe para computar features autorregressivas em tabelas SCD Type 2.

    Parameters
    ----------
    spark : SparkSession
        Sessão Spark já configurada.
    """

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.spark.conf.set("spark.sql.session.timeZone", "America/Sao_Paulo")
        # Associa nome -> função do módulo feature_calculations
        self.feature_funcs = {
            'vsoma_rtrit_reneg_atvo': vsoma_rtrit_reneg_atvo,
            'vmax_grau_svrdade_rtrit_reneg_atvo': vmax_grau_svrdade_rtrit_reneg_atvo,
            'nrtrit_reneg_atvo': nrtrit_reneg_atvo
        }
        self.computed_features: Optional[ComputedFeatures] = None

    def list(self) -> List[str]:
        """
        Lista todas as features disponíveis para computação.

        Returns
        -------
        list[str]
        """
        return list(self.feature_funcs.keys())

    def compute(
        self,
        feature_names: List[str],
        pk_ids: DataFrame,
        df: DataFrame,
        reference_date: Optional[Union[str, datetime]] = None,
        freq: str = '1w',
        lags: List[Union[int, str]] = [0]
    ) -> DataFrame:
        """
        Computa as features para o público-alvo e salva em `self.computed_features`.

        Parameters
        ----------
        feature_names : list[str]
            Nomes das features a computar (devem existir em `self.feature_funcs`).
        pk_ids : DataFrame
            DataFrame com colunas de chave primária composta (ex.: ['cli_id','segmento']).
        df : DataFrame
            DataFrame SCD Type 2 contendo __START_AT, __END_AT e colunas numéricas.
        reference_date : str or datetime, optional
            Data de referência inicial (ex.: '2025/03/01'). Se None, usa hoje.
        freq : str
            Frequência de geração de múltiplas datas de referência (e.g. '7d','1m').
        lags : list[int or str]
            Lista de lags (e.g. [0,'7d','1m']).

        Returns
        -------
        DataFrame
            DataFrame com todas as PKs, dreft_sist e features calculadas.
        """
        # prepara datas
        if isinstance(reference_date, str):
            ref_start = datetime.strptime(reference_date, '%Y/%m/%d')
        elif isinstance(reference_date, datetime):
            ref_start = reference_date
        else:
            ref_start = datetime.today()

        ref_end = datetime.today()
        delta = self._parse_time_delta(freq)
        # gera lista de datas de referência
        refs = []
        cur = ref_start
        while cur <= ref_end:
            refs.append(cur)
            cur += delta

        result_df: Optional[DataFrame] = None
        pk_cols = pk_ids.columns

        for ref in refs:
            for lag in lags:
                lag_delta = self._parse_time_delta(lag)
                start = ref - lag_delta
                filt = filter_active_records(df, start, ref)
                for feat in feature_names:
                    if feat not in self.feature_funcs:
                        raise ValueError(f"Feature '{feat}' não implementada.")
                    out = self.feature_funcs[feat](filt, pk_ids, pk_cols, ref, lag)
                    result_df = out if result_df is None else result_df.join(out, on=pk_cols+['dreft_sist'], how='outer')

        # salva wrapper
        self.computed_features = ComputedFeatures(result_df, pk_cols)
        return result_df

    def _parse_time_delta(self, t: Union[int, str]) -> relativedelta:
        """
        Converte string de intervalo (e.g. '7d','1m') ou int em relativedelta exato.

        Parameters
        ----------
        t : int or str
            Número de dias (int) ou formato '<n><d|w|m|y>'.

        Returns
        -------
        relativedelta
        """
        if isinstance(t, int):
            return relativedelta(days=t)
        m = re.match(r'(\d+)([dwmy])', t)
        if not m:
            raise ValueError(f"Formato inválido: {t}")
        v, u = m.groups()
        v = int(v)
        return {
            'd': relativedelta(days=v),
            'w': relativedelta(weeks=v),
            'm': relativedelta(months=v),
            'y': relativedelta(years=v)
        }[u]

"""COMO USAR:
from features import Features, gerar_description_map

# 1. instância
features = Features(spark)

# 2. compute
df_feat = features.compute(
    ['vsoma_rtrit_reneg_atvo','nrtrit_reneg_atvo'],
    pk_ids_df,
    df=scd2_df,
    reference_date='2025/03/01',
    freq='1w',
    lags=[0,'7d','1m']
)

# 3. gerar description_map e associar
base_descriptions = {
    'vsoma_rtrit_reneg_atvo': 'Soma monetária de renegociações ativas',
    'nrtrit_reneg_atvo': 'Contagem de renegociações ativas'
}
desc_map = gerar_description_map(df_feat, pk_ids_df.columns, base_descriptions)
features.computed_features.description_map = desc_map

# 4. imprimir DDL
print(features.computed_features.print_ddl_schema())
"""
