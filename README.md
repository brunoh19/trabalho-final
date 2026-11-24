# trabalho-final

# Inteligência de Receita para os Hotéis de Port Alder

Trabalho final do curso de Ciência de Dados(LabEduc). Análise de dois anos (2027–2028) de operação de 14 hotéis fictícios.

**Autor:** Bruno Henrique

> O dataset Nice Rooms é sintético. As conclusões valem para Port Alder, não para o mercado hoteleiro real.

## Painel

**Abrir online:** [COLE AQUI O LINK DO STREAMLIT]

O painel foi feito em Streamlit

## Como abrir cada parte

| Parte | Onde |
|---|---|
| Etapa 1 · exploração | `notebook/exploracao.ipynb` |
| Etapa 2 · estatística | `notebook/estatisticas.ipynb` |
| Etapa 3 · banco de dados | `notebook/bancodedados.ipynb`, `banco/nice_rooms.db`, `banco/diagrama.png` |
| Etapa 4 · visualização | `notebook/visualizacao.ipynb` |
| Etapa 5 · painel | `dashboard/app.py` (código) |
| Etapa 6 · fechamento | `diario_de_campo.md`, `relatorio_executivo`, `apresentacao` |

Os notebooks já estão **executados**, com as saídas visíveis.

## Como rodar no seu computador

```bash
python -m venv .venv
.venv\Scripts\activate                       
pip install -r requirements.txt
pip install jupyter wordcloud nbformat       
```

A ordem importa, porque cada etapa usa o que a anterior gerou:

1. `notebook/exploracao.ipynb`
2. `notebook/bancodedados.ipynb` (cria o banco `banco/nice_rooms.db`)
3. `notebook/estatisticas.ipynb` (lê o banco)
4. `python dashboard/preparar_dados.py` (gera os CSVs do painel e dos gráficos)
5. `notebook/visualizacao.ipynb`
6. `streamlit run dashboard/app.py`

## Estrutura

```
trabalho-final/
├── README.md
├── requirements.txt
├── dados/              
├── notebook/           
├── banco/              
├── dashboard/          
├── diario_de_campo.md
├── relatorio_executivo
└── apresentacao
```

## Ferramentas

Python, Pandas, SQLite, Matplotlib, Seaborn, Plotly, WordCloud, Streamlit, Jupyter e VS Code. Auxílio da IA (Claude) na criação.