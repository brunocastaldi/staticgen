# Module: features.py
# Módulo integrado de cálculo de features autorregressivas (SCD Tipo 2)
# com registro automático e correções de data/timezone.

from pyspark.sql import DataFrame, SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, StringType, DateType, DoubleType, IntegerType
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
import re

# --- Utilitários de datas ---
def _parse_frequency(freq: str) -> relativedelta:
    """
    Converte string de frequência ('7d','1m','2w','1y') em um objeto relativedelta.
    """
    m = re.match(r"^(\d+)([dwmy])$", freq)
    if not m:
        raise ValueError(f"Formato de frequência inválido: '{freq}'")
    val, unit = int(m.group(1)), m.group(2)
    if unit == 'd': return relativedelta(days=val)
    if unit == 'w': return relativedelta(weeks=val)
    if unit == 'm': return relativedelta(months=val)
    if unit == 'y': return relativedelta(years=val)
    raise ValueError(f"Unidade de frequência não suportada: '{unit}'")

def _to_timezone(dt: datetime, tz: str) -> datetime:
    """
    Converte datetime ingênuo ou timezone-aware para o fuso especificado.
    """
    target = pytz.timezone(tz)
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(target)

def _adjust_ref_date(ref: datetime, mode: str) -> datetime:
    """
    Ajusta data de referência para:
      - 'month': primeiro dia útil do mês.
      - 'week' : primeiro dia útil da semana (segunda-feira).
      - dia da semana (ex: 'Monday'): próximo dia correspondente.
    """
    if mode == 'week':
        base = ref - timedelta(days=ref.weekday())
    elif mode == 'month':
        base = ref.replace(day=1)
    elif mode in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']:
        base = ref
        weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        target = weekdays.index(mode)
        while base.weekday() != target:
            base += timedelta(days=1)
    else:
        return ref
    while base.weekday() >= 5:  # 5=Sábado,6=Domingo
        base += timedelta(days=1)
    return base

def _generate_ref_dates(start: datetime, end: datetime, freq: str) -> list:
    """
    Gera sequência de datas de referência entre start e end, usando freq.
    """
    delta = _parse_frequency(freq)
    dates = []
    cur = start
    while cur <= end:
        dates.append(cur)
        cur += delta
    return dates

# --- Definição de metadata de cada feature ---
class FeatureDefinition:
    """
    Metadados de uma feature autorregressiva.
    """
    def __init__(self, name: str, func, source_table: str,
                 id_col: str, start_col: str, end_col: str,
                 required_cols: list, description: str):
        self.name          = name
        self.func          = func
        self.source_table  = source_table
        self.id_col        = id_col
        self.start_col     = start_col
        self.end_col       = end_col
        self.required_cols = required_cols
        self.description   = description

class FeatureRegistry:
    """
    Container de FeatureDefinition, com agrupamento por origem.
    """
    def __init__(self):
        self._defs = {}

    def register_def(self, fd: FeatureDefinition):
        self._defs[fd.name] = fd

    def list_defs(self) -> list:
        return list(self._defs.keys())

    def get_def(self, name: str) -> FeatureDefinition:
        if name not in self._defs:
            raise KeyError(f"Feature não registrada: '{name}'")
        return self._defs[name]

    def group_by_source(self, feature_names: list) -> dict:
        groups = {}
        for nm in feature_names:
            fd = self.get_def(nm)
            key = (fd.source_table, fd.start_col, fd.end_col)
            groups.setdefault(key, []).append(fd)
        return groups

