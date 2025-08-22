#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 15:13:40 2025

@author: mariano
"""

import pandas as pd

# %% Limpieza


# === 1. Leer el archivo Excel ===
df = pd.read_excel("data_estudiantes.xlsx", header=[0,1])

# === 2. Aplanar columnas ===
df.columns = [
    f"{a}_{b}".strip("_")   # si b está vacío no agrega guion bajo
    for a, b in df.columns.to_flat_index()
]

# Ahora ya tenemos columnas del estilo:
# ['Actividad', 'Alumno - Legajo', 'Apellido y Nombre - Tipo Nro Documento',
#  '2017_Aprobado', '2017_Promovido', '2017_Reprobado',
#  '2018_Aprobado', '2018_Ausente', '2018_Promovido', ...]

# === 3. Separar columnas compuestas ===

# Actividad: separar código y nombre
df[['Actividad_Cod', 'Actividad_Nombre']] = df['Unnamed: 0_level_0_Actividad'].str.extract(r"\((\d+)\)\s*-\s*(.*)")

# Alumno - Legajo
df[['Alumno_Cod', 'Legajo']] = df['Unnamed: 1_level_0_Alumno - Legajo'].str.split('-', expand=True)
df['Alumno_Cod'] = df['Alumno_Cod'].str.strip()
df['Legajo'] = df['Legajo'].str.strip()

# Apellido y Nombre + DNI
df[['ApellidoNombre', 'DNI']] = df['Unnamed: 2_level_0_Apellido y Nombre - Tipo Nro Documento'].str.split('- DNI', expand=True)
df['ApellidoNombre'] = df['ApellidoNombre'].str.strip()
df['DNI'] = df['DNI'].str.strip()

# === 4. Reordenar columnas principales primero ===
cols_principales = ['Actividad_Cod','Actividad_Nombre','Alumno_Cod','Legajo','ApellidoNombre','DNI']
otros = [c for c in df.columns if c not in cols_principales 
         and c not in ['Unnamed: 0_level_0_Actividad','Unnamed: 1_level_0_Alumno - Legajo','Unnamed: 2_level_0_Apellido y Nombre - Tipo Nro Documento']]
df = df[cols_principales + otros]

# === 5. Guardar limpio (opcional) ===
# df.to_excel("data_estudiantes_limpio.xlsx", index=False)

# %% Análisis por materia

df = pd.read_excel("data_estudiantes_limpio.xlsx")

# Partimos del dataframe ya reestructurado (con columnas como 2017_Aprobado, etc.)

# === 1. Pasar a formato largo ===
df_long = df.melt(
    id_vars=['Actividad_Cod', 'Actividad_Nombre', 'Alumno_Cod', 'Legajo', 'ApellidoNombre', 'DNI'],
    var_name="Periodo",
    value_name="Valor"
)

# === 2. Separar Año y Resultado (ej: "2017_Aprobado" → "2017", "Aprobado") ===
df_long[['Año', 'Resultado']] = df_long['Periodo'].str.split("_", expand=True)

# === 3. Filtrar solo filas con "SI" (es decir, cuando ocurrió el evento) ===
df_long = df_long[df_long['Valor'].str.upper() == "SI"]

# === 4. Agrupar y contar alumnos por asignatura, año y resultado ===
df_resumen = (
    df_long.groupby(['Actividad_Cod', 'Actividad_Nombre', 'Año', 'Resultado'])
    .size()
    .reset_index(name="Cantidad")
)

# Ordenar años para que quede más prolijo
df_resumen['Año'] = df_resumen['Año'].astype(int)
df_resumen = df_resumen.sort_values(['Actividad_Cod', 'Año', 'Resultado'])

# === 5. (Opcional) Pivotear para tener una tabla Año vs. Resultados ===
df_pivot = df_resumen.pivot_table(
    index=['Actividad_Cod', 'Actividad_Nombre', 'Año'],
    columns='Resultado',
    values='Cantidad',
    fill_value=0
).reset_index()

# %% Análisis de resultado por materia de 2017 a 2024

import matplotlib.pyplot as plt
import seaborn as sns

# Pasamos a formato largo
df_plot_long = df_pivot.melt(
    id_vars=['Actividad_Cod', 'Actividad_Nombre', 'Año'],
    value_vars=['Aprobado', 'Reprobado', 'Promovido', 'Ausente'],
    var_name="Resultado",
    value_name="Cantidad"
)

# Calcular totales por año y materia
totales = df_plot_long.groupby(['Actividad_Cod', 'Año'])['Cantidad'].sum().reset_index(name='Total')

# Unir los totales al dataset largo
df_plot_long = df_plot_long.merge(totales, on=['Actividad_Cod', 'Año'])

# Calcular porcentaje
df_plot_long['Porcentaje'] = (df_plot_long['Cantidad'] / df_plot_long['Total']) * 100

# Lista de materias
materias = df_plot_long['Actividad_Cod'].unique()

# Colores fijos para los resultados
palette = {
    "Aprobado": "green",
    "Reprobado": "red",
    "Promovido": "blue",
    "Ausente": "gray"
}

for cod in materias:
    df_mat = df_plot_long[df_plot_long['Actividad_Cod'] == cod]

    fig, ax1 = plt.subplots(figsize=(9,5))

    # === Eje Y1: porcentajes ===
    sns.lineplot(
        data=df_mat,
        x="Año", y="Porcentaje", hue="Resultado", marker="o",
        palette=palette, ax=ax1
    )

    ax1.set_ylabel("Porcentaje de estudiantes (%)")
    ax1.set_xlabel("Año")
    ax1.set_ylim(0, 100)  # porcentajes de 0 a 100
    ax1.grid(True)

    # === Eje Y2: totales ===
    ax2 = ax1.twinx()
    sns.lineplot(
        data=df_mat.drop_duplicates(['Año','Total']),
        x="Año", y="Total", color="black", marker="s", linestyle="--", ax=ax2, label="Total"
    )
    ax2.set_ylabel("Total de estudiantes")

    # Título
    nombre = df_mat['Actividad_Nombre'].iloc[0]
    plt.title(f"Evolución académica (porcentaje + total) - {nombre}")

    # Manejo de leyendas (unir ambas)
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc="upper left")

    plt.show()
    # (opcional guardar)
    fig.savefig(f"evolucion_pct_total_{cod}.png", dpi=150, bbox_inches="tight")
    plt.close()


# %%

# Crear los datos organizados por año y nivel
data = {
    'Año': [
        # 1er Año (6 materias)
        1, 1, 1, 1, 1, 1,
        # 2do Año (8 materias)
        2, 2, 2, 2, 2, 2, 2, 2,
        # 3er Año (8 materias)
        3, 3, 3, 3, 3, 3, 3, 3,
        # 4to Año (7 materias)
        4, 4, 4, 4, 4, 4, 4,
        # 5to Año (6 materias)
        5, 5, 5, 5, 5, 5,
        # 6to Año (4 materias)
        6, 6, 6, 6
    ],
    'Asignatura': [
        # 1er Año
        'Álgebra y Geometría Analítica', 'Análisis Matemático I', 'Física I', 
        'Informática I', 'Ingeniería y Sociedad', 'Química General',
        
        # 2do Año
        'Análisis Matemático II', 'Física II', 'Informática II', 'Inglés I', 
        'Diseño Asistido por Computadora', 'Análisis de Señales y Sistemas', 
        'Física Electrónica', 'Probabilidad y Estadística',
        
        # 3er Año
        'Análisis de Señales y Sistemas', 'Dispositivos Electrónicos', 
        'Medios de Enlace', 'Técnicas Digitales I', 'Teoría de los Circuitos I', 
        'Inglés II', 'Electrónica Aplicada I', 'Legislación',
        
        # 4to Año
        'Electrónica Aplicada II', 'Máquinas e Instalaciones Eléctricas', 
        'Medidas Electrónicas I', 'Seguridad, Higiene y Medio Ambiente', 
        'Sistemas de Comunicaciones', 'Técnicas Digitales II', 
        'Teoría de los Circuitos II',
        
        # 5to Año
        'Electrónica Aplicada III', 'Electrónica de Potencia', 
        'Medidas Electrónicas II', 'Sistemas de Control', 
        'Técnicas Digitales III', 'Tecnología Electrónica',
        
        # 6to Año
        'Proyecto Final', 'Economía', 'Organización Industrial', 
        'Materias Electivas'
    ]
}

# Crear el DataFrame
df_materias = pd.DataFrame(data)

# Filtrar filas vacías y resetear índice
df_materias = df_materias[df_materias['Asignatura'] != ''].reset_index(drop=True)

# Mostrar el DataFrame
# print(df_materias)

# %% Análisis por año de la carrera

# Primero, unimos la información del año de la carrera al dataframe principal
df_con_año = df.merge(df_materias[['Asignatura', 'Año']], 
                     left_on='Actividad_Nombre', 
                     right_on='Asignatura',
                     how='left')

# Verificamos el resultado
print(f"Filas en df original: {len(df)}")
print(f"Filas después del merge: {len(df_con_año)}")
print(f"Materias sin año asignado: {df_con_año['Año'].isna().sum()}")

# Mostramos las materias que no encontraron coincidencia
if df_con_año['Año'].isna().sum() > 0:
    print("\nMaterias sin año asignado:")
    print(df_con_año[df_con_año['Año'].isna()]['Actividad_Nombre'].unique())
    
    
# Preparamos los datos para el análisis por año de carrera
años_carrera = sorted(df_con_año['Año'].dropna().unique())

# Procesamos los datos para tener la misma estructura que antes pero por año de carrera
df_por_año = pd.DataFrame()

for año in años_carrera:
    df_año = df_con_año[df_con_año['Año'] == año]
    
    # Sumamos los resultados por año académico para todas las materias de ese año de carrera
    for año_academico in range(2017, 2025):
        aprobados = df_año[f'{año_academico}_Aprobado'].sum()
        reprobados = df_año[f'{año_academico}_Reprobado'].sum()
        promovidos = df_año[f'{año_academico}_Promovido'].sum()
        ausentes = df_año[f'{año_academico}_Ausente'].sum() if f'{año_academico}_Ausente' in df_año.columns else 0
        
        temp_df = pd.DataFrame({
            'Año': [año],
            'Año_Academico': [año_academico],
            'Aprobado': [aprobados],
            'Reprobado': [reprobados],
            'Promovido': [promovidos],
            'Ausente': [ausentes]
        })
        
        df_por_año = pd.concat([df_por_año, temp_df], ignore_index=True)

# Pasamos a formato largo
df_plot_long_año = df_por_año.melt(
    id_vars=['Año', 'Año_Academico'],
    value_vars=['Aprobado', 'Reprobado', 'Promovido', 'Ausente'],
    var_name="Resultado",
    value_name="Cantidad"
)

# Calcular totales por año de carrera y año académico
totales_año = df_plot_long_año.groupby(['Año', 'Año_Academico'])['Cantidad'].sum().reset_index(name='Total')

# Unir los totales al dataset largo
df_plot_long_año = df_plot_long_año.merge(totales_año, on=['Año', 'Año_Academico'])

# Calcular porcentaje
df_plot_long_año['Porcentaje'] = (df_plot_long_año['Cantidad'] / df_plot_long_año['Total']) * 100

# Colores fijos para los resultados
palette = {
    "Aprobado": "green",
    "Reprobado": "red",
    "Promovido": "blue",
    "Ausente": "gray"
}

# Generar gráficos por año de carrera
for año_carrera in años_carrera:
    df_año_carrera = df_plot_long_año[df_plot_long_año['Año'] == año_carrera]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # === Eje Y1: porcentajes ===
    sns.lineplot(
        data=df_año_carrera,
        x="Año_Academico", y="Porcentaje", hue="Resultado", marker="o",
        palette=palette, ax=ax1
    )

    ax1.set_ylabel("Porcentaje de estudiantes (%)")
    ax1.set_xlabel("Año Académico")
    ax1.set_ylim(0, 100)
    ax1.grid(True)
    ax1.set_xticks(range(2017, 2025))

    # === Eje Y2: totales ===
    ax2 = ax1.twinx()
    sns.lineplot(
        data=df_año_carrera.drop_duplicates(['Año_Academico', 'Total']),
        x="Año_Academico", y="Total", color="black", marker="s", 
        linestyle="--", ax=ax2, label="Total"
    )
    ax2.set_ylabel("Total de estudiantes")

    # Título
    plt.title(f"Evolución académica - Año {int(año_carrera)} de la carrera\n"
              f"(Porcentaje por resultado + total de estudiantes)")

    # Manejo de leyendas
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc="best")

    plt.tight_layout()
    plt.show()
    
    # Guardar gráfico
    fig.savefig(f"evolucion_año_carrera_{int(año_carrera)}.png", dpi=150, bbox_inches="tight")
    plt.close()

# También podemos hacer un análisis comparativo entre años de carrera
print("\nResumen estadístico por año de carrera:")
resumen_años = df_plot_long_año.groupby(['Año', 'Resultado'])['Cantidad'].sum().unstack()
print(resumen_años)

# Porcentajes promedio por año de carrera
print("\nPorcentajes promedio por año de carrera:")
porcentajes_promedio = df_plot_long_año.groupby(['Año', 'Resultado'])['Porcentaje'].mean().unstack()
print(porcentajes_promedio.round(2))




# %%



# Función para convertir Si/No a 1/0
def convertir_si_no(valor):
    if pd.isna(valor):
        return 0
    elif valor == 'Si':
        return 1
    else:
        return 0

# Procesamos los datos para tener la misma estructura que antes pero por año de carrera
df_por_año = pd.DataFrame()

for año in años_carrera:
    df_año = df_con_año[df_con_año['Año_Carrera'] == año]
    
    # Sumamos los resultados por año académico para todas las materias de ese año de carrera
    for año_academico in range(2017, 2025):
        # Convertimos las columnas a valores numéricos
        col_aprobado = f'{año_academico}_Aprobado'
        col_reprobado = f'{año_academico}_Reprobado'
        col_promovido = f'{año_academico}_Promovido'
        
        # Aseguramos que las columnas existan
        if col_aprobado in df_año.columns:
            aprobados = df_año[col_aprobado].apply(convertir_si_no).sum()
        else:
            aprobados = 0
            
        if col_reprobado in df_año.columns:
            reprobados = df_año[col_reprobado].apply(convertir_si_no).sum()
        else:
            reprobados = 0
            
        if col_promovido in df_año.columns:
            promovidos = df_año[col_promovido].apply(convertir_si_no).sum()
        else:
            promovidos = 0
        
        # Para ausentes, verificamos si la columna existe
        col_ausente = f'{año_academico}_Ausente'
        if col_ausente in df_año.columns:
            ausentes = df_año[col_ausente].apply(convertir_si_no).sum()
        else:
            ausentes = 0
        
        temp_df = pd.DataFrame({
            'Año_Carrera': [año],
            'Año_Academico': [año_academico],
            'Aprobado': [aprobados],
            'Reprobado': [reprobados],
            'Promovido': [promovidos],
            'Ausente': [ausentes]
        })
        
        df_por_año = pd.concat([df_por_año, temp_df], ignore_index=True)

# También podemos hacer una versión más eficiente usando apply en todo el dataframe
# Alternativa más eficiente:
def procesar_año_academico(df_grupo, año_academico):
    """Procesa un año académico específico para un grupo de materias"""
    resultados = {}
    
    for resultado in ['Aprobado', 'Reprobado', 'Promovido', 'Ausente']:
        col_name = f'{año_academico}_{resultado}'
        if col_name in df_grupo.columns:
            resultados[resultado] = df_grupo[col_name].apply(convertir_si_no).sum()
        else:
            resultados[resultado] = 0
    
    return resultados

# O usando una versión vectorizada (más rápida para grandes datasets):
def convertir_columna_vectorizada(columna):
    """Versión vectorizada para convertir Si/No a 1/0"""
    if columna.dtype == 'object':  # Si es string
        return (columna == 'Si').fillna(False).astype(int)
    else:  # Si ya es numérico o tiene NaN
        return columna.fillna(0).astype(int)

# Re-procesar con método vectorizado
df_por_año = pd.DataFrame()

for año in años_carrera:
    df_año = df_con_año[df_con_año['Año_Carrera'] == año]
    
    for año_academico in range(2017, 2025):
        resultados = {}
        
        for resultado in ['Aprobado', 'Reprobado', 'Promovido']:
            col_name = f'{año_academico}_{resultado}'
            if col_name in df_año.columns:
                resultados[resultado] = convertir_columna_vectorizada(df_año[col_name]).sum()
            else:
                resultados[resultado] = 0
        
        # Ausente puede no existir para algunos años
        col_ausente = f'{año_academico}_Ausente'
        if col_ausente in df_año.columns:
            resultados['Ausente'] = convertir_columna_vectorizada(df_año[col_ausente]).sum()
        else:
            resultados['Ausente'] = 0
        
        temp_df = pd.DataFrame({
            'Año_Carrera': [año],
            'Año_Academico': [año_academico],
            **resultados
        })
        
        df_por_año = pd.concat([df_por_año, temp_df], ignore_index=True)

# Verificamos los resultados
print("Primeras filas del dataframe procesado:")
print(df_por_año.head())
print(f"\nTotal de registros: {len(df_por_año)}")

# Verificamos que no haya NaN en las sumas
print("\nValores nulos por columna:")
print(df_por_año.isnull().sum())