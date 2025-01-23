import streamlit as st
import pandas as pd
import geopandas as gpd
from geodatasets import get_path
import matplotlib.pyplot as plt
import seaborn as sns

# ----------------------------------------------------------------------
# 1. Carga de datos
# ----------------------------------------------------------------------
# Si no vas a usar el archivo Excel "data.xlsx", puedes comentarlo o quitarlo.
# file_path = 'data.xlsx'
# excel_data = pd.ExcelFile(file_path)
# df = pd.read_excel(excel_data, sheet_name='Sheet1')

@st.cache_data
def load_data():
    """
    Carga los datos necesarios para la aplicación:
      - Datos de obesidad (CSV)
      - Shapefile (mapa mundial) usando un dataset integrado de geopandas.
    """
    # Cargar dataset de obesidad
    obesity_data = pd.read_csv("BEFA58B_ALL_LATEST.csv")  # Ajusta el nombre a tu archivo CSV real
    # Cargar shapefile del mapa mundial
    file_path = "C:/Users/raulv/Documents/MBDS/HDVC/hdvc/ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp"
    world = gpd.read_file(file_path)
    
    return obesity_data, world

# ----------------------------------------------------------------------
# Cargar datos
# ----------------------------------------------------------------------
data, world = load_data()

# ----------------------------------------------------------------------
# 2. Configuración de la página y títulos en Streamlit
# ----------------------------------------------------------------------
st.title("Visualizing the Global Prevalence of Obesity")
st.sidebar.header("Filtros")

# ----------------------------------------------------------------------
# 3. Ajuste de columnas (si fuese necesario) para hacer el merge
#    Asegúrate de que 'GEO_NAME_SHORT' sea la columna que corresponde
#    a los nombres de país en tu dataset.
#    Si tu dataset ya está en la columna 'name', puedes omitir el rename.
# ----------------------------------------------------------------------
if "GEO_NAME_SHORT" in data.columns:
    data.rename(columns={"GEO_NAME_SHORT": "NAME"}, inplace=True)

# ----------------------------------------------------------------------
# 4. Unir datos del mapa con los datos de obesidad
# ----------------------------------------------------------------------
# Asegúrate de que 'name' exista en ambos dataframes.
# 'world' normalmente tiene una columna 'name' con los nombres de país,
# pero puedes revisar si coincide con los nombres de tu dataset (puede ser 'iso_a3', etc.)
world = world.merge(data, left_on="NAME", right_on="NAME", how="left")

# Eliminar la columna 'NAME' duplicada de world_merged
#world.drop(columns=["NAME"], inplace=True)
# ----------------------------------------------------------------------
# 5. Selección del gráfico en la barra lateral
# ----------------------------------------------------------------------
option = st.sidebar.radio(
    "Selecciona el gráfico que deseas visualizar:",
    ("Mapa Mundial", "Gráficas de Tendencias")
)

# ----------------------------------------------------------------------
# 6. Mapa Mundial con filtro por año
# ----------------------------------------------------------------------
if option == "Mapa Mundial":
    st.header("Mapa Mundial: Prevalencia de Obesidad por País")

    # Selección del año (DIM_TIME)
    if "DIM_TIME" in data.columns:
        available_years = sorted(data["DIM_TIME"].dropna().unique())
        selected_year = st.sidebar.selectbox("Selecciona un año:", available_years)
    else:
        st.warning("No se encontró la columna 'DIM_TIME' en los datos.")
        st.stop()

    # Filtrar los datos por el año seleccionado
    filtered_data = data[data["DIM_TIME"] == selected_year]

    # Asegurarse de que las columnas de los países coincidan en ambos DataFrames
    world_filtered = world.drop(columns=[col for col in world.columns if col not in ["NAME", "geometry"]], errors="ignore")
    world_filtered = world_filtered.merge(filtered_data, left_on="NAME", right_on="NAME", how="left")

    # Verificamos qué columna en 'filtered_data' tiene la prevalencia
    # Supongamos que es "RATE_PER_100_N". Ajusta según tu CSV real.
    if "RATE_PER_100_N" not in world_filtered.columns:
        st.warning("No se encontró la columna 'RATE_PER_100_N' para colorear el mapa.")
        st.stop()

    # Crear la figura y ejes
    fig, ax = plt.subplots(figsize=(15, 10))

    # Dibuja las fronteras de todos los países
    world.boundary.plot(ax=ax, linewidth=0.5, color='black')

    #  Pintar los países con la tasa de obesidad
    world_filtered.plot(
        column="RATE_PER_100_N",
        ax=ax,
        legend=True,
        cmap="OrRd",
        legend_kwds={
            'label': "Prevalencia de Obesidad (%)",
            'orientation': "horizontal"
        },
        missing_kwds={"color": "lightgrey"}
    )

    # Título y formateo
    ax.set_title(f"Mapa Mundial: Prevalencia de Obesidad ({selected_year})", fontsize=16)
    ax.set_axis_off()  # Oculta los ejes
    st.pyplot(fig)

# ----------------------------------------------------------------------
# 7. Gráficas de Tendencias
# ----------------------------------------------------------------------
elif option == "Gráficas de Tendencias":
    st.header("Evolución de la Prevalencia de Obesidad por Región")
    
    # Revisar si existe la columna 'region' en el dataset
    if "region" not in data.columns:
        st.warning("No se encontró la columna 'region' en los datos.")
        st.stop()
    
    # Selección de regiones
    regions = st.multiselect("Selecciona regiones:", data["NAME"].dropna().unique())
    
    if not regions:
        st.warning("Selecciona al menos una región para mostrar las tendencias.")
    else:
        filtered_data = data[data["NAME"].isin(regions)]
        
        # Verificamos la columna 'DIM_TIME' y 'RATE_PER_100_N' para la gráfica
        if "DIM_TIME" in filtered_data.columns and "RATE_PER_100_N" in filtered_data.columns:
            fig, ax = plt.subplots(figsize=(12, 8))
            sns.lineplot(
                data=filtered_data,
                x="DIM_TIME",
                y="RATE_PER_100_N",
                hue="NAME",
                marker="o",
                ax=ax
            )
            ax.set_title("Evolución de la Prevalencia de Obesidad por Región", fontsize=16)
            ax.set_xlabel("Año", fontsize=12)
            ax.set_ylabel("Tasa de Obesidad (%)", fontsize=12)
            plt.legend(title="Región", fontsize=10)
            plt.grid(alpha=0.3)
            st.pyplot(fig)
        else:
            st.warning("No se encontraron las columnas 'DIM_TIME' o 'RATE_PER_100_N' en los datos.")

# # Filtros en la barra lateral
# alcohol_filter = st.sidebar.slider("Nivel de Consumo de Alcohol", 0, 100, (10, 50))
# actividad_filter = st.sidebar.slider("Horas de Ejercicio", 0, 40, (5, 20))

# # Filtra los datos
# filtered_data = df

# # Visualización: Scatterplot
# st.subheader("Gráfico de Consumo de Alcohol vs Ejercicio Físico")
# fig, ax = plt.subplots()
# ax.scatter(filtered_data['columna 1'], filtered_data['columna 2'], alpha=0.7)
# ax.set_xlabel("Consumo de Alcohol")
# ax.set_ylabel("Horas de Ejercicio")
# st.pyplot(fig)

# # Tabla interactiva
# st.subheader("Datos Filtrados")
# st.dataframe(filtered_data)
