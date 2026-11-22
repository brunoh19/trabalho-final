import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ORDEM_TIER = ["luxury", "upscale", "boutique", "midscale", "economy"]
CORES = dict(zip(ORDEM_TIER, px.colors.qualitative.Safe))


def _revpar(df, por):
    """RevPAR ponderado: receita total dividida pelos quartos disponíveis (não é média de médias)."""
    g = df.groupby(por, as_index=False).agg(receita=("room_revenue", "sum"), disp=("available_rooms", "sum"))
    g["revpar"] = g["receita"] / g["disp"]
    return g

def comparacao_tiers(semanal):
    g = _revpar(semanal, "tier")
    fig = px.bar(g, x="tier", y="revpar", color="tier", text_auto=".0f", color_discrete_map=CORES,
                 category_orders={"tier": ORDEM_TIER}, labels={"tier": "Tier", "revpar": "RevPAR (US$)"},
                 title="RevPAR médio por tier")
    fig.update_layout(showlegend=False)
    return fig

def evolucao_eventos(semanal):
    s = _revpar(semanal, ["week_start", "tier"])
    ev = semanal.groupby("week_start", as_index=False)["event_nights"].sum()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.72, 0.28], vertical_spacing=0.06)
    for t in ORDEM_TIER:
        d = s[s["tier"] == t]
        if len(d):
            fig.add_trace(go.Scatter(x=d["week_start"], y=d["revpar"], name=t, line=dict(color=CORES[t])),
                          row=1, col=1)
    fig.add_trace(go.Bar(x=ev["week_start"], y=ev["event_nights"], name="noites com evento",
                         marker_color="#888"), row=2, col=1)
    fig.update_yaxes(title_text="RevPAR (US$)", row=1, col=1)
    fig.update_yaxes(title_text="Noites com evento", row=2, col=1)
    fig.update_layout(title="RevPAR semanal por tier e eventos de demanda")
    return fig

def quadrantes(semanal):
    h = semanal.groupby(["hotel_name", "tier"], as_index=False)[["ari", "mpi"]].mean()
    ref = 100 if h["ari"].median() > 10 else 1      # "igual ao concorrente": 100 ou 1, conforme a escala
    fig = px.scatter(h, x="ari", y="mpi", color="tier", text="hotel_name", color_discrete_map=CORES,
                     labels={"ari": "Índice de preço (ARI)", "mpi": "Índice de ocupação (MPI)"},
                     title="Posicionamento de cada hotel frente aos concorrentes")
    fig.add_vline(x=ref, line_dash="dash")
    fig.add_hline(y=ref, line_dash="dash")
    fig.update_traces(textposition="top center", marker_size=12)
    return fig

def desvio_mars(decisoes):
    fig = px.box(decisoes, x="tier", y="rate_gap_pct", color="tier", color_discrete_map=CORES,
                 category_orders={"tier": ORDEM_TIER},
                 labels={"tier": "Tier", "rate_gap_pct": "Desvio do preço em relação ao MARS (%)"},
                 title="Quanto o preço praticado se afasta do preço recomendado (MARS)")
    fig.add_hline(y=0, line_dash="dash")
    fig.update_layout(showlegend=False)
    return fig

def cenarios_dist(cenarios):
    g = cenarios.groupby("cenario", as_index=False)["avaliacoes"].sum().sort_values("avaliacoes")
    g["pct"] = (g["avaliacoes"] / g["avaliacoes"].sum() * 100).round(1)
    return px.bar(g, x="avaliacoes", y="cenario", orientation="h", text=g["pct"].astype(str) + "%",
                  labels={"avaliacoes": "Avaliações", "cenario": ""}, title="Avaliações por cenário")
    
def sankey(fluxo):
    cen = list(fluxo["cenario"].unique())
    notas = sorted(fluxo["rating"].unique())
    nos = cen + [f"{n} estrelas" for n in notas]
    origem = fluxo["cenario"].map(cen.index).tolist()
    destino = fluxo["rating"].map(lambda n: len(cen) + notas.index(n)).tolist()
    fig = go.Figure(go.Sankey(node=dict(label=nos, pad=15, thickness=16),
                              link=dict(source=origem, target=destino, value=fluxo["n"].tolist())))
    fig.update_layout(title="Do cenário de avaliação à nota dada")
    return fig

def nuvem(palavras, sentimento, cor):
    from wordcloud import WordCloud
    freq = palavras.loc[palavras["sentimento"] == sentimento].set_index("palavra")["freq"].to_dict()
    return WordCloud(width=900, height=450, background_color="white", colormap=cor).generate_from_frequencies(freq).to_array()

def resultado_decisoes(decisoes):
    g = decisoes.groupby(["action", "outcome"], as_index=False).size()
    fig = px.bar(g, x="action", y="size", color="outcome",
                 category_orders={"action": ["raise", "hold", "lower"], "outcome": ["better", "in line", "worse"]},
                 color_discrete_map={"better": "#2e7d32", "in line": "#9e9e9e", "worse": "#c62828"},
                 labels={"action": "Decisão de preço", "size": "% das decisões", "outcome": "Resultado"},
                 title="Resultado da semana seguinte, por tipo de decisão")
    fig.update_layout(barnorm="percent")      # cada barra soma 100%
    return fig