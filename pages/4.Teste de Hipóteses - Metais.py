import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind, mannwhitneyu, shapiro, chi2_contingency

# --- Configuração da página ---
st.set_page_config(page_title="Teste de Hipóteses - Metais", layout="wide")

# --- Estilo embutido: header oculto e fundo uniforme ---
st.markdown("""
<style>
    /* Oculta o header padrão do Streamlit */
    header {visibility: hidden;}
    .viewerBadge_container__1QSob {visibility: hidden;}

    /* Ajusta o padding do conteúdo principal */
    .main .block-container {
        padding-top: 2rem;
    }

    /* Estilo geral */
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
""", unsafe_allow_html=True)

# --- Banner de destaque ---
st.markdown('<div class="banner">💧 Monitoramento de Qualidade da Água - Testes Estatísticos</div>', unsafe_allow_html=True)

# --- Título ---
st.title("📌 Testes de Hipóteses - Metais na Água")

# ---------------------
# Leitura dos dados
# ---------------------
file_path = "dados_metais_com_categoria.xlsx"
df = pd.read_excel(file_path)
df.columns = df.columns.str.strip()

# ---------------------
# Informações iniciais
# ---------------------
st.markdown('<div class="lavender-box">', unsafe_allow_html=True)
st.subheader("📊 Informações do Banco de Dados")
st.write(f"Total de registros: {len(df)}")
st.write("**Colunas e tipos de dados:**")
st.write(df.dtypes)
st.write("**Valores ausentes por coluna:**")
st.write(df.isnull().sum())
st.write("**Estatísticas descritivas:**")
st.write(df.describe())
st.write("**Frequência das categorias:**")
st.write(df["Categoria"].value_counts())
st.subheader("🔍 Pré-visualização dos dados")
st.dataframe(df.head())
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------
# Seletor de metal
# ---------------------
st.header("🧪 Testes de Hipótese")

metais_disponiveis = ["Ferro dissolvido", "Arsênio total", "Manganês total"]
metal = st.selectbox("Escolha o metal para análise:", metais_disponiveis)

# ---------------------
# TESTE 1: Comparação de Médias
# ---------------------
st.markdown('<div class="lavender-box">', unsafe_allow_html=True)
st.subheader(f"📌 Teste 1 - Comparação de Médias ({metal})")

df_teste = df[[metal, "Categoria"]].dropna()
grupo_incidente = df_teste[df_teste["Categoria"] == "Incidente"][metal]
grupo_outros = df_teste[df_teste["Categoria"] != "Incidente"][metal]

st.write(f"Incidente: {len(grupo_incidente)} registros")
st.write(f"Outros: {len(grupo_outros)} registros")

# Teste de normalidade
stat_inc, p_inc = shapiro(grupo_incidente)
stat_out, p_out = shapiro(grupo_outros)

st.write(f"Shapiro-Wilk p-valor (Incidente): {p_inc:.4f}")
st.write(f"Shapiro-Wilk p-valor (Outros): {p_out:.4f}")
normal = p_inc > 0.05 and p_out > 0.05

# Teste t ou Mann-Whitney
if normal:
    stat, p = ttest_ind(grupo_incidente, grupo_outros, equal_var=False)
    st.write("🔍 Teste T aplicado (dados com distribuição normal)")
else:
    stat, p = mannwhitneyu(grupo_incidente, grupo_outros)
    st.write("🔍 Teste de Mann-Whitney aplicado (dados não normais)")

st.write(f"Estatística do teste: {stat:.4f}")
st.write(f"p-valor: {p:.4f}")

if p < 0.05:
    st.success("Rejeitamos H₀: Diferença significativa entre as médias.")
else:
    st.info("Não rejeitamos H₀: Diferença não significativa.")

# Visualização: boxplot
st.write("📊 Boxplot:")
fig, ax = plt.subplots()
sns.boxplot(data=df_teste, x="Categoria", y=metal, ax=ax)
st.pyplot(fig)
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------
# TESTE 2: Qui-Quadrado
# ---------------------
st.markdown('<div class="lavender-box">', unsafe_allow_html=True)
st.subheader(f"📌 Teste 2 - Associação entre Categoria e {metal} Acima do Limite")

limites = {
    "Ferro dissolvido": 0.3,
    "Arsênio total": 0.01,
    "Manganês total": 0.1
}
limite_escolhido = limites[metal]

df["Metal_cat"] = df[metal].apply(
    lambda x: "Acima do limite" if x > limite_escolhido else "Dentro do limite"
)

contingencia = pd.crosstab(df["Categoria"], df["Metal_cat"])
st.write("📋 Tabela de contingência:")
st.write(contingencia)

chi2, p_chi, dof, expected = chi2_contingency(contingencia)

st.write(f"Estatística Qui-Quadrado: {chi2:.4f}")
st.write(f"p-valor: {p_chi:.4f}")

if p_chi < 0.05:
    st.success("Rejeitamos H₀: Existe associação entre Categoria e nível do metal.")
else:
    st.info("Não rejeitamos H₀: Sem associação significativa entre as variáveis.")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------
# VISUALIZAÇÕES ADICIONAIS
# ---------------------
st.header("📈 Visualizações")

# Frequência de Incidentes por Estação
st.markdown('<div class="lavender-box">', unsafe_allow_html=True)
st.subheader("📊 Frequência de Incidentes por Estação")
st.markdown("""
Este gráfico de barras mostra **quantos registros classificados como "Incidente" ocorreram em cada estação de amostragem**.
Ele é útil para identificar **quais estações têm maior concentração de eventos críticos**, permitindo análises direcionadas para prevenção ou investigação.
""")

if "Estação" in df.columns and "Categoria" in df.columns:
    freq_incidentes = df[df["Categoria"] == "Incidente"]["Estação"].value_counts()
    fig2, ax2 = plt.subplots()
    sns.barplot(x=freq_incidentes.index, y=freq_incidentes.values, ax=ax2)
    ax2.set_ylabel("Número de Incidentes")
    ax2.set_xlabel("Estação")
    ax2.set_title("Incidentes por Estação")
    st.pyplot(fig2)
else:
    st.warning("Coluna 'Estação' não encontrada no banco de dados.")
st.markdown('</div>', unsafe_allow_html=True)

# Histogramas
st.markdown('<div class="lavender-box">', unsafe_allow_html=True)
st.subheader("📉 Histogramas - Distribuição dos Metais")
st.markdown("""
Os histogramas a seguir mostram a **distribuição das concentrações de cada metal** na base de dados.  
Esses gráficos ajudam a entender:

- Se os valores estão concentrados em alguma faixa específica;
- Se existem **valores extremos (outliers)**;
- Se a distribuição é próxima de uma curva normal (simétrica);
- Qual o padrão geral da presença dos metais no ambiente analisado.
""")

for m in metais_disponiveis:
    if m in df.columns:
        st.markdown(f"**Distribuição de {m}:**")
        fig3, ax3 = plt.subplots()
        sns.histplot(df[m].dropna(), kde=True, bins=30, ax=ax3)
        ax3.set_xlabel(m)
        ax3.set_ylabel("Frequência")
        st.pyplot(fig3)
st.markdown('</div>', unsafe_allow_html=True)

# --- Rodapé ---
st.markdown("---")
st.markdown('<div class="footer">🎓 Projeto acadêmico - FIAP | Uso interno e institucional</div>', unsafe_allow_html=True)
