import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from PIL import Image

# ✅ Primeira chamada obrigatória
st.set_page_config(page_title="Análise de Intervalos de Confiança", layout="centered")

# 🎨 Estilo lavanda profunda embutido
st.markdown("""
<style>
    header {visibility: hidden;}
    .viewerBadge_container__1QSob {visibility: hidden;}
    .main .block-container {
        padding-top: 2rem;
    }
    body, .main, .block-container {
        background-color: #f9f7fc !important;
        color: #3e3553;
        font-family: 'Segoe UI', sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #5e4b8b !important;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    h1, h2, h3, h4 {
        color: #4a3d6a;
    }
    .stSelectbox > div > div {
        background-color: white !important;
        color: #5e4b8b !important;
    }
    .lavender-box {
        background-color: #ede6fa;
        border-left: 6px solid #b89fe6;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .banner {
        background-color: #5e4b8b;
        color: white;
        padding: 1.5rem;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 600;
        border-radius: 10px;
        margin-bottom: 40px;
        letter-spacing: 0.5px;
    }
    .footer {
        font-size: 0.9rem;
        color: #777;
        text-align: center;
        margin-top: 40px;
    }
</style>

<style>
    body, .main, .block-container {
        background-color: white;
        color: #4a355a;
    }
    section[data-testid="stSidebar"] {
        background-color: #5e4b8b !important;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    h1, h2, h3, h4 {
        color: #5e4b8b;
    }
    div[data-baseweb="select"] {
        background-color: #ede6fa !important;
        border-radius: 8px !important;
        padding: 4px !important;
        color: #4a355a !important;
        font-weight: 500 !important;
    }
    .stButton>button {
        background-color: #5e4b8b !important;
        color: white;
        border: none;
        border-radius: 5px;
    }
    .lavender-box {
        background-color: #ede6fa;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #d7c4f0;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 🌟 Título da Página
st.title("🔍 Intervalos de Confiança por Categoria de Estação")
st.markdown("Aplicação de Intervalos de Confiança, visualizações e interpretações práticas com base nos dados de metais pesados.")

# --- Carregar os dados ---
@st.cache_data
def load_data():
    df = pd.read_excel("dados_metais_com_categoria.xlsx")
    df.columns = df.columns.str.strip().str.upper()
    return df

df = load_data()

# --- Visualização do dataset ---
st.markdown('<div class="lavender-box">', unsafe_allow_html=True)
st.subheader("🧾 Dados Carregados")
st.markdown("Abaixo estão as amostras de concentração de metais pesados por estação de coleta:")
st.dataframe(df, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Explicação das colunas ---
st.markdown('<div class="lavender-box">', unsafe_allow_html=True)
st.subheader("📘 Dicionário das Colunas do Dataset")
st.markdown("""
- **ESTAÇÃO**: Código da estação de coleta da amostra de água (ex: RD009, RD085...).
- **CATEGORIA**: Classificação da estação com base na proximidade ao evento de contaminação:
  - `INCIDENTE`: diretamente afetadas;
  - `MÉDIOS`: próximas ao incidente;
  - `LONGES`: regiões mais afastadas.
- **DATA**: Data da coleta da amostra.
- **ARSÊNIO TOTAL**: Concentração total de arsênio presente na água (μg/L).
- **FERRO DISSOLVIDO**: Concentração de ferro dissolvido na amostra (μg/L).
- **MANGANÊS TOTAL**: Concentração total de manganês na água (μg/L).
""")
st.markdown('</div>', unsafe_allow_html=True)

# --- Define os grupos ---
grupos = {
    "INCIDENTE": ["RD009", "RD075", "RD074", "RD059"],
    "LONGES": ["RD095", "RD085"],
    "MEDIOS": ["RD083", "RD039"]
}

# --- Escolha da métrica numérica para análise ---
colunas_numericas = df.select_dtypes(include=np.number).columns.tolist()
coluna_selecionada = st.selectbox("Selecione o tipo de metal para análise:", colunas_numericas)

# --- Função para cálculo de intervalo de confiança ---
def calcular_ic(dados, alpha=0.05):
    n = len(dados)
    media = np.mean(dados)
    erro_padrao = stats.sem(dados, nan_policy='omit')
    margem_erro = stats.t.ppf(1 - alpha/2, df=n-1) * erro_padrao
    return media, media - margem_erro, media + margem_erro

# --- Análise por grupo ---
for grupo_nome, regioes in grupos.items():
    st.subheader(f"📊 Categoria: {grupo_nome}")
    
    grupo_df = df[df["ESTAÇÃO"].isin(regioes)]

    if grupo_df.empty:
        st.warning(f"Nenhum dado encontrado para a categoria {grupo_nome}.")
        continue

    # 🔹 Cálculo do IC para a categoria inteira (todas as estações juntas)
    valores_categoria = grupo_df[coluna_selecionada].dropna()

    if not valores_categoria.empty:
        media_cat, ic_min_cat, ic_max_cat = calcular_ic(valores_categoria)
        
        st.markdown(f"**Resumo da Categoria `{grupo_nome}`**")
        st.write(f"Média geral: `{media_cat:.2f}`, IC 95%: [`{ic_min_cat:.2f}`, `{ic_max_cat:.2f}`]")

        fig_cat, ax_cat = plt.subplots()
        sns.histplot(valores_categoria, kde=True, ax=ax_cat, color='mediumpurple')
        ax_cat.axvline(ic_min_cat, color='red', linestyle='--', label='IC Min')
        ax_cat.axvline(ic_max_cat, color='red', linestyle='--', label='IC Max')
        ax_cat.axvline(media_cat, color='green', linestyle='-', label='Média')
        ax_cat.set_title(f'Distribuição Geral - {grupo_nome}')
        ax_cat.legend()
        st.pyplot(fig_cat)

        st.success(
            f"Para a categoria **{grupo_nome}**, o intervalo de confiança de 95% da média de `{coluna_selecionada}` "
            f"está entre **{ic_min_cat:.2f}** e **{ic_max_cat:.2f}**."
        )

    # 🔎 Análise por estação individual
    for estacao in regioes:
        estacao_df = grupo_df[grupo_df["ESTAÇÃO"] == estacao]
        valores = estacao_df[coluna_selecionada].dropna()

        if valores.empty:
            st.warning(f"Sem dados válidos para {estacao} na métrica selecionada.")
            continue

        media, ic_min, ic_max = calcular_ic(valores)

        st.markdown(f"**Estação `{estacao}`**")
        st.write(f"Média: `{media:.2f}`, IC 95%: [`{ic_min:.2f}`, `{ic_max:.2f}`]")

        fig, ax = plt.subplots()
        sns.histplot(valores, kde=True, ax=ax, color='skyblue')
        ax.axvline(ic_min, color='red', linestyle='--', label='IC Min')
        ax.axvline(ic_max, color='red', linestyle='--', label='IC Max')
        ax.axvline(media, color='green', linestyle='-', label='Média')
        ax.set_title(f'Distribuição - {estacao}')
        ax.legend()
        st.pyplot(fig)

        st.info(
            f"O intervalo de confiança indica que há 95% de confiança de que a média real de `{coluna_selecionada}` na estação **{estacao}** "
            f"esteja entre **{ic_min:.2f}** e **{ic_max:.2f}** com base na amostra."
        )
