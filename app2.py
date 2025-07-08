import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# --- Configuración de la página de Streamlit ---
st.set_page_config(
    page_title="Análisis Cualitativo de Estudiantes",
    page_icon="🔬",
    layout="wide",
)

# --- CSS Personalizado para un Diseño Profesional ---
st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-1r6slb0 {
        border: 1px solid #e6e6e6; border-radius: 10px; padding: 25px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); background-color: #ffffff;
    }
    .st-emotion-cache-16txtl3 { background-color: #ffffff; border-right: 1px solid #e6e6e6; }
    h1, h2, h3 { color: #31333F; }
    .st-emotion-cache-1h9usn1 button {
        border-radius: 10px; margin: 0 5px; border: none; background-color: #f0f2f6;
    }
    .st-emotion-cache-1h9usn1 button[aria-selected="true"] {
        background-color: #1a5f7a; color: white;
    }
</style>
""", unsafe_allow_html=True)


# --- Funciones de Carga y Procesamiento de Datos ---

@st.cache_data
def load_data(file_path):
    """Carga los datos desde un archivo Excel (.xlsx)."""
    try:
        return pd.read_excel(file_path)
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo en la ruta '{file_path}'. Verifica que la ruta sea correcta.")
        return None

def code_observations(df):
    """Codifica observaciones como Positiva/Negativa y limpia el texto."""
    df_coded = df.copy()
    
    def get_sentiment(text):
        if pd.isna(text): return 'Neutra'
        text_str = str(text)
        if '(p)' in text_str: return 'Positiva'
        if '(n)' in text_str: return 'Negativa'
        return 'Neutra'

    for i in range(1, 4):
        obs_col = f'Observ{i}'
        df_coded[f'{obs_col}_Tipo'] = df_coded[obs_col].apply(get_sentiment)
        df_coded[obs_col] = df_coded[obs_col].apply(lambda x: re.sub(r'\s*\([pn]\)', '', str(x)) if pd.notna(x) else '')

    return df_coded

# --- Carga y Procesamiento de Datos ---
file_path = r'C:\Users\Usuario\Desktop\proyecto1\datos.xlsx'
df_raw = load_data(file_path)

if df_raw is None:
    st.stop()

df_coded = code_observations(df_raw)

# --- Interfaz de la Aplicación ---

st.title("🔬 Panel de Análisis Cualitativo de Desempeño")
st.markdown("Herramienta para la exploración y codificación de datos cualitativos y cuantitativos de estudiantes.")

# --- Barra Lateral ---
with st.sidebar:
    st.header("⚙️ Filtros de Análisis")
    program_options = sorted(df_coded['Prog'].unique())
    selected_program = st.multiselect(
        'Filtrar por Programa (Prog)',
        options=program_options,
        default=program_options,
        help="Selecciona los programas a incluir en el análisis."
    )

df_coded['Clave'] = df_coded['Clave'].astype(str)
df_filtered = df_coded[df_coded['Prog'].isin(selected_program)] if selected_program else df_coded

# --- Contenido Principal con Pestañas ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Visión General",
    "📈 Análisis Cruzado",
    "🔄 Comparación de Resultados",
    "☁️ Exploración de Temas",
    "🧑‍🎓 Casos Individuales"
])

with tab1:
    st.header("Análisis de Sentimiento de las Observaciones")
    st.markdown("Codificación inicial de las observaciones para identificar la polaridad del feedback general.")

    obs_tipos = df_filtered[['Observ1_Tipo', 'Observ2_Tipo', 'Observ3_Tipo']].melt(value_name='Tipo').dropna()
    sentiment_counts = obs_tipos[obs_tipos['Tipo'] != 'Neutra']['Tipo'].value_counts()

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Conteo Total de Observaciones")
        st.dataframe(sentiment_counts)
        total_obs = sentiment_counts.sum()
        if total_obs > 0:
            st.metric("Tasa de Feedback Positivo", f"{sentiment_counts.get('Positiva', 0) / total_obs:.1%}")

    with col2:
        if not sentiment_counts.empty:
            fig = px.pie(
                sentiment_counts,
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title="Distribución del Sentimiento en Todas las Observaciones",
                color=sentiment_counts.index,
                color_discrete_map={'Positiva': '#2ca02c', 'Negativa': '#d62728'}
            )
            st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ver datos codificados completos"):
        st.dataframe(df_filtered)

with tab2:
    st.header("Análisis Cruzado: Calificaciones vs. Tipo de Observación")
    st.markdown("Explora la relación entre la calificación obtenida y el tipo de feedback cualitativo recibido para un resultado específico.")
    
    selected_res_num = st.radio(
        "Selecciona el conjunto de resultados a analizar:",
        (1, 2, 3),
        format_func=lambda x: f"Resultados y Observaciones {x}",
        horizontal=True,
    )
    
    res_col = f'Res{selected_res_num}'
    obs_tipo_col = f'Observ{selected_res_num}_Tipo'

    cross_df = df_filtered[[res_col, obs_tipo_col]].copy()
    cross_df.rename(columns={res_col: 'Respuesta', obs_tipo_col: 'Tipo_Observacion'}, inplace=True)
    cross_df = cross_df[cross_df['Tipo_Observacion'] != 'Neutra']

    contingency_table = pd.crosstab(cross_df['Respuesta'], cross_df['Tipo_Observacion'])
    
    if not contingency_table.empty:
        fig = px.bar(
            contingency_table,
            barmode='group',
            title=f"Co-ocurrencia para Resultado {selected_res_num}",
            labels={'value': 'Cantidad de Observaciones', 'Respuesta': 'Calificación'},
            color_discrete_map={'Positiva': '#2ca02c', 'Negativa': '#d62728'}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos suficientes para el análisis cruzado con los filtros actuales.")

with tab3:
    st.header("Comparación entre Conjuntos de Resultados")
    st.markdown("Compara las distribuciones de los resultados cuantitativos y cualitativos a través de las tres mediciones.")

    # Comparación de Resultados Cuantitativos
    st.subheader("Comparación de Calificaciones (Res1, Res2, Res3)")
    df_res_melted = df_filtered[['Res1', 'Res2', 'Res3']].melt(var_name='Resultado', value_name='Calificación')
    df_res_counts = df_res_melted.groupby(['Resultado', 'Calificación']).size().reset_index(name='Cantidad')
    
    fig_res_comp = px.bar(
        df_res_counts,
        x='Calificación',
        y='Cantidad',
        color='Resultado',
        barmode='group',
        title="Distribución de Calificaciones por Resultado",
        category_orders={"Calificación": ["INSUFICIENTE", "ACEPTABLE", "BUENO", "MUY BUENO", "SOBRESALIENTE"]}
    )
    st.plotly_chart(fig_res_comp, use_container_width=True)

    # Comparación de Sentimiento Cualitativo
    st.subheader("Comparación de Sentimiento en Observaciones (Observ1, Observ2, Observ3)")
    df_obs_melted = df_filtered[['Observ1_Tipo', 'Observ2_Tipo', 'Observ3_Tipo']].melt(var_name='Conjunto de Observación', value_name='Tipo de Sentimiento')
    df_obs_melted = df_obs_melted[df_obs_melted['Tipo de Sentimiento'] != 'Neutra']
    df_obs_counts = df_obs_melted.groupby(['Conjunto de Observación', 'Tipo de Sentimiento']).size().reset_index(name='Cantidad')

    fig_obs_comp = px.bar(
        df_obs_counts,
        x='Conjunto de Observación',
        y='Cantidad',
        color='Tipo de Sentimiento',
        barmode='group',
        title="Distribución de Sentimiento por Conjunto de Observación",
        color_discrete_map={'Positiva': '#2ca02c', 'Negativa': '#d62728'}
    )
    st.plotly_chart(fig_obs_comp, use_container_width=True)


with tab4:
    st.header("Exploración de Temas Emergentes (Nube de Palabras)")
    st.markdown("Identifica los conceptos y temas más frecuentes en el texto de las observaciones.")
    
    all_obs_text = ' '.join(df_filtered['Observ1'].astype(str) + ' ' + df_filtered['Observ2'].astype(str) + ' ' + df_filtered['Observ3'].astype(str))

    if all_obs_text.strip():
        wordcloud = WordCloud(
            width=800, height=400, background_color='white',
            colormap='cividis'
        ).generate(all_obs_text)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.warning("No hay texto de observaciones para generar la nube de palabras.")

with tab5:
    st.header("Análisis de Casos Individuales")
    st.markdown("Realiza un análisis profundo de un estudiante específico, combinando sus datos cuantitativos y cualitativos.")

    student_options = sorted(df_filtered['Nombre y Email'].unique())
    selected_student = st.selectbox("Selecciona un estudiante para un estudio de caso", options=student_options)

    if selected_student:
        student_data = df_filtered[df_filtered['Nombre y Email'] == selected_student].iloc[0]
        st.write(f"#### Estudio de Caso: **{student_data['Nombre y Email'].split(' - ')[0]}**")

        st.subheader("Resultados Cuantitativos")
        cols = st.columns(3)
        cols[0].metric("Resultado 1", student_data['Res1'])
        cols[1].metric("Resultado 2", student_data['Res2'])
        cols[2].metric("Resultado 3", student_data['Res3'])

        st.subheader("Evidencia Cualitativa (Observaciones Codificadas)")
        for i in range(1, 4):
            obs_text = student_data[f'Observ{i}']
            obs_type = student_data[f'Observ{i}_Tipo']
            if obs_type == 'Positiva':
                st.success(f"**Observación {i} (Positiva):** {obs_text}")
            elif obs_type == 'Negativa':
                st.error(f"**Observación {i} (Negativa):** {obs_text}")
            else:
                st.info(f"**Observación {i} (Neutra):** {obs_text}")
