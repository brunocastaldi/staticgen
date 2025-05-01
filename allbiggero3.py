# ============================================================================
# utils.py
# ============================================================================
"""utils.py
Módulo com funções utilitárias para manipulação de datas/intervalos e geração de
códigos auxiliares. Todas as funções são puras e podem ser reutilizadas em outros
contextos sem dependências externas além de *pyspark* e *python‑dateutil*.

Todas as docstrings seguem o padrão *numpydoc* em PT‑BR.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Dict, Tuple

import pyspark.sql.functions as F
from dateutil.relativedelta import relativedelta
from pyspark.sql.column import Column

__all__ = [
    "_NUM_TO_WORD_PT",
    "_UNIT_WORD",
    "parse_interval",
    "interval_suffix",
    "spark_lower_bound",
    "adjust_business_day",
    "generate_ddl",
]

# ---------------------------------------------------------------------------
# Dicionários corporativos padrão (mantidos conforme legado da companhia)
# ---------------------------------------------------------------------------
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

_UNIT_WORD: Dict[str, str] = {"d": "dia", "w": "smnal", "m": "mes", "y": "ano"}

# ---------------------------------------------------------------------------
# Funções públicas
# ---------------------------------------------------------------------------

def parse_interval(interval: str | int) -> Tuple[int, str]:
    """Interpreta uma string numérica‑temporal (``"7d"``, ``"2w"``, etc.).

    Parameters
    ----------
    interval : str or int
        * Se ``int`` ou string representando inteiro ``0`` indica ausência de
          deslocamento temporal (lag=0).
        * Caso string, obrigatoriamente no formato ``<int><unidade>`` onde
          ``unidade`` ∈ {``d`` (dia), ``w`` (semana), ``m`` (mês), ``y`` (ano)}.

    Returns
    -------
    tuple
        ``(quantidade, unidade)`` onde ``unidade`` é sempre minúscula.

    Examples
    --------
    >>> parse_interval("3m")
    (3, "m")
    >>> parse_interval(0)
    (0, "")
    """
    if isinstance(interval, int) or interval in {0, "0"}:
        return int(interval), ""
    digits = "".join(filter(str.isdigit, interval))
    letters = "".join(filter(str.isalpha, interval)).lower()
    if not digits or letters not in {"d", "w", "m", "y"}:
        raise ValueError(f"Intervalo inválido: {interval!r}")
    return int(digits), letters


def interval_suffix(interval: str | int | None) -> str:
    """Gera sufixo em PT‑BR padronizado para colunas de features.

    A convenção corporativa estabelece o prefixo ``"_ultim_"`` seguido do valor
    numérico por extenso (``_NUM_TO_WORD_PT``) concatenado à unidade curta em
    ``_UNIT_WORD``.

    Parameters
    ----------
    interval : str or int or None
        Deslocamento temporal solicitado. ``None`` ou ``0`` → string vazia.

    Returns
    -------
    str
        Sufixo normalizado (começando por sublinhado) ou string vazia.

    Examples
    --------
    >>> interval_suffix("7d")
    "_ultim_sete_dia"
    >>> interval_suffix(0)
    ""
    """
    if interval in {None, 0, "0"}:
        return ""
    qtd, unit = parse_interval(interval)
    extenso = _NUM_TO_WORD_PT.get(qtd, str(qtd))
    return f"_ultim_{extenso}_{_UNIT_WORD[unit]}"


def spark_lower_bound(ref_col: Column, interval: str | int) -> Column:
    """Cria expressão Spark que retorna a data inferior do intervalo.

    Esta função é *lazy* e compatível com *Spark SQL*; não executa ações.

    Parameters
    ----------
    ref_col : pyspark.sql.column.Column
        Coluna de data/hora usada como referência superior.
    interval : str or int
        Intervalo no formato aceito por :pyfunc:`parse_interval`.

    Returns
    -------
    pyspark.sql.column.Column
        Coluna representando *ref_col - (intervalo‑1)*.
    """
    qtd, unit = parse_interval(interval)
    if qtd == 0:
        return ref_col  # limite inferior == limite superior
    if unit == "d":
        return F.date_sub(ref_col, qtd - 1)
    if unit == "w":
        return F.date_sub(ref_col, 7 * qtd - 1)
    if unit == "m":
        return F.add_months(ref_col, -qtd)
    if unit == "y":
        return F.add_months(ref_col, -12 * qtd)
    raise ValueError(f"Unidade temporal não reconhecida: {unit}")


def adjust_business_day(ref_date: date, rule: str = "first") -> date:
    """Ajusta ``ref_date`` para um dia útil baseado em ``rule``.

    A função não considera feriados; para calendários avançados, integrar com
    *pandas_market_calendars* ou API da B3.

    Parameters
    ----------
    ref_date : datetime.date
        Data original.
    rule : {"first", "previous", "next"}, default ``"first"``
        Estratégia de ajuste: primeiro dia útil do mês/semana (``"first"``),
        dia útil imediatamente anterior (``"previous"``) ou posterior
        (``"next"``).

    Returns
    -------
    datetime.date
        Data ajustada.
    """
    weekday = ref_date.weekday()  # 0=segunda … 6=domingo
    if rule == "first":
        # primeiro dia útil ⇒ se sábado (5) ou domingo (6) avança para segunda
        if weekday == 5:
            return ref_date.replace(day=ref_date.day + 2)
        if weekday == 6:
            return ref_date.replace(day=ref_date.day + 1)
        return ref_date
    if rule == "previous":
        if weekday == 5:
            return ref_date.replace(day=ref_date.day - 1)
        if weekday == 6:
            return ref_date.replace(day=ref_date.day - 2)
        return ref_date
    if rule == "next":
        if weekday == 5:
            return ref_date.replace(day=ref_date.day + 2)
        if weekday == 6:
            return ref_date.replace(day=ref_date.day + 1)
        return ref_date
    raise ValueError(f"Regra de ajuste não suportada: {rule}")


def generate_ddl(
    schema: "pyspark.sql.types.StructType",
    table_name: str,
    pk_cols: list[str],
    table_comment: str | None = None,
) -> str:
    """Gera código DDL em *Databricks SQL* para criação de tabela Delta.

    Parameters
    ----------
    schema : pyspark.sql.types.StructType
        Schema da *Spark DataFrame*.
    table_name : str
        Nome da tabela a ser criada.
    pk_cols : list of str
        Lista de colunas que compõem a *primary key*.
    table_comment : str, optional
        Comentário de descrição para a tabela.

    Returns
    -------
    str
        Código SQL completo.
    """
    cols_ddl = []
    for field in schema.fields:
        comment = field.metadata.get("comment", "")
        comment_sql = f" COMMENT '{comment}'" if comment else ""
        cols_ddl.append(f"  {field.name} {field.dataType.simpleString()}{comment_sql}")
    pk_sql = f",\n  PRIMARY KEY({', '.join(pk_cols)})" if pk_cols else ""
    comment_sql = f" COMMENT '{table_comment}'" if table_comment else ""
    ddl = f"""CREATE TABLE IF NOT EXISTS {table_name} (
{',\n'.join(cols_ddl)}{pk_sql}
){comment_sql}\nUSING DELTA;"""
    return ddl

# ============================================================================
# registry.py
# ============================================================================
"""registry.py
Infraestrutura de registro dinâmico de *features*.

