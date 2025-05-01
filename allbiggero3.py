# ========================================= utils.py =========================================
"""
Ferramentas utilitárias para manipulação temporal, nomenclaturas mnemônicas
e geração de timelines no PySpark.

Notas
-----
As funções aqui definidas são *stateless* e independentes de qualquer `SparkSession`
além da que é passada por parâmetro. Mantêm compatibilidade total com
``Databricks Runtime`` e Unity Catalog, considerando *lazy evaluation*.

Exemplos
--------
>>> from utils import generate_timeline
>>> tl_df = generate_timeline(spark, "2024-01-01", "2024-03-01", freq="1m")
>>> tl_df.show()
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Dict, Tuple, Union, List

from dateutil.relativedelta import relativedelta  # type: ignore
from pyspark.sql import DataFrame, Window, functions as F, SparkSession

# -------------------------------------------------------------------------------------------
# Mapeamentos internos para sufixos mnemônicos
# -------------------------------------------------------------------------------------------
_NUMBERS = str.maketrans("", "", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
_LETTERS = str.maketrans("", "", "0123456789")

_NUM_TO_WORD_PT: Dict[int, str] = {
    0: "zero",
    1: "um",
    2: "dois",
    3: "tres",
    4: "quato",
    5: "cinco",
    6: "seis",
    7: "sete",
    8: "oito",
    9: "nove",
    10: "dez",
    11: "onze",
    12: "doze",
    13: "treze",
    14: "quatorze",
    15: "quinze",
    16: "dezesseis",
    17: "dezessete",
    18: "dezoito",
    19: "dezenove",
    20: "vinte",
    21: "vinte_e_um",
    22: "vinte_e_dois",
    23: "vinte_e_tres",
    24: "vinte_e_quatro",
    25: "vinte_e_cinco",
    26: "vinte_e_seis",
    27: "vinte_e_sete",
    28: "vinte_e_oito",
    29: "vinte_e_nove",
    30: "trinta",
    31: "trinta_e_um",
}

_UNIT_WORD = {"d": "dia", "w": "smnal", "m": "mes", "y": "ano"}


# -------------------------------------------------------------------------------------------
# Funções auxiliares
# -------------------------------------------------------------------------------------------
def parse_interval(interval: Union[str, int]) -> Tuple[int, str]:
    """
    Converte um intervalo tipo ``'7d'`` ou ``'3m'`` em (numero, unidade).

    Parameters
    ----------
    interval : str or int
        Intervalo com sufixo de unidade (`d`, `w`, `m`, `y`) ou zero.

    Returns
    -------
    tuple
        (numero, unidade) convertidos.

    Raises
    ------
    ValueError
        Caso a unidade não seja reconhecida.
    """
    if interval in (0, "0"):
        return 0, ""
    if isinstance(interval, int):
        raise ValueError("Inteiros devem vir acompanhados de unidade (ex.: '7d').")
    num = int(interval.translate(_NUMBERS))
    unit = interval.translate(_LETTERS).lower()
    if unit not in {"d", "w", "m", "y"}:
        raise ValueError(f"Unidade de intervalo inválida: {unit}")
    return num, unit


def interval_suffix(interval: Union[str, int]) -> str:
    """
    Gera sufixo padronizado para colunas de *feature*.

    Exemplos
    --------
    >>> interval_suffix('7d')
    '_ultim_7dias'
    """
    if interval in (0, "0", None):
        return ""
    num, unit = parse_interval(interval)
    num_word = _NUM_TO_WORD_PT.get(num, str(num))
    return f"_ultim_{num_word}{_UNIT_WORD[unit]}"


def generate_timeline(
    spark: SparkSession,
    start_date: str,
    end_date: str,
    freq: str = "1m",
    tz: str | None = None,
    adjust_to_bday: str | None = None,
) -> DataFrame:
    """
    Cria um DataFrame coluna única com todas as datas de referência.

    Parameters
    ----------
    spark : SparkSession
        Sessão Spark ativa.
    start_date, end_date : str
        Limites ISO ``YYYY-MM-DD``.
    freq : str, default ``'1m'``
        Frequência das amostras.
    tz : str, optional
        Timezone desejado (ex.: ``'America/Sao_Paulo'``). Se ``None``, usa a
        configuração atual da sessão.
    adjust_to_bday : {'previous', 'next'}, optional
        Ajusta cada data para dia útil anterior ou seguinte.

    Returns
    -------
    DataFrame
        Coluna ``dreft_sist`` com tipo ``date``.

    Notes
    -----
    O cálculo utiliza ``sequence`` nativa do Spark para máxima performance
    (avaliação preguiçosa).&#8203;:contentReference[oaicite:10]{index=10}
    """
    num, unit = parse_interval(freq)
    start_col = F.to_date(F.lit(start_date))
    end_col = F.to_date(F.lit(end_date))

    if unit == "w":
        step = F.expr(f"interval {num*7} days")
    elif unit == "d":
        step = F.expr(f"interval {num} days")
    elif unit == "m":
        step = F.expr(f"interval {num} months")
    else:  # 'y'
        step = F.expr(f"interval {num} years")

    timeline = (
        spark.range(1)
        .select(F.explode(F.sequence(start_col, end_col, step)).alias("dreft_sist"))
    )

    if tz:
        timeline = timeline.select(
            F.from_utc_timestamp(F.col("dreft_sist").cast("timestamp"), tz).cast("date")
        )

    if adjust_to_bday:
        is_bday = (F.dayofweek("dreft_sist").isin(2, 3, 4, 5, 6)).alias("is_bday")
        if adjust_to_bday == "previous":
            # iterativamente busca dia útil anterior
            w = Window.orderBy(F.col("dreft_sist")).rowsBetween(Window.unboundedPreceding, 0)
            timeline = timeline.withColumn(
                "dreft_sist",
                F.last(F.when(is_bday, F.col("dreft_sist")), ignorenulls=True).over(w),
            )
        elif adjust_to_bday == "next":
            w = Window.orderBy(F.col("dreft_sist")).rowsBetween(0, Window.unboundedFollowing)
            timeline = timeline.withColumn(
                "dreft_sist",
                F.first(F.when(is_bday, F.col("dreft_sist")), ignorenulls=True).over(w),
            )

    return timeline.distinct()


# ========================================= registry.py =========================================
"""
Registro central de *features*.

