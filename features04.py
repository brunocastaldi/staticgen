from pyspark.sql import DataFrame, functions as F
from datetime import date

class Features:
    """
    Classe PySpark para cálculo de features autorregressivas a partir de tabela SCD Tipo 2.
    
    Esta classe gera features agregadas (soma de valores, máximo de grau de severidade, contagem de registros)
    para períodos de referência ao longo do tempo, com base em registros históricos de vigência (`__START_AT`, `__END_AT`).
    Permite calcular valores pontuais e em janelas móveis (lags) para cada ID primário.
    """
    def __init__(self, df: DataFrame, dtime_col: str, id_col: str,
                 dtime_inicial: str = None, dtime_final: str = None,
                 freq: str = '1m', lags: list = None):
        """
        Inicializa a classe Features com os dados e parâmetros de período.
        
        :param df: DataFrame de entrada contendo os dados históricos (SCD Tipo 2).
        :param dtime_col: Nome da coluna de data de referência (ex.: 'dreft_sist').
        :param id_col: Nome da coluna de ID primário (ex.: 'ccpf_cnpj').
        :param dtime_inicial: Data inicial (YYYY-MM-DD) para início das referências. Se None, usa somente `dtime_final`.
        :param dtime_final: Data final (YYYY-MM-DD) para as referências. Se None, utiliza a data de hoje.
        :param freq: Frequência de geração das datas de referência (ex.: '7d' para 7 dias, '1m' para 1 mês, '1w' para 1 semana).
        :param lags: Lista de lags de tempo para cálculo (ex.: [0, '7d', '2w', '1m', '3m', '6m']). 0 representa o ponto no tempo atual.
        """
        self.df = df
        self.dtime_col = dtime_col
        self.id_col = id_col
        # Definir datas inicial e final (ISO format YYYY-MM-DD)
        self.dtime_inicial = str(dtime_inicial) if dtime_inicial is not None else None
        self.dtime_final = str(dtime_final) if dtime_final is not None else date.today().isoformat()
        # Parâmetros de frequência e lags
        self.freq = freq
        self.lags = lags if lags is not None else [0, '7d', '2w', '1m', '3m', '6m']
        # Definição das features base disponíveis e suas colunas de origem e tipo de agregação
        # Supondo colunas: 'valor_rtrit_reneg_atvo' (valor numérico para soma), 
        # 'grau_svrdade_rtrit_reneg_atvo' (grau de severidade numérico para máximo).
        # Contagem de registros não requer coluna específica (usa o próprio ID).
        self._features_def = {
            'vsoma_rtrit_reneg_atvo': {'agg': 'sum', 'col': 'valor_rtrit_reneg_atvo'},
            'vmax_grau_svrdade_rtrit_reneg_atvo': {'agg': 'max', 'col': 'grau_svrdade_rtrit_reneg_atvo'},
            'nrtrit_reneg_atvo': {'agg': 'count', 'col': None}
        }
    
    def list(self) -> list:
        """
        Retorna a lista de nomes de features base disponíveis (antes da aplicação de lags).
        
        As features base incluem as métricas fundamentais (soma de valores, máximo de grau, contagem de registros).
        Os nomes retornados correspondem às features sem sufixos de intervalo de tempo.
        """
        return list(self._features_def.keys())
    
    def _parse_interval(self, interval: str):
        """
        Analisa a string de intervalo (e.g., '7d', '1m') e retorna uma tupla (numero, unidade).
        Unidade pode ser 'd' (dias), 'w' (semanas), 'm' (meses) ou 'y' (anos).
        """
        num = int(''.join(filter(str.isdigit, interval)))
        unit = ''.join(filter(str.isalpha, interval)).lower()
        return num, unit
    
    def _interval_suffix(self, interval: str) -> str:
        """
        Retorna o sufixo de coluna correspondente ao intervalo especificado.
        Exemplo: '7d' -> '_ultim_7dias'; '2w' -> '_ultim_2semna'; '1m' -> '_ultim_1mes'.
        Para lag 0 (intervalo None), retorna string vazia (sem sufixo).
        """
        if interval is None or interval == 0 or interval == '0':
            return ''
        num, unit = self._parse_interval(interval)
        prefix = "_ultim_"
        if unit == 'd':
            return f"{prefix}{num}dia" if num == 1 else f"{prefix}{num}dias"
        elif unit == 'w':
            return f"{prefix}{num}semna"
        elif unit == 'm':
            return f"{prefix}{num}mes"
        elif unit == 'y':
            return f"{prefix}{num}ano" if num == 1 else f"{prefix}{num}anos"
        else:
            return ''
    
    def _generate_timeline(self, start_date: str, end_date: str, freq: str) -> DataFrame:
        """
        Gera um DataFrame de uma coluna (dtime_col) com todas as datas de referência de start_date até end_date (inclusive),
        obedecendo a frequência definida.
        """
        spark = self.df.sparkSession
        # Converter datas inicial e final para colunas de tipo data
        start_col = F.to_date(F.lit(start_date))
        end_col = F.to_date(F.lit(end_date))
        # Determinar intervalo de frequência para sequence()
        num, unit = self._parse_interval(freq)
        if unit == 'w':
            days = 7 * num
            interval_expr = F.expr(f'interval {days} days')
        elif unit == 'd':
            interval_expr = F.expr(f'interval {num} days')
        elif unit == 'm':
            interval_expr = F.expr(f'interval {num} months')
        elif unit == 'y':
            interval_expr = F.expr(f'interval {num} years')
        else:
            interval_expr = F.expr(f'interval {num} days')
        # Gerar sequência de datas e explodir em linhas
        timeline_df = spark.range(1).select(F.explode(F.sequence(start_col, end_col, interval_expr)).alias(self.dtime_col))
        return timeline_df
    
    def compute(self, features: list, pk_ids: DataFrame = None,
                dtime_col: str = None, dtime_inicial: str = None,
                freq: str = None, lags: list = None) -> DataFrame:
        """
        Computa as features solicitadas para os IDs e período definidos, retornando um DataFrame resultado.
        
        :param features: Lista de features base a calcular (use Features.list() para disponíveis).
        :param pk_ids: DataFrame contendo os IDs primários a considerar (coluna com mesmo nome de id_col). Se None, usa todos IDs em df.
        :param dtime_col: (Opcional) Nome da coluna de data de referência no resultado. Padrão: mesmo nome definido na classe.
        :param dtime_inicial: (Opcional) Data inicial para começo das referências (se diferente da definida na classe).
        :param freq: (Opcional) Frequência de atualização das datas de referência (se diferente da definida na classe).
        :param lags: (Opcional) Lista de lags a calcular (se diferente da definida na classe).
        :return: DataFrame PySpark com colunas [id_col, dtime_col, <features calculadas>].
        
        **Nota:** Colunas de feature no resultado terão sufixos indicando o período quando lag != 0 (por exemplo, `_ultim_2semna`, `_ultim_1mes`).
                 Para lag 0, o nome da coluna permanece igual ao da feature base.
        """
        # Parâmetros efetivos (usa valores da classe se não fornecidos)
        ref_date_col = dtime_col if dtime_col else self.dtime_col
        start_date = str(dtime_inicial) if dtime_inicial is not None else (self.dtime_inicial or self.dtime_final)
        end_date = self.dtime_final
        freq_val = freq if freq is not None else self.freq
        lags_list = [lags] if isinstance(lags, (str, int)) else (lags if lags is not None else self.lags)
        # Gerar DataFrame de datas de referência conforme período e frequência
        timeline_df = self._generate_timeline(start_date, end_date, freq_val).alias("timeline")
        # DataFrame de IDs a considerar
        id_df = pk_ids.alias("ids") if pk_ids is not None else self.df.select(F.col(self.id_col)).distinct().alias("ids")
        # Combinação cruzada IDs x datas de referência
        combos_df = id_df.crossJoin(timeline_df).select(
            F.col(f"ids.{self.id_col}").alias(self.id_col),
            F.col(f"timeline.{self.dtime_col}").alias(self.dtime_col)
        )
        result_df = combos_df  # inicialmente todas combinações possíveis
        # Validar se todas as features solicitadas existem nas definições
        for feat in features:
            if feat not in self._features_def:
                raise ValueError(f"Feature n\u00e3o dispon\u00edvel: {feat}")
        # Calcular cada lag solicitado
        feature_cols = []  # manter rastreamento das colunas de feature adicionadas
        for lag in lags_list:
            interval_label = None if lag == 0 or lag == '0' else str(lag)
            suffix = self._interval_suffix(interval_label)
            # DataFrames auxiliar com alias
            events_df = self.df.alias("event")
            # Selecionar apenas ID e data de referência para junção (evita carregar colunas extras)
            combo_df = result_df.select(self.id_col, self.dtime_col).alias("combo_ref")
            # Condições de junção e filtro temporal
            join_cond = F.col(f"event.{self.id_col}") == F.col(f"combo_ref.{self.id_col}")
            if interval_label is None:
                # Lag 0: registros vigentes na data de referência (start <= date < end ou end nulo)
                time_cond = (
                    (F.col("event.__START_AT") <= F.col(f"combo_ref.{self.dtime_col}")) &
                    (
                        F.col("event.__END_AT").isNull() |
                        (F.col("event.__END_AT") > F.col(f"combo_ref.{self.dtime_col}"))
                    )
                )
            else:
                # Lag em intervalo: registros iniciados entre (data_ref - intervalo + 1) e data_ref (inclusive)
                num, unit = self._parse_interval(interval_label)
                if unit == 'w':
                    lower_bound = F.date_sub(F.col(f"combo_ref.{self.dtime_col}"), 7 * num - 1)
                elif unit == 'd':
                    lower_bound = F.date_sub(F.col(f"combo_ref.{self.dtime_col}"), num - 1)
                elif unit == 'm':
                    lower_bound = F.add_months(F.col(f"combo_ref.{self.dtime_col}"), -num)
                elif unit == 'y':
                    lower_bound = F.add_months(F.col(f"combo_ref.{self.dtime_col}"), -12 * num)
                else:
                    lower_bound = F.date_sub(F.col(f"combo_ref.{self.dtime_col}"), num - 1)
                time_cond = (
                    (F.col("event.__START_AT") >= lower_bound) &
                    (F.col("event.__START_AT") <= F.col(f"combo_ref.{self.dtime_col}"))
                )
            # Junção entre eventos e combinações (por ID) com filtro de tempo
            joined_df = events_df.join(combo_df, join_cond, how="inner").filter(time_cond)
            # Agregar valores conforme cada feature solicitada
            agg_exprs = []
            for feat in features:
                agg_type = self._features_def[feat]['agg']
                col_name = self._features_def[feat]['col']
                out_col = feat + suffix  # nome da coluna de saída com sufixo se aplicável
                if agg_type == 'sum' and col_name:
                    agg_exprs.append(F.sum(F.col(f"event.{col_name}")).alias(out_col))
                elif agg_type == 'max' and col_name:
                    agg_exprs.append(F.max(F.col(f"event.{col_name}")).alias(out_col))
                elif agg_type == 'count':
                    agg_exprs.append(F.count(F.col(f"event.{self.id_col}")).alias(out_col))
                feature_cols.append(out_col)
            aggregated_df = joined_df.groupBy(
                F.col(f"combo_ref.{self.id_col}").alias(self.id_col),
                F.col(f"combo_ref.{self.dtime_col}").alias(self.dtime_col)
            ).agg(*agg_exprs)
            # Juntar agregados ao resultado total (left join mantém combinações sem eventos)
            result_df = result_df.join(aggregated_df, on=[self.id_col, self.dtime_col], how="left")
        # Preencher valores ausentes (NULL) das features com 0
        result_df = result_df.fillna(0, subset=feature_cols)
        # Renomear coluna de data de referência para nome customizado, se especificado
        if dtime_col and dtime_col != self.dtime_col:
            result_df = result_df.withColumnRenamed(self.dtime_col, dtime_col)
        return result_df
