import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Configuración de la Página y Título ---
st.set_page_config(
    layout="wide",
    page_title="Simulador de Sumas de Riemann",
    page_icon="📊"
)

st.title("📊 Simulador Interactivo de Sumas de Riemann")
st.markdown("""
Esta aplicación visualiza cómo las **Sumas de Riemann** se utilizan para aproximar el área bajo una curva, lo que representa el concepto fundamental de la **integral definida**.

**Instrucciones:**
1.  Utiliza los controles en la **barra lateral** para seleccionar una función.
2.  Ajusta el **número de rectángulos (n)** y observa cómo la aproximación se vuelve más precisa.
3.  Compara los diferentes **tipos de sumas** (Izquierda, Derecha, Punto Medio).
4.  ¡Interactúa con el gráfico! Puedes hacer **zoom**, **desplazarte** y **pasar el cursor** sobre los elementos para ver más detalles.
""")

# --- Controles en la Barra Lateral ---
st.sidebar.header("⚙️ Panel de Control")

# Selección de función
# Usamos un diccionario para mapear nombres amigables a funciones lambda, cadenas LaTeX y sus integrales analíticas
functions = {
    'f(x) = x²': (lambda x: x**2, r'$f(x) = x^2$', lambda x: x**3 / 3),
    'f(x) = sin(x)': (lambda x: np.sin(x), r'$f(x) = \sin(x)$', lambda x: -np.cos(x)),
    'f(x) = x³ - 2x² + 5': (lambda x: x**3 - 2*x**2 + 5, r'$f(x) = x^3 - 2x^2 + 5$', lambda x: x**4/4 - 2*x**3/3 + 5*x),
    'f(x) = e^x': (lambda x: np.exp(x), r'$f(x) = e^x$', lambda x: np.exp(x)),
    'f(x) = 1/x': (lambda x: 1/x, r'$f(x) = \frac{1}{x}$', lambda x: np.log(x))
}
func_option = st.sidebar.selectbox(
    "1. Elige una función:",
    list(functions.keys())
)
func, func_latex, integral_func = functions[func_option]

# Intervalo de integración [a, b]
# Manejo especial para 1/x para evitar x=0
default_a = 0.1 if func_option == 'f(x) = 1/x' else 0.0
default_b = 5.0

col1_side, col2_side = st.sidebar.columns(2)
with col1_side:
    a = st.number_input("Límite Inferior (a):", value=default_a, step=0.5, format="%.2f")
with col2_side:
    b = st.number_input("Límite Superior (b):", value=default_b, step=0.5, format="%.2f")

if a >= b:
    st.sidebar.error("El límite inferior (a) debe ser menor que el límite superior (b).")
    st.stop()

# Slider para el número de rectángulos
n = st.sidebar.slider("2. Número de Rectángulos (n):", 1, 200, 15)

# Selección del tipo de Suma de Riemann
sum_type = st.sidebar.radio(
    "3. Tipo de Suma de Riemann:",
    ('Izquierda', 'Derecha', 'Punto Medio'),
    horizontal=True
)

st.sidebar.markdown("---")
st.sidebar.info(f"**Tipo Seleccionado: {sum_type}**\n\nLa altura de cada rectángulo se determina por el valor de la función en el extremo **{sum_type.lower().replace('punto medio', 'del punto medio')}** de su base.")

# --- Cálculos ---
# Ancho de cada rectángulo
delta_x = (b - a) / n

# Puntos en x para la base de los rectángulos
x_points = np.linspace(a, b, n + 1)

# Puntos en x para determinar la altura de los rectángulos
if sum_type == 'Izquierda':
    sample_x_points = x_points[:-1]
elif sum_type == 'Derecha':
    sample_x_points = x_points[1:]
else:  # Punto Medio
    sample_x_points = (x_points[:-1] + x_points[1:]) / 2

# Alturas de los rectángulos
y_heights = func(sample_x_points)

# Área aproximada
approximated_area = np.sum(y_heights * delta_x)

# Área real (integral definida)
try:
    real_area = integral_func(b) - integral_func(a)
    error = np.abs(real_area - approximated_area)
except (ValueError, ZeroDivisionError) as e:
    st.error(f"No se puede calcular el área real en el intervalo dado. Error: {e}")
    st.stop()


# --- Visualización en el Panel Principal ---
st.header("📈 Resultados y Visualización")

# Mostrar resultados
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label=f"Área Aproximada ({sum_type})", value=f"{approximated_area:.5f}")
with col2:
    st.metric(label="Área Real (Integral)", value=f"{real_area:.5f}")
with col3:
    st.metric(label="Error Absoluto", value=f"{error:.5f}", delta=f"{-100 * error / real_area:.2f}%" if real_area != 0 else "N/A")

# --- Gráfico con Plotly ---
fig = go.Figure()

# Añadir los rectángulos
bar_color = {'Izquierda': '#ef476f', 'Derecha': '#ffd166', 'Punto Medio': '#06d6a0'}[sum_type]
fig.add_trace(go.Bar(
    x=sample_x_points,
    y=y_heights,
    width=delta_x,
    marker_color=bar_color,
    marker_line_width=1,
    marker_line_color='black',
    opacity=0.7,
    name=f'Rectángulos ({sum_type})'
))

# Añadir la curva de la función
x_curve = np.linspace(a, b, 500)
y_curve = func(x_curve)
fig.add_trace(go.Scatter(
    x=x_curve,
    y=y_curve,
    mode='lines',
    line=dict(color='#0077b6', width=3),
    name=f"Curva de {func_latex}",
    fill='tozeroy',  # Rellena el área bajo la curva
    fillcolor='rgba(0, 119, 182, 0.15)'
))

# Actualizar el diseño para un aspecto limpio y profesional
fig.update_layout(
    title=dict(text=f"Suma de Riemann ({sum_type}) con n = {n} rectángulos", font=dict(size=20), x=0.5),
    xaxis_title="x",
    yaxis_title="f(x)",
    bargap=0,  # Sin espacio entre las barras para una apariencia continua
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    template="plotly_white",
    height=500
)

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig, use_container_width=True)


# --- Sección de Explicación ---
st.markdown("---")
st.header("🧠 ¿Qué estamos viendo?")
st.markdown(r"""
* **Aumenta `n`**: A medida que incrementas el número de rectángulos (`n`), la aproximación del área se vuelve mucho más precisa y el **error disminuye**. Visualmente, los rectángulos se ajustan cada vez mejor a la forma de la curva.

* **Cambia el método**: Compara los métodos "Izquierda", "Derecha" y "Punto Medio".
    * Para una función **creciente**, la suma izquierda **subestima** el área, mientras que la suma derecha la **sobreestima**.
    * Para una función **decreciente**, ocurre lo contrario.
    * Generalmente, la suma del **punto medio** converge más rápidamente hacia el valor real (tiene un error menor para el mismo `n`).

* **El Límite es la Integral**: El concepto fundamental del cálculo integral es que si tomas el límite cuando `n` tiende a infinito ($n \to \infty$), la suma de Riemann se convierte *exactamente* en la integral definida.

$$
\int_{a}^{b} f(x) \,dx = \lim_{n \to \infty} \sum_{i=1}^{n} f(x_i^*) \Delta x
$$
""")
