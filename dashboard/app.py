from pathlib import Path

import pandas as pd
import streamlit as st

import graficos as g

st.set_page_config(page_title="Port Alder · Painel de Receita", layout="wide")

DADOS = Path(__file__).resolve().parent / "dados"


@st.cache_data
def carregar():
    semanal = pd.read_csv(DADOS / "semanal.csv", parse_dates=["week_start"])
    decisoes = pd.read_csv(DADOS / "decisoes.csv")
    cenarios = pd.read_csv(DADOS / "cenarios.csv")
    return semanal, decisoes, cenarios


semanal, decisoes, cenarios = carregar()

st.title("Painel de Receita · Port Alder")
st.caption("Associação de 14 hotéis · 2027–2028 · dados sintéticos")

with st.expander("Sobre este painel"):
    st.markdown("""
**Público:** (escreva aqui)

**Decisões que o painel ajuda a tomar:**
1. (decisão 1)
2. (decisão 2)
3. (decisão 3)
""")
    
    st.sidebar.header("Filtros")
anos_disp = sorted(semanal["ano"].unique())
anos = st.sidebar.multiselect("Ano", anos_disp, default=anos_disp)
tiers = st.sidebar.multiselect("Tier", g.ORDEM_TIER, default=g.ORDEM_TIER)
hoteis_disp = sorted(semanal[semanal["tier"].isin(tiers)]["hotel_name"].unique())
hoteis = st.sidebar.multiselect("Hotel", hoteis_disp, default=hoteis_disp)

f = semanal[semanal["ano"].isin(anos) & semanal["hotel_name"].isin(hoteis)]
d = decisoes[decisoes["ano"].isin(anos) & decisoes["hotel"].isin(hoteis)]
c = cenarios[cenarios["ano"].isin(anos) & cenarios["hotel"].isin(hoteis)]

if f.empty:
    st.warning("Nenhum dado para os filtros escolhidos. Selecione ao menos um ano, um tier e um hotel.")
    st.stop()
    
def calcular_kpis(f):
    disp, vend = f["available_rooms"].sum(), f["rooms_sold"].sum()
    com_nota = f["mean_rating"].notna()
    nota = (f["mean_rating"] * f["review_count"]).sum() / f.loc[com_nota, "review_count"].sum()
    rgi = (f["rgi"] * f["available_rooms"]).sum() / disp
    return {
        "Ocupação": f"{vend / disp:.1%}",
        "ADR (US$)": f"{f['room_revenue'].sum() / vend:,.0f}",
        "RevPAR (US$)": f"{f['room_revenue'].sum() / disp:,.0f}",
        "Receita total (US$ mi)": f"{f['total_revenue'].sum() / 1e6:,.1f}",
        "RGI médio": f"{rgi:.1f}",
        "Nota média": f"{nota:.2f}",
    }


def tabela_hoteis(f):
    f = f.assign(rgi_pond=f["rgi"] * f["available_rooms"])
    t = f.groupby(["hotel_name", "tier"], as_index=False).agg(
        vendidos=("rooms_sold", "sum"), disp=("available_rooms", "sum"),
        receita=("room_revenue", "sum"), total=("total_revenue", "sum"), rgi_pond=("rgi_pond", "sum"))
    t["Ocupação (%)"] = (100 * t["vendidos"] / t["disp"]).round(1)
    t["ADR (US$)"] = (t["receita"] / t["vendidos"]).round(0)
    t["RevPAR (US$)"] = (t["receita"] / t["disp"]).round(0)
    t["Receita total (US$)"] = t["total"].round(0)
    t["RGI médio"] = (t["rgi_pond"] / t["disp"]).round(1)
    t = t.rename(columns={"hotel_name": "Hotel", "tier": "Tier"})
    colunas = ["Hotel", "Tier", "Ocupação (%)", "ADR (US$)", "RevPAR (US$)", "Receita total (US$)", "RGI médio"]
    return t[colunas].sort_values("RGI médio", ascending=False)


kpis = calcular_kpis(f)
for coluna, (rotulo, valor) in zip(st.columns(len(kpis)), kpis.items()):
    coluna.metric(rotulo, valor)
    
aba1, aba2, aba3, aba4 = st.tabs(["Visão geral", "Concorrência", "Decisões de preço", "Hóspedes"])

with aba1:
    g.mostrar(g.comparacao_tiers(f))
    g.mostrar(g.evolucao_eventos(f))

with aba2:
    g.mostrar(g.quadrantes(f))
    st.subheader("Hotéis ordenados por RGI")
    st.dataframe(tabela_hoteis(f), hide_index=True)

with aba3:
    if d.empty:
        st.info("Sem decisões de preço para os filtros escolhidos.")
    else:
        g.mostrar(g.resultado_decisoes(d))
        g.mostrar(g.desvio_mars(d))

with aba4:
    if c.empty:
        st.info("Sem avaliações para os filtros escolhidos.")
    else:
        g.mostrar(g.cenarios_dist(c))
        
st.divider()
st.caption("Fonte: dataset Nice Rooms (Kaggle), sintético: as conclusões valem apenas para Port Alder. "
           "Indicadores ponderados (soma ÷ soma). O ano segue o início de cada semana.")