A cada nova *feature* definida via *decorator* ``@register_feature`` os metadados
são adicionados ao *singleton* :class:`FeatureRegistry` permitindo descoberta e
uso dinâmico sem intervenção manual na classe de engine.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Callable, Dict, List, Mapping, Optional

__all__ = [
    "FeatureMeta",
    "FeatureRegistry",
    "register_feature",
]


@dataclass(frozen=True)
class FeatureMeta:
    """Metadados imutáveis de uma *feature*.

    Attributes
    ----------
    name : str
        Nome curto, único, usado como coluna no *DataFrame* de saída.
    source_table : str
        Nome lógico da tabela de origem (Spark *catalog* ou *DataFrame* registrado
        no Engine via ``source_tables``).
    agg : {"sum", "max", "count", "avg", "min"}
        Tipo de agregação SQL utilizada.
    column : str | None
        Coluna alvo da agregação. ``None`` para ``count``.
    description : str
        Descrição em PT‑BR.
    scd2 : bool, default ``True``
        Indica se a tabela é do tipo SCD 2.
    start_col : str, default ``"__START_AT"``
    end_col : str, default ``"__END_AT"``
    extra_filter : str | None, optional
        Filtro SQL adicional aplicado ANTES da agregação.
    """

    name: str
    source_table: str
    agg: str
    column: Optional[str] = None
    description: str = ""
    scd2: bool = True
    start_col: str = "__START_AT"
    end_col: str = "__END_AT"
    extra_filter: Optional[str] = None
    # Campos derivados ------------------------------------------------------------------
    func: Optional[Callable] = field(default=None, repr=False, compare=False)

    # ---------------------------------------------------------------------
    # Helper API
    # ---------------------------------------------------------------------
    def to_dict(self) -> Mapping[str, str]:
        """Retorna mapeamento somente‑leitura dos metadados."""
        return MappingProxyType(self.__dict__)


