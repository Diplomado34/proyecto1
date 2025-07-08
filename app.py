import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# --- Configuración de la página de Streamlit ---
st.set_page_config(
    page_title="Panel de Análisis de Estudiantes",
    page_icon="✨",
    layout="wide",
)

# --- CSS Personalizado para un Diseño Moderno ---
st.markdown("""
<style>
    /* Estilo general del cuerpo */
    .main {
        background-color: #f0f2f6;
    }
    /* Estilo para las tarjetas */
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-1r6slb0 {
        border: 1px solid #e6e6e6;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        background-color: #ffffff;
    }
    /* Estilo para la barra lateral */
    .st-emotion-cache-16txtl3 {
        background-color: #ffffff;
        border-right: 1px solid #e6e6e6;
    }
    /* Estilo para los títulos */
    h1, h2, h3 {
        color: #31333F;
    }
    /* Estilo para los botones de las pestañas */
    .st-emotion-cache-1h9usn1 button {
        border-radius: 10px;
        margin: 0 5px;
        border: none;
        background-color: #f0f2f6;
    }
    .st-emotion-cache-1h9usn1 button[aria-selected="true"] {
        background-color: #007bff;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# --- Funciones de Carga y Limpieza de Datos ---

@st.cache_data
def load_data(file_path):
    """Carga los datos desde un archivo Excel (.xlsx)."""
    try:
        # Lee el archivo de Excel
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo en la ruta '{file_path}'. Por favor, verifica que la ruta sea correcta.")
        return None

def clean_data(df):
    """Limpia y transforma el DataFrame para el análisis."""
    df_cleaned = df.copy()
    response_mapping = {
        'INSUFICIENTE': 1, 'ACEPTABLE': 2, 'BUENO': 3,
        'MUY BUENO': 4, 'SOBRESALIENTE': 5, 'No disponible': None
    }
    res_cols = ['Res1', 'Res2', 'Res3']
    for col in res_cols:
        df_cleaned[f'{col}_Num'] = df_cleaned[col].map(response_mapping)

    obs_cols = ['Observ1', 'Observ2', 'Observ3']
    df_cleaned['Observaciones_Completas'] = df_cleaned[obs_cols].apply(
        lambda row: ' '.join(str(s) for s in row if pd.notna(s)), axis=1
    )
    df_cleaned['Observaciones_Completas'] = df_cleaned['Observaciones_Completas'].apply(
        lambda text: re.sub(r'\s*\([pn]\)', '', text)
    )
    return df_cleaned

# --- Carga y Procesamiento de Datos ---
# Se utiliza una cadena raw (r'...') para manejar correctamente las barras invertidas de Windows.
file_path = r'C:\Users\Usuario\Desktop\proyecto1\datos.xlsx'
df_raw = load_data(file_path)


if df_raw is None:
    st.stop()

df_cleaned = clean_data(df_raw)


# --- Interfaz de la Aplicación ---

# --- Título ---
st.title("✨ Panel de Análisis de Desempeño Estudiantil")
st.markdown("Una herramienta interactiva para explorar el rendimiento y las observaciones de los estudiantes.")

# --- Barra Lateral para Filtros ---
with st.sidebar:
    st.header("⚙️ Filtros de Visualización")
    program_options = sorted(df_cleaned['Prog'].unique())
    selected_program = st.multiselect(
        'Filtrar por Programa (Prog)',
        options=program_options,
        default=program_options,
        help="Selecciona uno o más programas para analizar."
    )

# Filtrar el dataframe
if selected_program:
    df_filtered = df_cleaned[df_cleaned['Prog'].isin(selected_program)]
else:
    df_filtered = df_cleaned

# --- Contenido Principal ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen General", "📈 Distribución de Respuestas", "☁️ Nube de Observaciones", "🧑‍🎓 Vista por Estudiante"])

with tab1:
    st.header("📄 Resumen General")
    st.markdown(f"Mostrando datos para **{len(df_filtered)}** de **{len(df_cleaned)}** estudiantes.")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Promedio Res. 1", f"{df_filtered['Res1_Num'].mean():.2f}")
    with col2:
        st.metric("Promedio Res. 2", f"{df_filtered['Res2_Num'].mean():.2f}")


    with st.expander("Ver tabla de datos completos"):
        st.dataframe(df_filtered, use_container_width=True)

    st.subheader("Estadísticas de Respuestas (Escala Numérica)")
    st.write(df_filtered[['Res1_Num', 'Res2_Num', 'Res3_Num']].describe())

with tab2:
    st.header("📊 Análisis de la Distribución de Respuestas")
    st.markdown("Visualiza cómo se distribuyen las respuestas categóricas.")

    res_cols_original = ['Res1', 'Res2', 'Res3']
    cols = st.columns(len(res_cols_original))
    order = ['INSUFICIENTE', 'ACEPTABLE', 'BUENO', 'MUY BUENO', 'SOBRESALIENTE', 'No disponible']

    for i, (col, res_col_name) in enumerate(zip(cols, res_cols_original)):
        with col:
            st.subheader(f"{res_col_name}")
            counts = df_filtered[res_col_name].value_counts().reindex(order).dropna()
            fig = px.bar(
                counts,
                y=counts.index,
                x=counts.values,
                orientation='h',
                labels={'y': 'Respuesta', 'x': 'Cantidad'},
                color=counts.index,
                color_discrete_sequence=px.colors.sequential.Mint
            )
            fig.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("☁️ Nube de Palabras de Observaciones")
    st.markdown("Visualiza los términos más frecuentes en las observaciones de los estudiantes seleccionados.")

    full_text = ' '.join(df_filtered['Observaciones_Completas'].dropna())

    if full_text:
        wordcloud = WordCloud(
            width=800, height=400, background_color='white',
            colormap='viridis', contour_color='steelblue', contour_width=1
        ).generate(full_text)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.warning("No hay suficientes datos de observaciones para generar una nube de palabras.")

with tab4:
    st.header("🧑‍🎓 Análisis Detallado por Estudiante")
    st.markdown("Selecciona un estudiante para ver sus datos y observaciones específicas.")

    student_options = sorted(df_filtered['Nombre y Email'].unique())
    selected_student = st.selectbox("Selecciona un estudiante", options=student_options)

    if selected_student:
        student_data = df_filtered[df_filtered['Nombre y Email'] == selected_student].iloc[0]
        st.write(f"#### Mostrando datos para: **{student_data['Nombre y Email'].split(' - ')[0]}**")

        st.subheader("Resultados de Evaluaciones")
        cols = st.columns(3)
        cols[0].metric("Respuesta 1", student_data['Res1'])
        cols[1].metric("Respuesta 2", student_data['Res2'])
        cols[2].metric("Respuesta 3", student_data['Res3'])

        st.subheader("Observaciones Registradas")
        st.info(f"**Observación 1:** {student_data['Observ1']}")
        st.success(f"**Observación 2:** {student_data['Observ2']}")
        st.warning(f"**Observación 3:** {student_data['Observ3']}")