# --- Classe principal de cálculo ---
class Features:
    """
    Motor principal para cálculo de features autorregressivas.
    """
    def __init__(self, spark: SparkSession, timezone: str = 'UTC'):
        """
        Parâmetros
        ----------
        spark    : SparkSession — sessão Spark.
        timezone : str          — fuso para ajuste de datas (ex: 'America/Sao_Paulo').
        """
        self.spark      = spark
        self.registry   = FeatureRegistry()
        self.timezone   = timezone
        self._auto_register_defaults()

    def _auto_register_defaults(self):
        """
        Registra automaticamente as features padrão.
        """
        # Exemplo de registros padrão, basta adaptar source_table
        self.register(
            name='vsoma_rtrit_reneg_atvo',
            func=lambda df, idc, sw, ew: df.groupBy(idc)
                                          .agg(F.sum('valor_rtrit_reneg_atvo')
                                          .alias('vsoma_rtrit_reneg_atvo')),
            source_table='catalogo.esquema.table_reneg',
            id_col='ccpf_cnpj',
            start_col='__START_AT',
            end_col='__END_AT',
            required_cols=['valor_rtrit_reneg_atvo'],
            description='Soma de valores de renegociações ativas'
        )
        self.register(
            name='vmax_grau_svrdade_rtrit_reneg_atvo',
            func=lambda df, idc, sw, ew: df.groupBy(idc)
                                          .agg(F.max('grau_svrdade_rtrit_reneg_atvo')
                                          .alias('vmax_grau_svrdade_rtrit_reneg_atvo')),
            source_table='catalogo.esquema.table_reneg',
            id_col='ccpf_cnpj',
            start_col='__START_AT',
            end_col='__END_AT',
            required_cols=['grau_svrdade_rtrit_reneg_atvo'],
            description='Máximo grau de severidade'
        )
        self.register(
            name='nrtrit_reneg_atvo',
            func=lambda df, idc, sw, ew: df.groupBy(idc)
                                          .agg(F.count(idc).alias('nrtrit_reneg_atvo')),
            source_table='catalogo.esquema.table_reneg',
            id_col='ccpf_cnpj',
            start_col='__START_AT',
            end_col='__END_AT',
            required_cols=[],
            description='Contagem de renegociações ativas'
        )

    def register(self, name: str, func, source_table: str,
                 id_col: str, start_col: str, end_col: str,
                 required_cols: list, description: str):
        """
        Registra definição de uma feature.
        """
        fd = FeatureDefinition(name, func, source_table,
                               id_col, start_col, end_col,
                               required_cols, description)
        self.registry.register_def(fd)

    def list(self) -> list:
        """Lista todas as features registradas."""
        return self.registry.list_defs()

    def compute(self,
                feature_names: list = None,
                dtime_inicial: str = None,
                dtime_final: str = None,
                freq: str = '1m',
                lags: list = [0],
                adjust_ref: str = None,
                pk_ids: DataFrame = None) -> DataFrame:
        """
        Computa automaticamente todas (ou selecionadas) as features.

        Parâmetros
        ----------
        feature_names : list, opcional
            Lista de nomes de features (None => todas).
        dtime_inicial : str, opcional
            'YYYY-MM-DD' (None => hoje − freq).
        dtime_final   : str, opcional
            'YYYY-MM-DD' (None => hoje).
        freq          : str, opcional
            Frequência de referência (ex: '1m','7d').
        lags          : list, opcional
            Lags a aplicar (0 ou 'Xd','Xw','Xm').
        adjust_ref    : str, opcional
            Ajuste de datas ('month','week','Monday',...).
        pk_ids        : DataFrame, opcional
            IDs primários (None => coleta todos automaticamente).

        Retorna
        -------
        DataFrame
            Resultado com colunas [id_col, dreft_sist, <features>].
        """
        # determina intervalo de datas
        now     = datetime.utcnow()
        end_dt  = datetime.strptime(dtime_final, "%Y-%m-%d") if dtime_final else _to_timezone(now, self.timezone)
        start_dt= (datetime.strptime(dtime_inicial, "%Y-%m-%d")
                   if dtime_inicial else end_dt - _parse_frequency(freq))
        refs    = _generate_ref_dates(start_dt, end_dt, freq)
        if adjust_ref:
            refs = [_adjust_ref_date(d, adjust_ref) for d in refs]

        # base de IDs x datas
        if pk_ids is None:
            all_ids = None
            for nm in (feature_names or self.list()):
                fd    = self.registry.get_def(nm)
                tmp   = self.spark.table(fd.source_table).select(fd.id_col).distinct()
                all_ids = tmp if all_ids is None else all_ids.union(tmp)
            base = all_ids.distinct().crossJoin(
                self.spark.createDataFrame([(d.date(),) for d in refs], ['dreft_sist'])
            )
        else:
            base = pk_ids.crossJoin(
                self.spark.createDataFrame([(d.date(),) for d in refs], ['dreft_sist'])
            )
        result = base

        # agrupa por origem e aplica cada feature/lag
        groups = self.registry.group_by_source(feature_names or self.list())
        for (src, sc, ec), fdefs in groups.items():
            cols = {fd.id_col for fd in fdefs} | {sc, ec} | set(sum((fd.required_cols for fd in fdefs), []))
            tbl  = self.spark.table(src).select(*cols)
            for lag in lags:
                for rd in refs:
                    sw = rd if lag in (0,'0') else rd - (lag if isinstance(lag,int) else _parse_frequency(str(lag)))
                    ew = rd
                    window_df = tbl.where(
                        (F.col(sc) <= F.lit(ew)) &
                        ((F.col(ec).isNull()) | (F.col(ec) > F.lit(sw)))
                    )
                    for fd in fdefs:
                        df_feat = fd.func(window_df, fd.id_col, sw, ew)
                        colname = fd.name + ('' if lag in (0,'0') else f"_ultim_{lag}")
                        result  = result.join(
                            df_feat.withColumn('dreft_sist', F.lit(rd.date()))
                                     .withColumnRenamed(fd.name, colname),
                            on=[fd.id_col,'dreft_sist'], how='left'
                        )
        # preenche zeros
        for fn in (feature_names or self.list()):
            for lag in lags:
                col = fn + ('' if lag in (0,'0') else f"_ultim_{lag}")
                result = result.fillna({col: 0})
        return result

    def print_ddl_schema(self, df: DataFrame, table: str, comment: str) -> str:
        """
        Gera DDL CREATE TABLE para o DataFrame resultante.
        """
        lines = [f"CREATE TABLE {table} ("]
        for f in df.schema.fields:
            nm = f.name
            tp = f.dataType.simpleString().upper()
            nn = ' NOT NULL' if nm in ['ccpf_cnpj','dreft_sist'] else ''
            lines.append(f"  {nm} {tp}{nn} COMMENT '{nm} calculado.' ,")
        lines[-1] = lines[-1].rstrip(',')
        lines.append(f") COMMENT '{comment}';")
        return '\n'.join(lines)
