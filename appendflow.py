# ================================== streaming_target.py ==================================
"""
Criação da tabela streaming alvo para os fluxos append_flow.

Referências
-----------
- create_streaming_table API :contentReference[oaicite:1]{index=1}
- Exemplo oficial MS Learn :contentReference[oaicite:2]{index=2}
"""

import dlt

dlt.create_streaming_table(               # <-- tabela vazia / streaming
    name="analitica.features_stream",
    comment="Tabela streaming de features autorregressivas.",
    partition_cols=["ccpf_cnpj"],
    tbl_properties={"quality": "gold"},
)
# ================================ backfill_append_flow.py ================================
"""
Back-fill histórico (executar apenas **uma vez**).

Executa o cálculo completo com `engine.Features` e grava via append_flow na
tabela streaming `analitica.features_stream`.

Depois de concluído o histórico, **remova este append_flow** do notebook
ou marque o notebook como concluído — a tabela permanece ativa
:contentReference[oaicite:3]{index=3}.
"""

import dlt
from pyspark.sql import SparkSession
from engine import Features

spark = SparkSession.builder.getOrCreate()

# Parâmetros do back-fill
INI = "2010-01-01"
FIM = "2025-04-30"

eng = Features(
    spark,
    freq="1m",
    lags=[0, "7d", "1m", "3m", "6m"],
    timezone="America/Sao_Paulo",
    adjust_to_bday="previous",
)

df_backfill = eng.compute(start_date=INI, end_date=FIM)

@dlt.append_flow(
    target="analitica.features_stream",   # deve existir como streaming table
    name="backfill_once",
)
def backfill_once():
    """
    Append flow único para histórico completo.

    Após finalizar e materializar o histórico, exclua ou comente
    esta função — mantém-se a consistência do checkpoint
:contentReference[oaicite:4]{index=4}.
    """
    return df_backfill


# ============================== incremental_append_flow.py ===============================
"""
Fluxo incremental diário.

Leva apenas os snapshots novos a partir do último `dreft_sist`
já presente na `features_stream`.

Documentação append_flow incremental:
- docs + exemplos :contentReference[oaicite:5]{index=5}
"""

import dlt
from pyspark.sql import SparkSession, functions as F
from engine import Features

spark = SparkSession.builder.getOrCreate()
TBL_TARGET = "analitica.features_stream"

# -------- recupera último snapshot gravado ----------------------------------------------
try:
    ultimo = (
        spark.table(TBL_TARGET)
        .select(F.max("dreft_sist").alias("max_dt"))
        .collect()[0]["max_dt"]
    )
except Exception:
    ultimo = None  # tabela vazia ou erro; tratado abaixo

hoje = spark.sql("SELECT current_date()").collect()[0][0]
inicio = hoje if ultimo is None else spark.sql(f"SELECT date_add('{ultimo}', 1)").collect()[0][0]

if inicio > hoje:
    # Nenhum dado novo — DLT ignora commit vazio
    dlt.mark_progress("Sem novos snapshots.")
    import sys; sys.exit(0)

# -------- calcula features somente para intervalo novo -----------------------------------
eng = Features(
    spark,
    freq="1d",
    lags=[0, "7d", "1m", "3m", "6m"],
    timezone="America/Sao_Paulo",
    adjust_to_bday="previous",
)

df_inc = eng.compute(start_date=str(inicio), end_date=str(hoje))

# -------- append_flow incremental --------------------------------------------------------
@dlt.append_flow(
    target=TBL_TARGET,
    name="features_incremental",
)
def features_incremental():
    """
    Fluxo diário incremental que adiciona novas linhas
    sem reprocessar histórico :contentReference[oaicite:6]{index=6}.
    """
    return df_inc


