import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Innovación - InnovaChile Corfo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título y descripción del dashboard
st.title("📊 Dashboard de Innovación - InnovaChile Corfo")
st.markdown("Este dashboard interactivo muestra indicadores clave de los proyectos de innovación financiados por **InnovaChile Corfo**.")
st.markdown("---")

# Cargar los datos
try:
    df = pd.read_csv("DataInnovacion - InnovaChile Corfo (1).csv", sep=';')
    
    # Limpieza y preparación de datos
    df.columns = df.columns.str.replace(r'[^\w\s]', '', regex=True).str.replace(' ', '_').str.strip()
    df['Financiamiento_Innova'] = df['Financiamiento_Innova'].replace({'\$': '', '\.': ''}, regex=True).astype(float)
    df['Aprobado_Privado_Pecuniario'] = df['Aprobado_Privado_Pecuniario'].replace({'\$': '', '\.': ''}, regex=True).astype(float)
    df['Monto_Certificado_Ley'] = df['Monto_Certificado_Ley'].replace({'\$': '', '\.': ''}, regex=True).astype(float)
    df['Inicio_Actividad_Economica'] = pd.to_datetime(df['Inicio_Actividad_Economica'], errors='coerce')
    df['Año_Adjudicacion'] = pd.to_numeric(df['Año_Adjudicacion'], errors='coerce').fillna(0).astype(int)
    
except Exception as e:
    st.error(f"Error al cargar o procesar el archivo: {e}")
    st.stop()

# --- Barra lateral para filtros ---
st.sidebar.header("⚙️ Opciones de Filtro")

# Filtro de año
años_disponibles = sorted(df['Año_Adjudicacion'].unique())
año_seleccionado = st.sidebar.slider(
    'Selecciona un Año de Adjudicación',
    min_value=min(años_disponibles),
    max_value=max(años_disponibles),
    value=(min(años_disponibles), max(años_disponibles))
)

# Filtro de región
regiones_disponibles = sorted(df['Region'].dropna().unique())
region_seleccionada = st.sidebar.multiselect(
    'Filtrar por Región',
    options=regiones_disponibles,
    default=regiones_disponibles
)

# Filtro de sector económico
sectores_disponibles = sorted(df['Sector_Economico'].dropna().unique())
sector_seleccionado = st.sidebar.multiselect(
    'Filtrar por Sector Económico',
    options=sectores_disponibles,
    default=sectores_disponibles
)

# Aplicar filtros
df_filtrado = df[
    (df['Año_Adjudicacion'] >= año_seleccionado[0]) &
    (df['Año_Adjudicacion'] <= año_seleccionado[1]) &
    (df['Region'].isin(region_seleccionada)) &
    (df['Sector_Economico'].isin(sector_seleccionado))
]

if df_filtrado.empty:
    st.warning("No hay datos que coincidan con los filtros seleccionados.")
    st.stop()

# --- Visualización de Indicadores Clave ---
st.header("📈 Indicadores Clave")

total_proyectos = df_filtrado.shape[0]
inversion_innova = df_filtrado['Financiamiento_Innova'].sum()
inversion_privada = df_filtrado['Aprobado_Privado_Pecuniario'].sum()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Proyectos", value=f"{total_proyectos}")
with col2:
    st.metric(label="Financiamiento Innova Total", value=f"${inversion_innova:,.0f}")
with col3:
    st.metric(label="Aprobado Privado Total", value=f"${inversion_privada:,.0f}")

st.markdown("---")

# --- Visualización por Tipo de Innovación ---
st.header("📊 Proyectos por Tipo de Innovación")

# Agrupar y contar proyectos por tipo de innovación
tipo_innovacion_counts = df_filtrado['Tipo_Innovacion'].value_counts().reset_index()
tipo_innovacion_counts.columns = ['Tipo_Innovacion', 'Cantidad_Proyectos']

fig_tipo_innovacion = px.pie(
    tipo_innovacion_counts,
    values='Cantidad_Proyectos',
    names='Tipo_Innovacion',
    title='Distribución de Proyectos por Tipo de Innovación',
    hole=0.4
)
fig_tipo_innovacion.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
st.plotly_chart(fig_tipo_innovacion, use_container_width=True)

st.markdown("---")

# --- Visualización por Región ---
st.header("🗺️ Distribución Geográfica de Proyectos")

region_counts = df_filtrado['Region'].value_counts().reset_index()
region_counts.columns = ['Region', 'Cantidad_Proyectos']

fig_region = px.bar(
    region_counts,
    x='Region',
    y='Cantidad_Proyectos',
    title='Cantidad de Proyectos por Región',
    color='Region',
    labels={'Cantidad_Proyectos': 'Cantidad de Proyectos', 'Region': 'Región'}
)
st.plotly_chart(fig_region, use_container_width=True)

st.markdown("---")

# --- Visualización por Sector Económico ---
st.header("🏭 Proyectos por Sector Económico")

sector_counts = df_filtrado['Sector_Economico'].value_counts().reset_index()
sector_counts.columns = ['Sector_Economico', 'Cantidad_Proyectos']
sector_counts = sector_counts.sort_values(by='Cantidad_Proyectos', ascending=False)

fig_sector = px.bar(
    sector_counts,
    x='Cantidad_Proyectos',
    y='Sector_Economico',
    orientation='h',
    title='Cantidad de Proyectos por Sector Económico',
    color='Sector_Economico',
    labels={'Cantidad_Proyectos': 'Cantidad de Proyectos', 'Sector_Economico': 'Sector Económico'}
)
fig_sector.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_sector, use_container_width=True)

st.markdown("---")

# --- Tabla de datos filtrada ---
st.header("📋 Tabla de Datos Filtrada")
st.dataframe(df_filtrado)

csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
st.download_button(
    "💾 Exportar datos filtrados a CSV",
    csv_data,
    "datos_innovacion_filtrados.csv",
    "text/csv"
)