class FeatureRegistry:
    """Singleton de registro de *features* corporativas."""

    _REG: Dict[str, FeatureMeta] = {}

    # ------------------------ API pública ---------------------------------
    @classmethod
    def register(cls, meta: FeatureMeta):
        if meta.name in cls._REG:
            raise ValueError(f"Feature já registrada: {meta.name}")
        cls._REG[meta.name] = meta

    @classmethod
    def get(cls, name: str) -> FeatureMeta:
        return cls._REG[name]

    @classmethod
    def list(cls) -> List[str]:
        return list(cls._REG.keys())

    @classmethod
    def describe(cls, name: str) -> str:
        meta = cls.get(name)
        return meta.description

    @classmethod
    def all(cls) -> Mapping[str, FeatureMeta]:
        return MappingProxyType(cls._REG)


# ---------------------------------------------------------------------------
# Decorator "register_feature" — usado pelos cientistas de dados
# ---------------------------------------------------------------------------

def register_feature(
    *,
    name: str,
    source_table: str,
    agg: str,
    column: str | None = None,
    description: str = "",
    scd2: bool = True,
    start_col: str = "__START_AT",
    end_col: str = "__END_AT",
    extra_filter: str | None = None,
):
    """Decorator que registra a função de cálculo (opcional) e seus metadados.

    A própria função decorada *pode* implementar lógica complexa de *feature*
    quando ``agg`` não é suficiente (ex.: métricas de NLP). O Engine inspecciona
    ``FeatureMeta.func`` para decidir se executa agregação padrão ou lógica
    customizada.
    """

    def _decorator(func: Callable | None):
        meta = FeatureMeta(
            name=name,
            source_table=source_table,
            agg=agg,
            column=column,
            description=description or (inspect.getdoc(func) or ""),
            scd2=scd2,
            start_col=start_col,
            end_col=end_col,
            extra_filter=extra_filter,
            func=func,
        )
        FeatureRegistry.register(meta)
        return func

    return _decorator


# ---------------------------------------------------------------------------
# *Features* de exemplo pré‑registradas -------------------------------------
# ---------------------------------------------------------------------------

@register_feature(
    name="vsoma_rtrit_reneg_atvo",
    source_table="tb_rtrit_reneg",
    agg="sum",
    column="valor_rtrit_reneg_atvo",
    description="Soma dos valores de renegociações ativas.",
)
def _vsoma_placeholder(df):
    return df  # Funcionalidade padrão via "agg", não será chamada.


@register_feature(
    name="vmax_grau_svrdade_rtrit_reneg_atvo",
    source_table="tb_rtrit_reneg",
    agg="max",
    column="grau_svrdade_rtrit_reneg_atvo",
    description="Valor máximo do grau de severidade entre renegociações ativas.",
)
def _vmax_placeholder(df):
    return df


@register_feature(
    name="nrtrit_reneg_atvo",
    source_table="tb_rtrit_reneg",
    agg="count",
    column=None,
    description="Contagem de renegociações ativas.",
)
def _count_placeholder(df):
    return df

# ============================================================================
# engine.py
# ============================================================================
"""engine.py

Camada de orquestração *lazy* que combina tabelas de origem, *features* do
:pyclass:`registry.FeatureRegistry` e parâmetros do usuário para gerar, de forma
imóvel (*immutable*), um *DataFrame* final com *snapshots* autorregressivos.

A classe expõe um contrato simples:

* :pyfunc:`FeaturesEngine.compute` – gera o *DataFrame* conforme parâmetros.
* :pyfunc:`FeaturesEngine.generate_ddl` – retorna string SQL pronta.

Exemplo mínimo
--------------
>>> from pyspark.sql import SparkSession
>>> from engine import FeaturesEngine
>>> spark = SparkSession.builder.getOrCreate()
>>> engine = FeaturesEngine(spark, source_tables={"tb_rtrit_reneg": spark.table("silver.tb_rtrit_reneg")})
>>> df = engine.compute(features=["vsoma_rtrit_reneg_atvo"], pk_ids=None,
...                      start="2023-01-01", end="2024-12-31", freq="1m")
>>> df.show()
"""

from __future__ import annotations

