from pyspark.sql import functions as F
from pyspark.sql.window import Window
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import re

class Features:
    def __init__(self):
        self._features = {
            'vsoma_rtrit_reneg_atvo': self._vsoma_rtrit_reneg_atvo,
            'vmax_grau_svrdade_rtrit_reneg_atvo': self._vmax_grau_svrdade_rtrit_reneg_atvo,
            'nrtrit_reneg_atvo': self._nrtrit_reneg_atvo,
        }

    def list(self):
        return list(self._features.keys())

    def _parse_offset(self, offset):
        """Converte string tipo '2w' para timedelta ou relativedelta."""
        if offset == 0:
            return lambda x: x
        match = re.match(r"(\d+)([dwmy])", str(offset))
        val, unit = int(match.group(1)), match.group(2)
        if unit == 'd':
            return lambda dt: dt - timedelta(days=val)
        elif unit == 'w':
            return lambda dt: dt - timedelta(weeks=val)
        elif unit == 'm':
            return lambda dt: dt - relativedelta(months=val)
        elif unit == 'y':
            return lambda dt: dt - relativedelta(years=val)
        else:
            raise ValueError(f"Unidade de tempo não reconhecida: {offset}")

    def _generate_ref_dates(self, dref_inic, dref_ultma, freq='1w'):
        freq_offset = self._parse_offset(freq)
        data = []
        current = dref_inic
        while current <= dref_ultma:
            data.append(current)
            current = freq_offset(current)
        return data

    def _build_window_filter(self, dreft_sist, lag_offset):
        lag_start = self._parse_offset(lag_offset)(dreft_sist)
        return (F.col('__START_AT') <= dreft_sist) & (F.col('__END_AT') > lag_start)

    def compute(self, features, pk_ids, dtime_col='dreft_sist', dtime_inicial='2025-03-01', freq='1w', lags=[0, '2w', '1m']):
        dref_inic = datetime.strptime(dtime_inicial, '%Y-%m-%d')
        dref_ultma = datetime.today()
        ref_dates = self._generate_ref_dates(dref_inic, dref_ultma, freq)

        all_results = []

        for dreft in ref_dates:
            base_df = pk_ids.withColumn(dtime_col, F.lit(dreft))

            for feature in features:
                for lag in lags:
                    lag_start = self._parse_offset(lag)(dreft)
                    lag_filter = (F.col('__START_AT') <= dreft) & (F.col('__END_AT') > lag_start)
                    df_feat = self._features[feature](dreft, lag)
                    df_feat = df_feat.withColumn(dtime_col, F.lit(dreft))
                    base_df = base_df.join(df_feat, on=['ccpf_cnpj', dtime_col], how='left')

            all_results.append(base_df)

        return reduce(lambda a, b: a.unionByName(b), all_results)

    # Exemplos de implementações de features
    def _vsoma_rtrit_reneg_atvo(self, dreft, lag):
        # Simule aqui sua lógica para filtrar e somar valores
        return spark.table('your_source_table') \
            .filter(self._build_window_filter(dreft, lag)) \
            .groupBy('ccpf_cnpj') \
            .agg(F.sum('valor').alias(self._lag_name('vsoma_rtrit_reneg_atvo', lag)))

    def _vmax_grau_svrdade_rtrit_reneg_atvo(self, dreft, lag):
        return spark.table('your_source_table') \
            .filter(self._build_window_filter(dreft, lag)) \
            .groupBy('ccpf_cnpj') \
            .agg(F.max('grau_severidade').alias(self._lag_name('vmax_grau_svrdade_rtrit_reneg_atvo', lag)))

    def _nrtrit_reneg_atvo(self, dreft, lag):
        return spark.table('your_source_table') \
            .filter(self._build_window_filter(dreft, lag)) \
            .groupBy('ccpf_cnpj') \
            .agg(F.count('*').alias(self._lag_name('nrtrit_reneg_atvo', lag)))

    def _lag_name(self, feature_name, lag):
        if lag == 0:
            return feature_name
        units = {'d': 'dia', 'w': 'semna', 'm': 'mes', 'y': 'ano'}
        match = re.match(r"(\d+)([dwmy])", str(lag))
        return f"{feature_name}_ultim_{match.group(1)}{units[match.group(2)]}"