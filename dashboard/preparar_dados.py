import re
import sqlite3
from collections import Counter
from pathlib import Path

import pandas as pd
from wordcloud import STOPWORDS

pasta = Path(__file__).resolve().parent
con = sqlite3.connect(pasta.parent / "banco" / "nice_rooms.db")
saida = pasta / "dados"
saida.mkdir(exist_ok=True)

consultas = {
    # uma linha por hotel e semana, já com nome, tier e ano (usa a VIEW da Etapa 3)
    "semanal": "SELECT * FROM v_semanal",
    # uma linha por decisão de preço
    "decisoes": """SELECT d.*, h.name AS hotel, h.tier,
                          CAST(substr(d.week_start, 1, 4) AS INTEGER) AS ano
                   FROM rate_decisions d JOIN hotels h USING (hotel_id)""",
    # avaliações por hotel, ano e cenário
    "cenarios": """SELECT r.hotel_id, h.name AS hotel, h.tier,
                          CAST(substr(r.week_start, 1, 4) AS INTEGER) AS ano,
                          s.label AS cenario, COUNT(*) AS avaliacoes, AVG(r.rating) AS nota_media
                   FROM reviews r
                   JOIN review_scenarios s USING (scenario_id)
                   JOIN hotels h USING (hotel_id)
                   GROUP BY r.hotel_id, ano, s.scenario_id""",
    # contagem cenário × nota, para o gráfico Sankey
    "fluxo": """SELECT s.label AS cenario, r.rating, COUNT(*) AS n
                FROM reviews r JOIN review_scenarios s USING (scenario_id)
                GROUP BY s.scenario_id, r.rating""",
}
for nome, consulta in consultas.items():
    pd.read_sql(consulta, con).to_csv(saida / f"{nome}.csv", index=False)
    print("salvo:", nome)

# palavras mais frequentes das avaliações boas (4 e 5) e ruins (1 e 2), para as nuvens
av = pd.read_sql("SELECT rating, text FROM reviews", con)
linhas = []
for sentimento, filtro in {"positivo": av["rating"] >= 4, "negativo": av["rating"] <= 2}.items():
    c = Counter()
    for t in av.loc[filtro, "text"].dropna():
        c.update(p for p in re.findall(r"[a-zà-ú']+", t.lower()) if len(p) > 2 and p not in STOPWORDS)
    linhas += [(sentimento, palavra, n) for palavra, n in c.most_common(150)]
pd.DataFrame(linhas, columns=["sentimento", "palavra", "freq"]).to_csv(saida / "palavras.csv", index=False)
print("salvo: palavras")