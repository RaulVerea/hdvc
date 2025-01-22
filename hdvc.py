import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Carga de datos
file_path = 'data.xlsx'
excel_data = pd.ExcelFile(file_path)
df = pd.read_excel(excel_data, sheet_name='Sheet1')

# Títulos
st.title("Relación entre Consumo de Alcohol y Ejercicio Físico")
st.sidebar.header("Filtros")

# Filtros en la barra lateral
alcohol_filter = st.sidebar.slider("Nivel de Consumo de Alcohol", 0, 100, (10, 50))
actividad_filter = st.sidebar.slider("Horas de Ejercicio", 0, 40, (5, 20))

# Filtra los datos
filtered_data = df

# Visualización: Scatterplot
st.subheader("Gráfico de Consumo de Alcohol vs Ejercicio Físico")
fig, ax = plt.subplots()
ax.scatter(filtered_data['columna 1'], filtered_data['columna 2'], alpha=0.7)
ax.set_xlabel("Consumo de Alcohol")
ax.set_ylabel("Horas de Ejercicio")
st.pyplot(fig)

# Tabla interactiva
st.subheader("Datos Filtrados")
st.dataframe(filtered_data)