# ==========================================================================================
    # -----------------------------------------------------------------
    # Novo método: retorna apenas o bloco de colunas + PRIMARY KEY
    # -----------------------------------------------------------------
    def print_ddl(self, df: DataFrame, *, pk_cols: List[str]) -> str:
        """
        Gera o bloco de definição de colunas para uso em DDL externos.

        Parameters
        ----------
        df : pyspark.sql.DataFrame
            DataFrame cujo `schema` será usado como base.
        pk_cols : list[str]
            Lista com o(s) nome(s) das colunas que compõem a chave primária.

        Returns
        -------
        str
            Texto contendo cada coluna na forma:
            ``  `nome` tipo COMMENT 'descrição',``  
            seguido de ``PRIMARY KEY (...)``.  
            **Não** inclui ``CREATE TABLE`` nem parêntese inicial/
            final, permitindo inserção flexível em *streaming
            tables* ou comandos SQL externos.

        Examples
        --------
        >>> ddl_fragment = eng.print_ddl(df_empty, pk_cols=["ccpf_cnpj", "dreft_sist"])
        >>> print(ddl_fragment)
        `ccpf_cnpj` string COMMENT 'Chave primária do cliente',
        `dreft_sist` date COMMENT 'Data de referência do snapshot',
        `vsoma_rtrit_reneg_atvo` double COMMENT 'Valor total renegociado ativo',
        PRIMARY KEY (ccpf_cnpj, dreft_sist)
        """
        # monta lista de colunas com comentários
        col_lines: List[str] = []
        for field in df.schema:
            dtype = field.dataType.simpleString()
            descr = (
                _feature_registry[field.name].description
                if field.name in _feature_registry
                else f"Coluna {field.name}"
            )
            col_lines.append(f"`{field.name}` {dtype} COMMENT '{descr}'")
        # adiciona cláusula PK
        pk_line = f"PRIMARY KEY ({', '.join(pk_cols)})"
        # concatena com vírgulas, exceto na última linha
        ddl_body = ",\n".join(col_lines + [pk_line])
        return ddl_body

Features.print_ddl_fragment = print_ddl


# ================== streaming_target_feature.py ==================
"""
Criação governada da _streaming table_ `analitica.features_stream`
usando **dlt.create_streaming_table(schema=ddl_fragment)**, conforme
documentação oficial.                             
Refs:
- Parâmetro `schema` em `create_streaming_table`  :contentReference[oaicite:0]{index=0}
- Sintaxe `CREATE STREAMING TABLE`                :contentReference[oaicite:1]{index=1}
- Conceito de Streaming Tables & DLT              :contentReference[oaicite:2]{index=2}
- Boas-práticas de governança Unity Catalog       :contentReference[oaicite:3]{index=3}
"""

import dlt
from pyspark.sql import SparkSession
from engine import Features

spark = SparkSession.builder.getOrCreate()

# -----------------------------------------------------------------
# 1. Geração do fragmento de schema utilizando print_ddl()
# -----------------------------------------------------------------
eng = Features(
    spark,
    freq="1m",
    lags=[0, "7d", "1m", "3m", "6m"],
    timezone="America/Sao_Paulo",
    adjust_to_bday="previous",
)

# DataFrame vazio apenas p/ capturar o schema completo
df_empty = (
    eng.compute(
        start_date="1900-01-01",
        end_date="1900-01-01",
        pk_ids=spark.createDataFrame([], "ccpf_cnpj string"),
    )
    .limit(0)
)

ddl_fragment = eng.print_ddl(
    df=df_empty,
    pk_cols=["ccpf_cnpj", "dreft_sist"],
)
# -----------------------------------------------------------------
# 2. Criação da tabela streaming governada
#    (sem usar execute_sql, conforme solicitado)
# -----------------------------------------------------------------
dlt.create_streaming_table(
    name="analitica.features_stream",
    comment="Streaming table de features autorregressivas governada.",
    partition_cols=["ccpf_cnpj"],
    schema=ddl_fragment,  # fragmento gerado por print_ddl()
    table_properties={"quality": "gold"},
)
