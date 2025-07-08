import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Dashboard de Ventas Moderno",
    page_icon="🛒",
    layout="wide"
)

st.markdown("""
<style>
    html, body, .main {
        background-color: #181A20 !important;
        color: #F4F4F4 !important;
    }
    .stApp, .stMarkdown, .stDataFrame, .stMetric, .stButton, .stDownloadButton, .stTabs, .stSidebar, .stTextInput, .stSelectbox, .stMultiSelect, .stDateInput {
        background-color: #181A20 !important;
        color: #F4F4F4 !important;
    }
    .stMetric {
        background-color: #23262F !important;
        color: #F4F4F4 !important;
        border: 1px solid #23262F !important;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #23262F !important;
        color: #F4F4F4 !important;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #181A20 !important;
        color: #F4F4F4 !important;
    }
    .stSidebar {
        background-color: #23262F !important;
        color: #F4F4F4 !important;
    }
    .stDownloadButton, .stButton {
        background-color: #23262F !important;
        color: #F4F4F4 !important;
        border: 1px solid #393E46 !important;
    }
    .stDataFrame {
        background-color: #23262F !important;
        color: #F4F4F4 !important;
    }
    .stTextInput, .stSelectbox, .stMultiSelect, .stDateInput {
        background-color: #23262F !important;
        color: #F4F4F4 !important;
        border: 1px solid #393E46 !important;
    }
    h1, h2, h3, h4, h5, h6, label, .css-10trblm, .css-1v0mbdj, .css-1d391kg, .css-1cpxqw2, .css-1offfwp, .css-1q8dd3e, .css-1lcbmhc, .css-1v3fvcr, .css-1y4p8pa, .css-1c7y2kd, .css-1vzeuhh, .css-1b0udgb, .css-1r6slb0, .css-1n76uvr, .css-1p05t8e, .css-1v3fvcr, .css-1v3fvcr, .css-1v3fvcr {
        color: #F4F4F4 !important;
    }
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
    html, body, .main {
        background-color: #181A20 !important;
        color: #F4F4F4 !important;
    }
    .stApp, .stMarkdown, .stDataFrame, .stMetric, .stButton, .stDownloadButton, .stTabs, .stSidebar, .stTextInput, .stSelectbox, .stMultiSelect, .stDateInput {
        background-color: #181A20 !important;
        color: #F4F4F4 !important;
    }
    .stMetric {
        background-color: #23262F !important;
        color: #F4F4F4 !important;
        border: 1px solid #23262F !important;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #23262F !important;
        color: #F4F4F4 !important;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #181A20 !important;
        color: #F4F4F4 !important;
    }
    .stSidebar {
        background-color: #23262F !important;
        color: #F4F4F4 !important;
    }
    .stDownloadButton, .stButton {
        background-color: #23262F !important;
        color: #F4F4F4 !important;
        border: 1px solid #393E46 !important;
    }
    .stDataFrame {
        background-color: #23262F !important;
        color: #F4F4F4 !important;
    }
    .stTextInput, .stSelectbox, .stMultiSelect, .stDateInput {
        background-color: #23262F !important;
        color: #F4F4F4 !important;
        border: 1px solid #393E46 !important;
    }
    h1, h2, h3, h4, h5, h6, label, .css-10trblm, .css-1v0mbdj, .css-1d391kg, .css-1cpxqw2, .css-1offfwp, .css-1q8dd3e, .css-1lcbmhc, .css-1v3fvcr, .css-1y4p8pa, .css-1c7y2kd, .css-1vzeuhh, .css-1b0udgb, .css-1r6slb0, .css-1n76uvr, .css-1p05t8e, .css-1v3fvcr, .css-1v3fvcr, .css-1v3fvcr {
        color: #F4F4F4 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Función para Simular Datos ---
@st.cache_data
def generate_data():
    """Genera un DataFrame de ventas simulado."""
    np.random.seed(42)
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 6, 26)
    num_days = (end_date - start_date).days
    dates = [start_date + timedelta(days=np.random.randint(num_days)) for _ in range(1000)]
    
    categories = ['Electrónica', 'Ropa', 'Hogar', 'Libros', 'Deportes']
    regions = ['Norte', 'Sur', 'Este', 'Oeste', 'Centro']
    
    data = {
        'Fecha': pd.to_datetime(dates),
        'Categoría': np.random.choice(categories, 1000, p=[0.3, 0.2, 0.2, 0.15, 0.15]),
        'Región': np.random.choice(regions, 1000),
        'Ventas': np.random.uniform(50, 2000, 1000).round(2),
        'Cantidad': np.random.randint(1, 10, 1000)
    }
    df = pd.DataFrame(data)
    df['Beneficio'] = (df['Ventas'] * np.random.uniform(0.1, 0.4, 1000)).round(2)
    return df

df = generate_data()

# --- Barra Lateral de Filtros ---
st.sidebar.header("🔍 Filtros del Dashboard")

# Filtro de Rango de Fechas
min_date = df['Fecha'].min().date()
max_date = df['Fecha'].max().date()
date_range = st.sidebar.date_input(
    "Selecciona un rango de fechas",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filtro de Región
selected_regions = st.sidebar.multiselect(
    "Selecciona regiones",
    options=df['Región'].unique(),
    default=df['Región'].unique()
)

# Filtro de Categoría
selected_categories = st.sidebar.multiselect(
    "Selecciona categorías",
    options=df['Categoría'].unique(),
    default=df['Categoría'].unique()
)

# --- Filtrar el DataFrame basado en la selección ---
start_date, end_date = date_range
df_filtered = df[
    (df['Fecha'].dt.date >= start_date) & 
    (df['Fecha'].dt.date <= end_date) &
    (df['Región'].isin(selected_regions)) &
    (df['Categoría'].isin(selected_categories))
]

if df_filtered.empty:
    st.warning("No hay datos disponibles para la selección actual. Por favor, ajusta los filtros.")
    st.stop()

# --- Título Principal ---
st.title("🛒 Dashboard de Ventas Corporativas")
st.markdown("Análisis interactivo del rendimiento de ventas.")

# --- KPIs (Métricas Principales) ---
total_sales = df_filtered['Ventas'].sum()
total_profit = df_filtered['Beneficio'].sum()
total_orders = df_filtered.shape[0]
avg_sale_value = total_sales / total_orders

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="💰 Ventas Totales", value=f"${total_sales:,.2f}")
with col2:
    st.metric(label="📈 Beneficio Total", value=f"${total_profit:,.2f}")
with col3:
    st.metric(label="📦 Pedidos Totales", value=f"{total_orders:,}")
with col4:
    st.metric(label="💵 Valor Promedio por Pedido", value=f"${avg_sale_value:,.2f}")

st.markdown("---")

# --- Pestañas para Gráficos ---
tab1, tab2, tab3 = st.tabs(["📊 Visión General de Ventas", "🗺️ Análisis Geográfico y por Categoría", "📄 Datos Detallados"])

with tab1:
    st.subheader("Tendencia de Ventas y Beneficios en el Tiempo")
    
    # Agrupar datos por mes
    df_time = df_filtered.set_index('Fecha').resample('M').agg({'Ventas': 'sum', 'Beneficio': 'sum'}).reset_index()

    # Gráfico de líneas
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(x=df_time['Fecha'], y=df_time['Ventas'], mode='lines+markers', name='Ventas', line=dict(color='#1f77b4')))
    fig_time.add_trace(go.Scatter(x=df_time['Fecha'], y=df_time['Beneficio'], mode='lines+markers', name='Beneficio', line=dict(color='#2ca02c')))
    fig_time.update_layout(
        title='Ventas y Beneficios Mensuales',
        xaxis_title='Mes',
        yaxis_title='Monto ($)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white"
    )
    st.plotly_chart(fig_time, use_container_width=True)
    
    # Botón de descarga para el gráfico de tiempo
    # Nota: Requiere la librería 'kaleido' (pip install kaleido)
    img_bytes = fig_time.to_image(format="png", width=1200, height=700, scale=2)
    st.download_button(
        label="📥 Descargar Gráfico de Tendencia",
        data=img_bytes,
        file_name="tendencia_ventas.png",
        mime="image/png"
    )


with tab2:
    col_geo1, col_geo2 = st.columns(2)
    
    with col_geo1:
        st.subheader("Ventas por Región")
        sales_by_region = df_filtered.groupby('Región')['Ventas'].sum().sort_values(ascending=False)
        fig_region = px.bar(
            sales_by_region,
            x=sales_by_region.index,
            y=sales_by_region.values,
            title="Total de Ventas por Región",
            labels={'y': 'Ventas Totales ($)', 'x': 'Región'},
            color=sales_by_region.index,
            template="plotly_white"
        )
        st.plotly_chart(fig_region, use_container_width=True)

        # Botón de descarga para el gráfico de región
        img_bytes_region = fig_region.to_image(format="png", width=800, height=600, scale=2)
        st.download_button(
            label="📥 Descargar Gráfico de Región",
            data=img_bytes_region,
            file_name="ventas_por_region.png",
            mime="image/png"
        )

    with col_geo2:
        st.subheader("Distribución de Ventas por Categoría")
        sales_by_category = df_filtered.groupby('Categoría')['Ventas'].sum()
        fig_category = px.pie(
            sales_by_category,
            values=sales_by_category.values,
            names=sales_by_category.index,
            title="Porcentaje de Ventas por Categoría",
            hole=0.4,
            template="plotly_white"
        )
        fig_category.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_category, use_container_width=True)

        # Botón de descarga para el gráfico de categoría
        img_bytes_category = fig_category.to_image(format="png", width=800, height=600, scale=2)
        st.download_button(
            label="📥 Descargar Gráfico de Categoría",
            data=img_bytes_category,
            file_name="distribucion_categorias.png",
            mime="image/png"
        )

with tab3:
    st.subheader("Explorador de Datos Filtrados")
    st.dataframe(
        df_filtered.sort_values('Fecha', ascending=False),
        use_container_width=True,
        hide_index=True
    )
