import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import requests
import json

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Dashboard de Ventas con IA",
    page_icon="🤖",
    layout="wide"
)

# --- CSS Personalizado para un Look Moderno ---
st.markdown("""
<style>
    .main {
        background-color: #F0F2F6;
    }
    .stMetric {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
		gap: 24px;
	}
	.stTabs [data-baseweb="tab"] {
		height: 50px;
        white-space: pre-wrap;
		background-color: transparent;
		border-radius: 4px 4px 0px 0px;
		gap: 1px;
		padding-top: 10px;
		padding-bottom: 10px;
    }
	.stTabs [aria-selected="true"] {
  		background-color: #FFFFFF;
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

# Entrada para la API Key de Gemini
api_key = st.sidebar.text_input("Ingresa tu API Key de Gemini", key="gemini_api_key", type="password", help="Obtén tu API Key de Google AI Studio.")

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
st.title("🛒 Dashboard de Ventas Corporativas con IA")
st.markdown("Análisis interactivo del rendimiento de ventas aumentado con Gemini.")

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
tab1, tab2, tab3, tab4 = st.tabs(["📊 Visión General", "🗺️ Análisis Geográfico/Categoría", "📄 Datos Detallados", "💬 Chat con IA"])

# Agrupaciones de datos para gráficos
df_time = df_filtered.set_index('Fecha').resample('M').agg({'Ventas': 'sum', 'Beneficio': 'sum'}).reset_index()
sales_by_region = df_filtered.groupby('Región')['Ventas'].sum().sort_values(ascending=False)
sales_by_category = df_filtered.groupby('Categoría')['Ventas'].sum()

with tab1:
    st.subheader("Tendencia de Ventas y Beneficios en el Tiempo")
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(x=df_time['Fecha'], y=df_time['Ventas'], mode='lines+markers', name='Ventas', line=dict(color='#1f77b4')))
    fig_time.add_trace(go.Scatter(x=df_time['Fecha'], y=df_time['Beneficio'], mode='lines+markers', name='Beneficio', line=dict(color='#2ca02c')))
    fig_time.update_layout(title='Ventas y Beneficios Mensuales', xaxis_title='Mes', yaxis_title='Monto ($)', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), template="plotly_white")
    st.plotly_chart(fig_time, use_container_width=True)
    
    img_bytes = fig_time.to_image(format="png", width=1200, height=700, scale=2)
    st.download_button(label="📥 Descargar Gráfico de Tendencia", data=img_bytes, file_name="tendencia_ventas.png", mime="image/png")

with tab2:
    col_geo1, col_geo2 = st.columns(2)
    with col_geo1:
        st.subheader("Ventas por Región")
        fig_region = px.bar(sales_by_region, x=sales_by_region.index, y=sales_by_region.values, title="Total de Ventas por Región", labels={'y': 'Ventas Totales ($)', 'x': 'Región'}, color=sales_by_region.index, template="plotly_white")
        st.plotly_chart(fig_region, use_container_width=True)
        img_bytes_region = fig_region.to_image(format="png", width=800, height=600, scale=2)
        st.download_button(label="📥 Descargar Gráfico de Región", data=img_bytes_region, file_name="ventas_por_region.png", mime="image/png")

    with col_geo2:
        st.subheader("Distribución de Ventas por Categoría")
        fig_category = px.pie(sales_by_category, values=sales_by_category.values, names=sales_by_category.index, title="Porcentaje de Ventas por Categoría", hole=0.4, template="plotly_white")
        fig_category.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_category, use_container_width=True)
        img_bytes_category = fig_category.to_image(format="png", width=800, height=600, scale=2)
        st.download_button(label="📥 Descargar Gráfico de Categoría", data=img_bytes_category, file_name="distribucion_categorias.png", mime="image/png")

with tab3:
    st.subheader("Explorador de Datos Filtrados")
    st.dataframe(df_filtered.sort_values('Fecha', ascending=False), use_container_width=True, hide_index=True)

with tab4:
    st.subheader("🤖 Chat de Análisis con Inteligencia Artificial")
    st.markdown("Haz preguntas en lenguaje natural sobre los datos filtrados. El asistente de IA utilizará la información actual del dashboard para responder.")

    if not api_key:
        st.warning("Por favor, ingresa tu API Key de Gemini en la barra lateral para activar el chat con IA.")
    else:
        # Inicializar el historial del chat en el estado de la sesión
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "¡Hola! Soy tu asistente de análisis de datos. ¿Qué te gustaría saber sobre las ventas actuales?"}]

        # Mostrar mensajes del historial
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Aceptar la entrada del usuario
        if prompt := st.chat_input("Pregúntame sobre los datos..."):
            # Añadir mensaje del usuario al historial
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Preparar la llamada a la API con el historial
            with st.chat_message("assistant"):
                with st.spinner("🧠 Pensando..."):
                    try:
                        # Preparar el contexto de datos para la IA
                        data_context = f"""
                        Aquí tienes un resumen de los datos de ventas actuales sobre los que debes basar tu respuesta:
                        
                        Métricas Clave (KPIs):
                        - Ventas Totales: ${total_sales:,.2f}
                        - Beneficio Total: ${total_profit:,.2f}
                        - Pedidos Totales: {total_orders}
                        - Valor Promedio por Pedido: ${avg_sale_value:,.2f}

                        Datos Detallados:
                        - Tendencia Mensual: {df_time.to_string()}
                        - Ventas por Región: {sales_by_region.to_string()}
                        - Ventas por Categoría: {sales_by_category.to_string()}
                        """
                        
                        # Construir el historial para la API
                        api_messages = []
                        api_messages.append({"role": "user", "parts": [{"text": "Actúa como un analista de datos experto y amigable. Tu tarea es responder preguntas sobre los datos de ventas de un dashboard. Basa tus respuestas únicamente en el contexto de datos que te proporciono en cada pregunta. Responde en español."}]})
                        api_messages.append({"role": "model", "parts": [{"text": "Entendido. Estoy listo para analizar los datos y responder preguntas."}]})

                        # Añadir historial de la conversación
                        for msg in st.session_state.messages:
                           role = "user" if msg["role"] == "user" else "model"
                           api_messages.append({"role": role, "parts": [{"text": msg["content"]}]})

                        # Añadir el contexto de datos a la última pregunta del usuario
                        api_messages[-1]["parts"].append({"text": f"\n\n--- CONTEXTO DE DATOS ACTUAL ---\n{data_context}"})

                        # Llamar a la API de Gemini
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
                        headers = {'Content-Type': 'application/json'}
                        payload = {"contents": api_messages}
                        
                        response = requests.post(url, headers=headers, data=json.dumps(payload))
                        response.raise_for_status()
                        
                        response_json = response.json()
                        full_response = response_json['candidates'][0]['content']['parts'][0]['text']
                        
                        st.markdown(full_response)
                        # Añadir respuesta de la IA al historial
                        st.session_state.messages.append({"role": "assistant", "content": full_response})

                    except requests.exceptions.HTTPError as errh:
                        st.error(f"Error HTTP: {errh.response.status_code} - {errh.response.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error de conexión: {e}")
                    except (KeyError, IndexError) as e:
                        st.error(f"No se pudo procesar la respuesta de la API. Verifica que la API Key sea correcta. Respuesta recibida: {response.text}")
                    except Exception as e:
                        st.error(f"Ocurrió un error inesperado: {e}")


