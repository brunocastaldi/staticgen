# Module: register_features.py
# Registra automaticamente todas as funções de feature no objeto Features

from feature_calculators import (
    vsoma_rtrit_reneg_atvo,
    vmax_grau_svrdade_rtrit_reneg_atvo,
    nrtrit_reneg_atvo
)

def registrar_features_default(features_obj):
    """
    Registra no objeto Features todas as funções de features padrão implementadas.
    """
    features_obj.register(
        name="vsoma_rtrit_reneg_atvo",
        func=vsoma_rtrit_reneg_atvo,
        description="Soma dos valores de renegociações restritivas ativas.",
        source_table="catalogo.esquema.table_reneg",
        id_col="ccpf_cnpj",
        start_col="__START_AT",
        end_col="__END_AT",
        required_cols=["valor_rtrit_reneg_atvo"]
    )

    features_obj.register(
        name="vmax_grau_svrdade_rtrit_reneg_atvo",
        func=vmax_grau_svrdade_rtrit_reneg_atvo,
        description="Valor máximo do grau de severidade das renegociações restritivas ativas.",
        source_table="catalogo.esquema.table_reneg",
        id_col="ccpf_cnpj",
        start_col="__START_AT",
        end_col="__END_AT",
        required_cols=["grau_svrdade_rtrit_reneg_atvo"]
    )

    features_obj.register(
        name="nrtrit_reneg_atvo",
        func=nrtrit_reneg_atvo,
        description="Número de ocorrências de renegociações restritivas ativas.",
        source_table="catalogo.esquema.table_reneg",
        id_col="ccpf_cnpj",
        start_col="__START_AT",
        end_col="__END_AT",
        required_cols=[]
    )
