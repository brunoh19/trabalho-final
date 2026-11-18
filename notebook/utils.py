import pandas as pd
from pathlib import Path

PASTA_DADOS = Path(__file__).resolve().parent.parent / "dados"
ARQUIVOS = ["hotels", "room_types", "daily_market", "weekly_performance",
            "rate_decisions", "reviews", "review_scenarios"]

def carregar_dados():
    """Lê os 7 arquivos JSONL e devolve um dicionário de DataFrames."""
    return {nome: pd.read_json(PASTA_DADOS / f"{nome}.jsonl", lines=True)
            for nome in ARQUIVOS}
    
from IPython.display import display

def inspecionar(df, nome):
    """Mostra formato, duplicados, tipos, nulos e textos vazios de uma tabela."""
    print(f"=== {nome} ===")
    print("Formato:", df.shape, "| Duplicados:", df.duplicated().sum())
    resumo = pd.DataFrame({"tipo": df.dtypes, "nulos": df.isna().sum()})
    resumo["vazios"] = (df == "").sum()
    display(resumo)
    display(df.head(3))
    