import itertools
from datetime import date, datetime
from typing import Dict, Iterable, List, Sequence

import pyspark.sql.functions as F
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType

from utils import (
    adjust_business_day,
    generate_ddl,
    interval_suffix,
    parse_interval,
    spark_lower_bound,
)
from registry import FeatureRegistry, FeatureMeta

__all__ = ["FeaturesEngine"]


class FeaturesEngine:
    """Motor de cálculo autorregressivo de *features* Spark.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Sessão Spark ativa.
    source_tables : dict[str, pyspark.sql.DataFrame]
        Mapeamento nome → DataFrame já carregado. Tabelas ausentes são
        acessadas via ``spark.table(name)`` *on‑demand*.
    dtime_col : str, default ``"dreft_sist"``
        Nome da coluna de data de referência no *DataFrame* final.
    timezone : str, default ``"America/Sao_Paulo"``
        Timezone configurado para ``spark.sql.session.timeZone``.
    """

    def __init__(
        self,
        spark: SparkSession,
        *,
        source_tables: Dict[str, DataFrame] | None = None,
        dtime_col: str = "dreft_sist",
        timezone: str = "America/Sao_Paulo",
    ):
        self.spark = spark
        self.dtime_col = dtime_col
        self.spark.conf.set("spark.sql.session.timeZone", timezone)
        self._tbl_cache: Dict[str, DataFrame] = source_tables or {}

    # ------------------------------------------------------------------
    # API pública de alto nível
    # ------------------------------------------------------------------
    def list_features(self) -> List[str]:
        """Lista de *features* disponíveis no *registry*."""
        return FeatureRegistry.list()

    # ------------------------------------------------------------------
    def compute(
        self,
        *,
        features: Sequence[str],
        pk_ids: DataFrame | None = None,
        start: str | date | None = None,
        end: str | date | None = None,
        freq: str = "1m",
        lags: Sequence[str | int] | None = None,
        business_day_rule: str | None = None,
    ) -> DataFrame:
        """Computa *features* e retorna ``DataFrame``.

        Parameters
        ----------
        features : list[str]
            Nome das *features* registradas.
        pk_ids : DataFrame, optional
            DataFrame contendo somente a coluna *PK* (mesmo nome usado nas
            tabelas de origem). ``None`` → combinação de *IDs* de todas as
            tabelas envolvidas.
        start, end : str or datetime.date, optional
            Período de datas de referência. Se omitido, usa ``end = today`` e
            ``start = end``.
        freq : str, default ``"1m"``
            Frequência entre datas sequenciais do *snapshot*.
        lags : list[str | int], optional
            Conjunto de intervalos autorregressivos. ``None`` → ``[0, "1m",
            "3m", "6m", "1y"]``.
        business_day_rule : {"first", "previous", "next"}, optional
            Ajusta cada data de referência resultante para dia útil.

        Returns
        -------
        pyspark.sql.DataFrame
            Colunas: *PK*, ``dtime_col`` e cada *feature*+sufixo.
        """
        if not features:
            raise ValueError("Favor informar pelo menos 1 feature para cálculo.")
        unknown = set(features) - set(self.list_features())
        if unknown:
            raise ValueError(f"Features desconhecidas: {sorted(unknown)}")
        lags = list(lags or [0, "1m", "3m", "6m", "1y"])

        # ----------------------------------------------------------------
        # Construção da "timeline" -----------------------------------------------------
        # ----------------------------------------------------------------
        end = end or date.today()
        start = start or end
        if isinstance(start, (datetime, date)):
            start = str(start)
        if isinstance(end, (datetime, date)):
            end = str(end)
        timeline = self._generate_timeline(start, end, freq)
        if business_day_rule:
            adjust_udf = F.udf(lambda d: adjust_business_day(d, rule=business_day_rule))
            timeline = timeline.withColumn(self.dtime_col, adjust_udf(F.col(self.dtime_col)))

        # ----------------------------------------------------------------
        # DataFrame base de IDs × datas ----------------------------------
        # ----------------------------------------------------------------
        if pk_ids is None:
            ids_df = self._collect_ids(features)
        else:
            ids_df = pk_ids.select(pk_ids.columns[0]).distinct()
        base = ids_df.crossJoin(timeline)

        # ----------------------------------------------------------------
        # Agrupar features por tabela de origem → otimizar leituras -------
        # ----------------------------------------------------------------
        by_table: Dict[str, List[FeatureMeta]] = {}
        for name in features:
            meta = FeatureRegistry.get(name)
            by_table.setdefault(meta.source_table, []).append(meta)

        result = base
        feature_cols: List[str] = []

        for table_name, metas in by_table.items():
            src_df = self._load_source(table_name)
            for lag in lags:
                suffix = interval_suffix(lag)
                lower_col_expr = spark_lower_bound(F.col(self.dtime_col), lag)

                # Filtra registros necessários uma única vez -----------------
                cond = (F.col(meta.start_col) <= F.col(self.dtime_col)) & (
                    F.col(meta.end_col).isNull() | (F.col(meta.end_col) > F.col(self.dtime_col))
                ) if metas[0].scd2 and (lag in {0, "0"}) else (
                    (F.col(meta.start_col) >= lower_col_expr) & (F.col(meta.start_col) <= F.col(self.dtime_col))
                )
                filtered = (
                    src_df.join(base, src_df[metas[0].start_col].isNotNull(), "right")
                    .where(cond)
                )

                # Aplica extra_filter se existir (idéntica para todas as metas da tabela)
                if metas[0].extra_filter:
                    filtered = filtered.filter(metas[0].extra_filter)

                group_cols = [F.col(ids_df.columns[0]).alias(ids_df.columns[0]), F.col(self.dtime_col)]
                agg_exprs = []
                for meta in metas:
                    out_col = meta.name + suffix
                    feature_cols.append(out_col)
                    if meta.func is not None and meta.agg == "custom":
                        # Lógica especial delegada ao usuário --------------------------------
                        feat_df = meta.func(filtered, lag=lag, ref_col=self.dtime_col)
                        result = result.join(feat_df, on=group_cols, how="left")
                        continue
                    if meta.agg == "sum":
                        agg_exprs.append(F.sum(meta.column).alias(out_col))
                    elif meta.agg == "max":
                        agg_exprs.append(F.max(meta.column).alias(out_col))
                    elif meta.agg == "count":
                        agg_exprs.append(F.count("*").alias(out_col))
                    elif meta.agg == "avg":
                        agg_exprs.append(F.avg(meta.column).alias(out_col))
                    elif meta.agg == "min":
                        agg_exprs.append(F.min(meta.column).alias(out_col))
                    else:
                        raise ValueError(f"Agregação não suportada: {meta.agg}")

                if agg_exprs:
                    agg_df = filtered.groupBy(*group_cols).agg(*agg_exprs)
                    result = result.join(agg_df, on=group_cols, how="left")

        # ----------------------------------------------------------------
        # Pós‑processamento final -----------------------------------------
        # ----------------------------------------------------------------
        result = result.fillna(0, subset=feature_cols)
        return result

    # ------------------------------------------------------------------
    def generate_ddl(
        self,
        df: DataFrame,
        *,
        table_name: str,
        table_comment: str | None = None,
    ) -> str:
        """Gera DDL *Databricks SQL* para ``df``.

        Inclui ``dreft_sist`` como *primary key* em conjunto com coluna de **ID**.
        """
        pk = [df.columns[0], self.dtime_col]
        ddl = generate_ddl(df.schema, table_name, pk, table_comment)
        return ddl

    # ------------------------------------------------------------------
    # Métodos privados helpers -----------------------------------------
    # ------------------------------------------------------------------
    def _generate_timeline(self, start: str, end: str, freq: str) -> DataFrame:
        num, unit = parse_interval(freq)
        if unit == "":
            raise ValueError("freq não pode ser 0")
        spark = self.spark
        expr = (
            F.expr(f"interval {num} {'days' if unit=='d' else 'months' if unit=='m' else 'weeks' if unit=='w' else 'years'}")
        )
        timeline = spark.range(1).select(
            F.explode(
                F.sequence(F.to_date(F.lit(start)), F.to_date(F.lit(end)), expr)
            ).alias(self.dtime_col)
        )
        return timeline

    def _collect_ids(self, features: Iterable[str]) -> DataFrame:
        """Coleta IDs únicos de todas as tabelas envolvidas."""
        tables = {FeatureRegistry.get(f).source_table for f in features}
        dfs = [self._load_source(t).select(F.col(list(self._load_source(t).columns)[0]).alias("id")) for t in tables]
        return functools.reduce(DataFrame.unionByName, dfs).distinct().toDF(dfs[0].columns[0])

    def _load_source(self, name: str) -> DataFrame:
        if name not in self._tbl_cache:
            self._tbl_cache[name] = self.spark.table(name)
        return self._tbl_cache[name]
