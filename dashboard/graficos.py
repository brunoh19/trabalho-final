import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns

sns.set_theme(style="whitegrid", context="notebook")

ORDEM_TIER = ["luxury", "upscale", "boutique", "midscale", "economy"]
CORES = dict(zip(ORDEM_TIER, sns.color_palette("colorblind", len(ORDEM_TIER)).as_hex()))


def _revpar(df, por):
    """RevPAR ponderado: receita total dividida pelos quartos disponíveis (não é média de médias)."""
    g = df.groupby(por, as_index=False).agg(receita=("room_revenue", "sum"), disp=("available_rooms", "sum"))
    g["revpar"] = g["receita"] / g["disp"]
    return g


def _ordem(serie):
    """Tiers que realmente aparecem nos dados, na ordem de luxo para econômico."""
    return [t for t in ORDEM_TIER if t in set(serie)]


def _fechar(fig):
    """Ajusta o espaçamento e fecha a figura (evita imagem duplicada no notebook e vazamento de memória)."""
    fig.tight_layout()
    plt.close(fig)
    return fig


def mostrar(fig):
    """Streamlit: mostra figura Plotly (Sankey) ou Matplotlib (as demais)."""
    import streamlit as st
    if isinstance(fig, go.Figure):
        st.plotly_chart(fig)
    else:
        st.pyplot(fig)


def comparacao_tiers(semanal):
    g = _revpar(semanal, "tier")
    ordem = _ordem(g["tier"])
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(data=g, x="tier", y="revpar", hue="tier", order=ordem, hue_order=ordem,
                palette=CORES, legend=False, ax=ax)
    for barras in ax.containers:
        ax.bar_label(barras, fmt="%.0f", padding=3)
    ax.set(title="RevPAR médio por tier", xlabel="Tier", ylabel="RevPAR (US$)")
    return _fechar(fig)


def evolucao_eventos(semanal):
    s = _revpar(semanal, ["week_start", "tier"])
    ev = semanal.groupby("week_start")["event_nights"].sum()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6.5), sharex=True,
                                   gridspec_kw={"height_ratios": [3, 1]})
    sns.lineplot(data=s, x="week_start", y="revpar", hue="tier", hue_order=_ordem(s["tier"]),
                 palette=CORES, ax=ax1)
    ax1.set(title="RevPAR semanal por tier e eventos de demanda", xlabel="", ylabel="RevPAR (US$)")
    ax1.legend(title="Tier", ncol=5, fontsize=8)
    ax2.bar(ev.index, ev.values, width=5, color="#888888")
    ax2.set(xlabel="Semana", ylabel="Noites com evento")
    fig.autofmt_xdate()
    return _fechar(fig)


def quadrantes(semanal):
    h = semanal.groupby(["hotel_name", "tier"], as_index=False)[["ari", "mpi"]].mean()
    ref = 100 if h["ari"].median() > 10 else 1      # "igual ao concorrente": 100 ou 1, conforme a escala
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(data=h, x="ari", y="mpi", hue="tier", hue_order=_ordem(h["tier"]),
                    palette=CORES, s=120, ax=ax)
    for _, linha in h.iterrows():
        ax.annotate(linha["hotel_name"], (linha["ari"], linha["mpi"]), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=8)
    ax.axvline(ref, ls="--", color="gray")
    ax.axhline(ref, ls="--", color="gray")
    ax.set(title="Posicionamento de cada hotel frente aos concorrentes",
           xlabel="Índice de preço (ARI)", ylabel="Índice de ocupação (MPI)")
    ax.legend(title="Tier")
    return _fechar(fig)


def desvio_mars(decisoes):
    ordem = _ordem(decisoes["tier"])
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.boxplot(data=decisoes, x="tier", y="rate_gap_pct", hue="tier", order=ordem, hue_order=ordem,
                palette=CORES, legend=False, ax=ax)
    ax.axhline(0, ls="--", color="gray")
    ax.set(title="Quanto o preço praticado se afasta do preço recomendado (MARS)",
           xlabel="Tier", ylabel="Desvio do preço em relação ao MARS (%)")
    return _fechar(fig)


def cenarios_dist(cenarios):
    g = (cenarios.groupby("cenario", as_index=False)["avaliacoes"].sum()
         .sort_values("avaliacoes", ascending=False))
    g["pct"] = (g["avaliacoes"] / g["avaliacoes"].sum() * 100).round(1)
    fig, ax = plt.subplots(figsize=(8, max(3.0, 0.5 * len(g) + 1)))
    sns.barplot(data=g, x="avaliacoes", y="cenario", orient="h", color="#4c72b0", ax=ax)
    ax.bar_label(ax.containers[0], labels=[f"{p}%" for p in g["pct"]], padding=3)
    ax.set(title="Avaliações por cenário", xlabel="Avaliações", ylabel="")
    return _fechar(fig)


def sankey(fluxo):
    # continua em Plotly: o seaborn não faz Sankey e o enunciado pede ao menos um gráfico Plotly interativo
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
    t = pd.crosstab(decisoes["action"], decisoes["outcome"], normalize="index").mul(100)
    t = t.reindex(index=[a for a in ["raise", "hold", "lower"] if a in t.index],
                  columns=[o for o in ["better", "in line", "worse"] if o in t.columns])
    cores = {"better": "#2e7d32", "in line": "#9e9e9e", "worse": "#c62828"}
    fig, ax = plt.subplots(figsize=(7, 4.5))
    t.plot.bar(stacked=True, ax=ax, color=[cores[c] for c in t.columns], rot=0)
    for barras in ax.containers:
        ax.bar_label(barras, labels=[f"{v:.0f}%" for v in barras.datavalues], label_type="center", color="white")
    ax.set(title="Resultado da semana seguinte, por tipo de decisão", xlabel="Decisão de preço",
           ylabel="% das decisões")
    ax.legend(title="Resultado", loc="upper left", bbox_to_anchor=(1, 1))
    return _fechar(fig)