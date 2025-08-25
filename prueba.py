#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 15:13:40 2025

@author: mariano
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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
df_long = df_long[df_long['Valor'] == 1]



# Crear los datos organizados por año y nivel
data = {
    'Año_nivel': [
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

# === 1. Unir df_long con df_materias ===
df_con_año = df_long.merge(
    df_materias[['Asignatura', 'Año_nivel']],
    left_on="Actividad_Nombre",
    right_on="Asignatura",
    how="left"
)

df_con_año = df_con_año[['Actividad_Cod', 'Actividad_Nombre', 'Año_nivel', 'Alumno_Cod', 'Legajo', 'ApellidoNombre', 'DNI', 'Año', 'Resultado']]


# === 5. Guardar limpio (opcional) ===
df_con_año.to_excel("data_estudiantes_limpio_largo_con_nivel.xlsx", index=False)


# %%

df_long = pd.read_excel("data_estudiantes_limpio_largo_con_nivel.xlsx")

# %% Análisis de resultado por materia de 2017 a 2024

# Configurar estilo de los gráficos
plt.style.use('default')
sns.set_palette("deep")

# Colores fijos para los resultados
palette = {
    "Aprobado": "#2ecc71",  # verde
    "Reprobado": "#e74c3c",  # rojo
    "Promovido": "#3498db",  # azul
    "Ausente": "#95a5a6"    # gris
}

# Procesar los datos para el análisis
print("Procesando datos...")

# Calcular conteos por materia, año y resultado
df_counts = df_long.groupby(['Actividad_Cod', 'Actividad_Nombre', 'Año_nivel', 'Año', 'Resultado']).size().reset_index(name='Cantidad')

# Calcular totales por materia y año
df_totales = df_long.groupby(['Actividad_Cod', 'Año']).size().reset_index(name='Total')

# Unir los totales al dataset de conteos
df_analysis = df_counts.merge(df_totales, on=['Actividad_Cod', 'Año'])

# Calcular porcentajes
df_analysis['Porcentaje'] = (df_analysis['Cantidad'] / df_analysis['Total']) * 100

# Obtener lista única de materias con su información completa
materias_info = df_analysis[['Actividad_Cod', 'Actividad_Nombre', 'Año_nivel']].drop_duplicates()

print(f"Total de materias a analizar: {len(materias_info)}")

# Generar gráficos por materia
for _, materia in materias_info.iterrows():
    cod = materia['Actividad_Cod']
    nombre = materia['Actividad_Nombre']
    año_nivel = materia['Año_nivel']
    
    # Filtrar datos para esta materia
    df_mat = df_analysis[df_analysis['Actividad_Cod'] == cod]
    
    # Crear figura con dos ejes Y
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    # === Eje Y1: Porcentajes ===
    sns.lineplot(
        data=df_mat,
        x="Año", 
        y="Porcentaje", 
        hue="Resultado", 
        marker="o",
        markersize=8,
        linewidth=2.5,
        palette=palette, 
        ax=ax1
    )
    
    ax1.set_ylabel("Porcentaje de estudiantes (%)", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Año Académico", fontsize=12, fontweight='bold')
    ax1.set_ylim(0, 110)
    ax1.grid(True, alpha=0.3)
    
    # Ajustar ticks del eje X según los años disponibles
    años_disponibles = sorted(df_mat['Año'].unique())
    ax1.set_xticks(años_disponibles)
    ax1.tick_params(axis='both', which='major', labelsize=10)
    
    # === Eje Y2: Totales ===
    ax2 = ax1.twinx()
    
    # Obtener datos únicos de totales por año
    totales_unicos = df_mat.drop_duplicates(['Año', 'Total'])
    
    sns.lineplot(
        data=totales_unicos,
        x="Año", 
        y="Total", 
        color="black", 
        marker="s", 
        markersize=8,
        linewidth=2.5,
        linestyle="--", 
        ax=ax2, 
        label="Total de estudiantes"
    )
    
    ax2.set_ylabel("Total de estudiantes", fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', which='major', labelsize=10)
    
    # Título con información completa
    titulo = f"Evolución del Rendimiento - Año {año_nivel} - {cod}\n{nombre}"
    plt.title(titulo, fontsize=14, fontweight='bold', pad=20)
    
    # Unir leyendas de ambos ejes
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    
    # Posicionar la leyenda fuera del gráfico
    ax1.legend(handles1 + handles2, labels1 + labels2, 
               loc='center left', 
               bbox_to_anchor=(1.15, 0.5),
               frameon=True,
               fancybox=True,
               shadow=True)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Crear nombre de archivo con la estructura solicitada
    # Limpiar nombre para archivo (remover caracteres especiales)
    nombre_limpio = "".join(c for c in nombre if c.isalnum() or c in (' ', '-', '_')).rstrip()
    nombre_limpio = nombre_limpio.replace(' ', '_')[:50]  # Limitar longitud
    
    nombre_archivo = f"rendimiento_A{año_nivel}_{cod}_{nombre_limpio}.png"
    
    # Guardar gráfico con alta calidad
    plt.savefig(nombre_archivo, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"Gráfico guardado: {nombre_archivo}")
    
    plt.close()

# %%


# Enfoque correcto: Agrupar por año académico y calcular totales una vez
print("Calculando resultados por año académico...")

# Agrupar por año académico y resultado para obtener los conteos
df_conteos_por_año = df_long.groupby(['Año', 'Resultado']).size().reset_index(name='Cantidad')

# Calcular el total único por año académico (estudiantes únicos por año)
total_por_año = df_long.groupby('Año')['Alumno_Cod'].count().reset_index(name='Total_Estudiantes')

# Unir los totales
df_resultados_año = df_conteos_por_año.merge(total_por_año, on='Año')

# Calcular porcentajes
df_resultados_año['Porcentaje'] = (df_resultados_año['Cantidad'] / df_resultados_año['Total_Estudiantes']) * 100

print("Resultados por año académico:")
print(df_resultados_año.head(20))

# Verificar que los porcentajes sumen 100% por año
print("\nVerificación - Suma de porcentajes por año:")
for año, group in df_resultados_año.groupby('Año'):
    suma_porcentajes = group['Porcentaje'].sum()
    print(f"Año {año}: {suma_porcentajes:.2f}%")

# Gráfico de resultados por año académico
fig, ax = plt.subplots(figsize=(14, 8))

# Pivotear para tener años como índice y resultados como columnas
df_pivot = df_resultados_año.pivot(index='Año', columns='Resultado', values='Porcentaje').fillna(0)

# Ordenar resultados consistentemente
orden_resultados = ['Aprobado', 'Promovido', 'Reprobado', 'Ausente']
for resultado in orden_resultados:
    if resultado not in df_pivot.columns:
        df_pivot[resultado] = 0

df_pivot = df_pivot[orden_resultados]

# Gráfico de barras apiladas
df_pivot.plot(kind='bar', stacked=True, ax=ax, 
              color=[palette[r] for r in orden_resultados],
              edgecolor='white', linewidth=0.5)

ax.set_title('Distribución de Resultados por Año Académico\n(Todos los años/niveles combinados)', 
            fontsize=16, fontweight='bold', pad=20)
ax.set_ylabel('Porcentaje de Estudiantes (%)')
ax.set_xlabel('Año Académico')
# ax.set_ylim(0, 100)
ax.legend(title='Resultado', bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True, alpha=0.3, axis='y')

# Agregar valores en las barras
for i, (año, row) in enumerate(df_pivot.iterrows()):
    cumulative = 0
    for resultado in orden_resultados:
        value = row[resultado]
        if value > 3:  # Solo mostrar valores significativos
            ax.text(i, cumulative + value/2, f'{value:.1f}%', 
                   ha='center', va='center', fontweight='bold', fontsize=9)
        cumulative += value

plt.tight_layout()
plt.savefig("resultados_generales_por_año.png", dpi=150, bbox_inches='tight')
plt.show()

# Ahora, si queremos análisis por año/nivel pero con totales correctos
print("\nCalculando resultados por año/nivel con totales correctos...")

# Para cada año/nivel y año académico, calcular estudiantes únicos
estudiantes_por_nivel_año = df_long.groupby(['Año_nivel', 'Año'])['Alumno_Cod'].count().reset_index(name='Total_Estudiantes')

# Conteos por año/nivel, año académico y resultado
conteos_por_nivel_año = df_long.groupby(['Año_nivel', 'Año', 'Resultado']).size().reset_index(name='Cantidad')

# Unir totales
df_nivel_año_correcto = conteos_por_nivel_año.merge(estudiantes_por_nivel_año, on=['Año_nivel', 'Año'])

# Calcular porcentajes
df_nivel_año_correcto['Porcentaje'] = (df_nivel_año_correcto['Cantidad'] / df_nivel_año_correcto['Total_Estudiantes']) * 100

print("Resultados por año/nivel (corregido):")
print(df_nivel_año_correcto.head(20))

# Verificar sumas por año/nivel y año académico
print("\nVerificación - Suma de porcentajes por año/nivel:")
for (año_nivel, año), group in df_nivel_año_correcto.groupby(['Año_nivel', 'Año']):
    suma_porcentajes = group['Porcentaje'].sum()
    print(f"Año {año_nivel}, {año}: {suma_porcentajes:.2f}%")

# Gráficos por año/nivel con datos corregidos
for año_nivel in sorted(df_nivel_año_correcto['Año_nivel'].unique()):
    df_nivel = df_nivel_año_correcto[df_nivel_año_correcto['Año_nivel'] == año_nivel]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Pivotear datos
    df_pivot_nivel = df_nivel.pivot(index='Año', columns='Resultado', values='Porcentaje').fillna(0)
    
    # Ordenar resultados
    for resultado in orden_resultados:
        if resultado not in df_pivot_nivel.columns:
            df_pivot_nivel[resultado] = 0
    
    df_pivot_nivel = df_pivot_nivel[orden_resultados]
    
    # Gráfico de barras apiladas
    df_pivot_nivel.plot(kind='bar', stacked=True, ax=ax, 
                       color=[palette[r] for r in orden_resultados],
                       edgecolor='white', linewidth=0.5)
    
    ax.set_title(f'Distribución de Resultados - Año {año_nivel} de Carrera\n(Con totales correctos - suma ~100%)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Porcentaje de Estudiantes (%)')
    ax.set_xlabel('Año Académico')
    # ax.set_ylim(0, 100)
    ax.legend(title='Resultado', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Agregar valores
    for i, (año, row) in enumerate(df_pivot_nivel.iterrows()):
        cumulative = 0
        for resultado in orden_resultados:
            value = row[resultado]
            if value > 3:
                ax.text(i, cumulative + value/2, f'{value:.1f}%', 
                       ha='center', va='center', fontweight='bold', fontsize=8)
            cumulative += value
    
    plt.tight_layout()
    plt.savefig(f"resultados_año_{año_nivel}_corregido.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Gráfico corregido guardado: resultados_año_{año_nivel}_corregido.png")

# Análisis adicional: Evolución temporal por resultado
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
axes = axes.flatten()

for i, resultado in enumerate(orden_resultados):
    df_resultado = df_resultados_año[df_resultados_año['Resultado'] == resultado]
    
    axes[i].plot(df_resultado['Año'], df_resultado['Porcentaje'], 
                marker='o', linewidth=2, markersize=8, 
                color=palette[resultado])
    
    axes[i].set_title(f'Evolución de {resultado}', fontweight='bold')
    axes[i].set_xlabel('Año Académico')
    axes[i].set_ylabel('Porcentaje (%)')
    # axes[i].set_ylim(0, 100)
    axes[i].grid(True, alpha=0.3)
    
    # Agregar valores en los puntos
    for _, row in df_resultado.iterrows():
        axes[i].text(row['Año'], row['Porcentaje'] + 2, f'{row["Porcentaje"]:.1f}%', 
                    ha='center', va='bottom', fontweight='bold')

plt.suptitle('Evolución Temporal de Cada Tipo de Resultado\n(Todos los años/niveles combinados)', 
             fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('evolucion_resultados_por_tipo.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n¡Análisis completado con éxito!")
print("Ahora los porcentajes suman aproximadamente 100% para cada agrupación.")
print("Archivos generados:")
print("- resultados_generales_por_año.png")
print("- resultados_año_X_corregido.png (para cada año/nivel)")
print("- evolucion_resultados_por_tipo.png")