Novas *features* podem ser adicionadas via o decorador ``@register_feature`` sem
qualquer alteração na classe ``Features``. Isso garante desacoplamento completo
entre **definição de negócio** e **orquestração de cálculo**.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from pyspark.sql import DataFrame, SparkSession, functions as F

_feature_registry: Dict[str, "FeatureDefinition"] = {}


@dataclass
class FeatureDefinition:
    """
    Metadados mínimos para que o *engine* saiba calcular uma *feature*.
    """

    name: str
    source_table: str
    id_col: str
    value_col: str | None
    agg: str  # 'sum', 'max', 'count', 'custom'
    description: str
    scd2: bool = True
    start_col: str = "__START_AT"
    end_col: str = "__END_AT"
    custom_fn: Optional[Callable[..., DataFrame]] = None
    required_cols: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _feature_registry[self.name] = self


def register_feature(
    *,
    name: str,
    source_table: str,
    id_col: str,
    value_col: str | None,
    agg: str,
    description: str,
    scd2: bool = True,
    start_col: str = "__START_AT",
    end_col: str = "__END_AT",
):
    """
    Decorador para registrar *feature* baseada em agregação simples.

    Exemplo
    -------
    >>> @register_feature(
    ...     name="vsoma_rtrit_reneg_atvo",
    ...     source_table="financas.rtrit_reneg",
    ...     id_col="ccpf_cnpj",
    ...     value_col="valor_rtrit_reneg_atvo",
    ...     agg="sum",
    ...     description="Soma de valores renegociados ativos"
    ... )
    ... def _unused():  # corpo não é usado
    ...     pass
    """

    def decorator(func: Callable[..., DataFrame]):
        FeatureDefinition(
            name=name,
            source_table=source_table,
            id_col=id_col,
            value_col=value_col,
            agg=agg,
            description=description,
            scd2=scd2,
            start_col=start_col,
            end_col=end_col,
            custom_fn=func if agg == "custom" else None,
            required_cols=[id_col] + ([value_col] if value_col else []),
        )
        return func

    return decorator


# --------------------------------------- exemplo de features -----------------------------------
@register_feature(
    name="vsoma_rtrit_reneg_atvo",
    source_table="financas.rtrit_reneg",
    id_col="ccpf_cnpj",
    value_col="valor_rtrit_reneg_atvo",
    agg="sum",
    description="Valor total renegociado ativo.",
)
def _f1():  # corpo simbólico
    ...


@register_feature(
    name="vmax_grau_svrdade_rtrit_reneg_atvo",
    source_table="financas.rtrit_reneg",
    id_col="ccpf_cnpj",
    value_col="grau_svrdade_rtrit_reneg_atvo",
    agg="max",
    description="Maior grau de severidade de renegociação ativa.",
)
def _f2():
    ...


@register_feature(
    name="nrtrit_reneg_atvo",
    source_table="financas.rtrit_reneg",
    id_col="ccpf_cnpj",
    value_col=None,
    agg="count",
    description="Número de renegociações ativas.",
)
def _f3():
    ...


