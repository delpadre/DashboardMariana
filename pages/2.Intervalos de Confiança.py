import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Configuração da página
st.set_page_config(page_title="📏 Intervalos de Confiança", layout="wide")

# --- Estilo visual lavanda embutido + ajuste no botão ---
st.markdown("""
<style>
    /* Oculta o header padrão do Streamlit */
    header {visibility: hidden;}
    .viewerBadge_container__1QSob {visibility: hidden;}

    /* Padding no conteúdo principal */
    .main .block-container {
        padding-top: 2rem;
    }

    /* Fundo e fontes */
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

    /* Caixa lavanda */
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

    /* Estilo do botão selectbox */
    div[data-baseweb="select"] > div {
        background-color: #ede6fa !important;
        border: 1.5px solid black !important;
        border-radius: 10px !important;
    }


    div[data-baseweb="select"] * {
        color: #4a355a !important;
        font-family: "Segoe UI", sans-serif;
    }

    div[data-baseweb="select"]:hover {
        border-color: #4a355a !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Banner ---
st.markdown('<div class="lavender-box"><h2>📏 Intervalos de Confiança</h2></div>', unsafe_allow_html=True)

# --- Introdução ---
st.markdown('<div class="lavender-box">', unsafe_allow_html=True)
st.markdown("""
### 📊 Análise de Concentração de Metais e Intervalos de Confiança (IC 95%)

#### 🎯 Objetivo
Avaliar a concentração de arsênio total, ferro dissolvido e manganês total nas estações de monitoramento de uma região impactada. Utilizamos os **intervalos de confiança (IC 95%)** para estimar a precisão das médias e analisar o **risco de contaminação** por categoria:
- **Incidente**
- **Médio**
- **Longes**

#### 🧪 Metodologia
- **Intervalo de Confiança (IC 95%)**: calculado para cada categoria e metal.
- **Limites Legais**:
  - **Arsênio Total**: 0.01 mg/L (CONAMA 357/2005)
  - **Ferro Dissolvido**: 0.3 mg/L (OMS - estética)
  - **Manganês Total**: 0.1 mg/L (OMS)
""")
st.markdown('</div>', unsafe_allow_html=True)

# --- Carregar dados ---
df = pd.read_excel("dados_metais_com_categoria.xlsx")

# --- Dicionários ---
variaveis_limites = {
    "Arsênio total": (0.01, "🔬 Arsênio Total – Média com IC 95% por Categoria"),
    "Ferro dissolvido": (0.3, "🔩 Ferro Dissolvido – Média com IC 95% por Categoria"),
    "Manganês total": (0.1, "⚙️ Manganês Total – Média com IC 95% por Categoria")
}

explicacoes = {
    "Arsênio total": """
**Categoria Incidente:**
- Concentrações médias estão **acima do limite de 0.01 mg/L**.
- IC 95% confirma contaminação significativa.
**Conclusão**: Alto risco de contaminação por arsênio.

**Categoria Médio:**
- Média próxima ao limite e IC cruza o limite.
**Conclusão**: Risco moderado, requer monitoramento.

**Categoria Longe:**
- Média e IC abaixo do limite.
**Conclusão**: Sem risco significativo.
""",
    "Ferro dissolvido": """
**Categoria Incidente:**
- Média **acima de 0.3 mg/L**, IC não cruza o limite.
**Conclusão**: Concentração preocupante, necessita remediação.

**Categoria Médio:**
- Médias próximas ao limite com IC cruzando.
**Conclusão**: Risco moderado, exige acompanhamento.

**Categoria Longe:**
- Médias abaixo do limite.
**Conclusão**: Níveis seguros.
""",
    "Manganês total": """
**Categoria Incidente:**
- Médias **acima do limite de 0.1 mg/L**, ICs também.
**Conclusão**: Alto risco de contaminação por manganês.

**Categoria Médio:**
- Médias próximas ou ligeiramente acima com ICs cruzando.
**Conclusão**: Risco moderado, requer monitoramento.

**Categoria Longe:**
- Médias e ICs abaixo do limite.
**Conclusão**: Região segura.
"""
}

# --- Caixa de seleção ---
st.markdown('<div class="lavender-box">', unsafe_allow_html=True)
st.markdown("### 🧪 Escolha o metal para análise:")
metal_escolhido = st.selectbox(
    "",
    options=list(variaveis_limites.keys()),
    format_func=lambda x: x.capitalize(),
    index=2
)
st.markdown('</div>', unsafe_allow_html=True)

# --- Análise do metal selecionado ---
df[metal_escolhido] = pd.to_numeric(df[metal_escolhido], errors='coerce')

def calcular_ic_categoria(grupo):
    dados = grupo[metal_escolhido].dropna()
    n = len(dados)
    if n > 1:
        media = dados.mean()
        sem = stats.sem(dados)
        ic = sem * stats.t.ppf(0.975, n - 1)
        return pd.Series({'Média': media, 'IC': ic})
    return pd.Series({'Média': None, 'IC': None})

estat = df.groupby('Categoria').apply(calcular_ic_categoria).dropna().reset_index()
limite, titulo = variaveis_limites[metal_escolhido]

st.subheader(titulo)
fig, ax = plt.subplots(figsize=(8, 5))
x = range(len(estat))
ax.errorbar(x, estat['Média'], yerr=estat['IC'], fmt='o',
            color='black', capsize=6, markersize=6, linewidth=1.5)
ax.set_xticks(x)
ax.set_xticklabels(estat['Categoria'])
ax.set_ylabel(f'Concentração de {metal_escolhido} (mg/L)')
ax.axhline(limite, color='red', linestyle='--', label=f'Limite Máx. ({limite} mg/L)')
ax.set_title(f'{metal_escolhido} – Intervalo de Confiança 95% por Categoria')
ax.grid(axis='y', linestyle='--', alpha=0.3)
ax.legend()
st.pyplot(fig)

st.markdown(explicacoes[metal_escolhido])

# --- Conclusão geral ---
st.markdown('<div class="lavender-box">', unsafe_allow_html=True)
st.markdown("""
### ✅ Conclusão Geral

**Risco de Contaminação:**
- **Incidente:** Riscos elevados para arsênio, ferro e manganês. Requerem **intervenções urgentes**.
- **Médios:** Concentrações próximas aos limites legais.
  - **Ação:** Monitoramento contínuo recomendado.
- **Longes:** Valores seguros, mas devem manter monitoramento de longo prazo.

### 📌 Recomendações
- Monitoramento contínuo nas áreas mais impactadas
- Ações de remediação para arsênio e manganês onde ultrapassam os limites legais
""")
st.markdown('</div>', unsafe_allow_html=True)