# ========================================= engine.py =========================================
"""
Módulo principal de cálculo de *features* autorregressivas.
"""

from __future__ import annotations

from typing import List, Dict, Union

from pyspark.sql import SparkSession, DataFrame, functions as F, Window

from utils import generate_timeline, parse_interval, interval_suffix
from registry import _feature_registry, FeatureDefinition

__all__ = ["Features"]


class Features:
    """
    Orquestrador de cálculo de *features* registradas.

    Esta classe **não** requer `DataFrame` de entrada; cada *feature*
    conhece sua própria origem física no Unity Catalog.

    Notes
    -----
    - Joins com dimensões pequenas são automaticamente *broadcast* para reduzir *shuffle*.&#8203;:contentReference[oaicite:11]{index=11}
    - Operações repetidas sobre a mesma tabela são consolidadas numa única leitura.
    - Respeita **lazy evaluation** do Spark; apenas ações finais disparam a execução.&#8203;:contentReference[oaicite:12]{index=12}
    """

    def __init__(
        self,
        spark: SparkSession,
        *,
        freq: str = "1m",
        lags: List[Union[str, int]] | None = None,
        timezone: str | None = None,
        adjust_to_bday: str | None = None,
    ):
        """
        Parameters
        ----------
        spark : SparkSession
            Sessão Spark.
        freq : str, default ``'1m'``
            Frequência de geração de snapshots.
        lags : list, optional
            Lista de lags. Defaults para ``[0, '7d', '1m', '3m', '6m']``.
        timezone : str, optional
            Timezone para correção de datas.
        adjust_to_bday : {'previous', 'next'}, optional
            Ajuste sistemático de cada ``dreft_sist`` para dia útil.
        """
        self.spark = spark
        self.freq = freq
        self.lags = lags or [0, "7d", "1m", "3m", "6m"]
        self.timezone = timezone
        self.adjust_to_bday = adjust_to_bday

    # ---------------------------------------------------------------------
    # Métodos públicos
    # ---------------------------------------------------------------------
    def list(self) -> List[str]:
        """Retorna todas as *features* disponíveis."""
        return sorted(_feature_registry.keys())

    def compute(
        self,
        features: List[str] | None = None,
        *,
        start_date: str,
        end_date: str,
        pk_ids: DataFrame | None = None,
        id_col: str = "ccpf_cnpj",
    ) -> DataFrame:
        """
        Calcula as *features* solicitadas.

        Parameters
        ----------
        features : list, optional
            Caso ``None``, calcula **todas** as *features* registradas.
        start_date, end_date : str
            Limites de cálculo ISO.
        pk_ids : DataFrame, optional
            Conjunto de IDs (coluna única) a limitar o universo.
        id_col : str, default ``'ccpf_cnpj'``
            Nome da coluna de chave primária.

        Returns
        -------
        DataFrame
            Colunas ``[id_col, dreft_sist, <features...>]``.

        Raises
        ------
        ValueError
            Se alguma *feature* for desconhecida.
        """
        feats = features or self.list()
        unknown = set(feats) - set(_feature_registry)
        if unknown:
            raise ValueError(f"Features desconhecidas: {unknown}")

        # -----------------------------------------------------------------
        # Timeline e conjunto de IDs
        # -----------------------------------------------------------------
        timeline_df = generate_timeline(
            self.spark,
            start_date,
            end_date,
            self.freq,
            tz=self.timezone,
            adjust_to_bday=self.adjust_to_bday,
        ).cache()

        if pk_ids is None:
            # busca IDs em todas as fontes envolvidas
            union_ids = None
            for ft in feats:
                fd = _feature_registry[ft]
                src = self.spark.table(fd.source_table).select(fd.id_col).distinct()
                union_ids = src if union_ids is None else union_ids.unionByName(src)
            pk_ids = union_ids.distinct()
        else:
            if id_col != pk_ids.columns[0]:
                pk_ids = pk_ids.select(F.col(pk_ids.columns[0]).alias(id_col))

        combos = pk_ids.crossJoin(timeline_df)

        # broadcast se porta-retratos < 100 k linhas
        if pk_ids.count() < 1e5:
            combos = F.broadcast(combos)

        result = combos
        # -----------------------------------------------------------------
        # Agrupamento por fonte para minimizar leituras
        # -----------------------------------------------------------------
        feats_by_src: Dict[str, List[FeatureDefinition]] = {}
        for ft in feats:
            fd = _feature_registry[ft]
            feats_by_src.setdefault(fd.source_table, []).append(fd)

        feature_cols = []
        for source_table, fd_list in feats_by_src.items():
            src_df = self.spark.table(source_table).select(
                *{fd.id_col for fd in fd_list},
                *{fd.value_col for fd in fd_list if fd.value_col},
                *{fd.start_col for fd in fd_list},
                *{fd.end_col for fd in fd_list},
            )

            for lag in self.lags:
                lag_label = None if lag in (0, "0") else lag
                suffix = interval_suffix(lag_label or 0)
                num, unit = (0, "") if lag_label is None else parse_interval(lag_label)

                # limite inferior de período
                def lower_bound(col):
                    if unit == "w":
                        return F.date_sub(col, num * 7 - 1)
                    elif unit == "d":
                        return F.date_sub(col, num - 1)
                    elif unit == "m":
                        return F.add_months(col, -num)
                    elif unit == "y":
                        return F.add_months(col, -12 * num)
                    return col

                # monta janela temporal para cada feature do grupo
                joined = (
                    src_df.alias("ev")
                    .join(
                        combos.alias("cb"),
                        F.col("ev." + fd_list[0].id_col) == F.col("cb." + id_col),
                        "inner",
                    )
                )

                # seleção SCD2 ou ponto-vigente
                if fd_list[0].scd2 and lag_label is None:
                    time_cond = (
                        (F.col("ev." + fd_list[0].start_col) <= F.col("cb.dreft_sist"))
                        & (
                            F.col("ev." + fd_list[0].end_col).isNull()
                            | (F.col("ev." + fd_list[0].end_col) > F.col("cb.dreft_sist"))
                        )
                    )
                    joined = joined.filter(time_cond)
                elif fd_list[0].scd2:
                    lb = lower_bound(F.col("cb.dreft_sist"))
                    joined = joined.filter(
                        (F.col("ev." + fd_list[0].start_col) >= lb)
                        & (F.col("ev." + fd_list[0].start_col) <= F.col("cb.dreft_sist"))
                    )

                # agrega todas as features desta fonte numa única passagem
                agg_exprs = []
                for fd in fd_list:
                    out_col = fd.name + suffix
                    if fd.agg == "sum":
                        agg_exprs.append(F.sum(F.col("ev." + fd.value_col)).alias(out_col))
                    elif fd.agg == "max":
                        agg_exprs.append(F.max(F.col("ev." + fd.value_col)).alias(out_col))
                    elif fd.agg == "count":
                        agg_exprs.append(F.count(F.col("ev." + fd.id_col)).alias(out_col))
                    elif fd.agg == "custom" and fd.custom_fn:
                        # custom_fn deve retornar DataFrame id_col,dreft_sist,out_col
                        custom_df = fd.custom_fn(self.spark, combos, lag_label)
                        result = result.join(custom_df, [id_col, "dreft_sist"], "left")
                        continue
                    feature_cols.append(out_col)

                aggregated = (
                    joined.groupBy("cb." + id_col, "cb.dreft_sist").agg(*agg_exprs)
                )
                result = result.join(
                    aggregated,
                    on=[id_col, "dreft_sist"],
                    how="left",
                )

        result = result.fillna(0, subset=feature_cols)
        return result

    # ---------------------------------------------------------------------
    # Geração de DDL
    # ---------------------------------------------------------------------
    def ddl(
        self,
        df: DataFrame,
        table_name: str,
        *,
        pk_cols: List[str],
        table_comment: str = "Tabela de features autorregressivas.",
    ) -> str:
        """
        Produz string DDL com `COMMENT ON` pronta para Unity Catalog.&#8203;:contentReference[oaicite:13]{index=13}
        """
        col_defs = []
        for field in df.schema:
            dtype = field.dataType.simpleString()
            comment = (
                _feature_registry.get(field.name, None).description
                if field.name in _feature_registry
                else f"Coluna {field.name}"
            )
            col_defs.append(f"  `{field.name}` {dtype} COMMENT '{comment}'")
        cols = ",\n".join(col_defs)
        pk = ", ".join(pk_cols)
        ddl = f"""CREATE TABLE IF NOT EXISTS {table_name} (
{cols},
  PRIMARY KEY ({pk})
)
COMMENT '{table_comment}';"""
        return ddl


# --------------------------------------- exemplo de uso --------------------------------------
if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()

    eng = Features(spark, freq="1m")
    df_features = eng.compute(
        start_date="2024-01-01",
        end_date="2024-03-31",
        features=["vsoma_rtrit_reneg_atvo", "nrtrit_reneg_atvo"],
    )
    df_features.show()

    print(eng.ddl(df_features, "analitica.tbl_features", pk_cols=["ccpf_cnpj", "dreft_sist"]))
