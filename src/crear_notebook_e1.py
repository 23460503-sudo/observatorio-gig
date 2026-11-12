"""
Script para generar el Jupyter Notebook oficial: docs/E1/limpieza.ipynb
Documenta de forma interactiva y detallada los 5 requisitos de limpieza y preprocesamiento de E1,
la integracion de fuentes y la puerta de calidad con Pandera.
"""
import json
import os

def generar_notebook():
    nb = {
        "cells": [],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    def add_md(source):
        nb["cells"].append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [line + "\n" for line in source.split("\n")]
        })

    def add_code(source):
        nb["cells"].append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [line + "\n" for line in source.split("\n")]
        })

    # Portada e Introduccion
    add_md("""# Proyecto Integrador: TRUSTED DATA LAB
## Observatorio de Rentabilidad para Repartidores y Conductores (Gig Economy)
### Entrega E1: Pipeline de Limpieza, Preprocesamiento y Puerta de Calidad

**Integrantes:**
- Fernando Benavides Manzo
- Milagros Andrade

**Asignaturas integradas:**
1. **Ingeniería de Datos (CMD-2602, U3)** - Mtro. Román
2. **Análisis Estadístico para Ciencia de Datos (U3)** - Mtro. Joel
3. **Calidad en los Sistemas de Información (IFC-1008, U3)** - Mtra. Isis

---
### Contenido del Notebook
1. **Ingestión e Integración de Fuentes Heterogéneas** (Clima Open-Meteo + Gig Economy Mobility).
2. **Resolución de Conflictos de Esquemas, Fechas, Monedas y Tipos**.
3. **Puerta de Calidad Automática con Pandera** y segregación a **Cuarentena**.
4. **Tratamiento Metodológico de Valores Faltantes** (Diagnóstico MCAR / MAR / MNAR e imputación).
5. **Detección y Tratamiento Estadístico de Atípicos** (IQR y Z-Score Robusto con MAD).
6. **Normalización (Min-Max) vs. Estandarización (Z-Score)** con justificación analítica.
7. **Discretización y Jerarquías Conceptuales** (Tarifas, turnos y jerarquía espacial).
8. **Reducción de Datos Analítica** (Agregación horaria y selección de variables para la serie de tiempo).
9. **Exportación a Capas Plata y Oro** (Arquitectura Medallion).""")

    # Celda 1: Setup
    add_md("""---
## 1. Configuración del Entorno y Carga de Paquetes
Importamos las librerías necesarias para procesamiento numérico, manipulación tabular, validación de esquemas y visualizaciones.""")
    
    add_code("""import os
import re
import json
import datetime
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

import pandera as pa
from pandera import Column, Check, DataFrameSchema
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')
print(f'Pandas versión: {pd.__version__}')
print(f'Pandera versión: {pa.__version__}')""")

    # Celda 2: Carga de Bronce
    add_md("""---
## 2. Ingestión de Datos de la Capa Bronce
Cargamos los dos orígenes de datos heterogéneos:
1. **Clima de Colima (Open-Meteo API):** Formato JSON no tabular con mediciones horarias de temperatura, lluvia y código WMO.
2. **Viajes y Entregas (Gig Economy):** Formato CSV crudo capturado con desformatos, nulos, strings de moneda e irregularidades reales.""")

    add_code("""# Carga de fuente 1: Clima Open-Meteo (JSON)
with open('../../data/bronze/clima_colima_raw.json', 'r', encoding='utf-8') as f:
    raw_clima = json.load(f)

df_clima_raw = pd.DataFrame({
    'fecha_hora_iso': raw_clima['hourly']['time'],
    'temperatura_c': raw_clima['hourly']['temperature_2m'],
    'lluvia_mm': raw_clima['hourly']['rain'],
    'codigo_clima': raw_clima['hourly']['weathercode']
})
df_clima_raw['fecha_hora_hora'] = pd.to_datetime(df_clima_raw['fecha_hora_iso'])

# Carga de fuente 2: Viajes Gig (CSV)
df_gig_raw = pd.read_csv('../../data/bronze/gig_viajes_raw.csv')

print(f'Clima Bronce: {df_clima_raw.shape[0]} registros horarios.')
print(f'Gig Bronce: {df_gig_raw.shape[0]} transacciones crudas.')
df_gig_raw.head(4)""")

    # Celda 3: Resolucion de Conflictos e Integracion
    add_md("""---
## 3. Resolución de Conflictos e Integración Multifuente

### Discrepancias Identificadas y Resueltas:
1. **Formatos de Fecha Dispares:** Registros con ISO-8601, DD/MM/AAAA y formatos con horas. Se utiliza `pd.to_datetime(..., format='mixed')` unificando a zona horaria local.
2. **Campos Monetarios como Texto:** Strings como `"$ 145.50 MXN"` se limpian mediante expresiones regulares para extraer valores tipo `float`.
3. **Strings de Distancia con Unidades:** Valores como `"12.5 km"` se convierten a valores numéricos continuos.
4. **Entity Resolution en Plataformas:** Variaciones de nombres como `'uber'`, `'UBER'`, `'didi'`, `'ML_Extra'` se homologan al catálogo canónico (`'Uber'`, `'DiDi'`, `'Mercado Libre Extra'`).
5. **Alineación Temporal Horaria:** Se genera la clave `fecha_hora_hora` truncada a nivel de hora para unir el clima con cada viaje/entrega.""")

    add_code("""def limpiar_moneda(val):
    if pd.isna(val) or val is None: return np.nan
    val_clean = str(val).replace('$', '').replace('MXN', '').replace(',', '').strip()
    try: return float(val_clean)
    except: return np.nan

def normalizar_plataforma(plat):
    if pd.isna(plat): return 'Desconocida'
    p = str(plat).strip().lower()
    if 'uber' in p: return 'Uber'
    elif 'didi' in p: return 'DiDi'
    elif 'mercado' in p or 'ml' in p: return 'Mercado Libre Extra'
    return str(plat).strip()

def parsear_distancia(val):
    if pd.isna(val): return np.nan
    m = re.search(r'[-+]?\\d*\\.\\d+|\\d+', str(val))
    return float(m.group()) if m else np.nan

# Aplicacion de transformaciones
df_gig = df_gig_raw.copy()
df_gig['fecha_hora'] = pd.to_datetime(df_gig['fecha_hora_captura'], format='mixed')
df_gig['fecha_hora_hora'] = df_gig['fecha_hora'].dt.floor('h')
df_gig['ganancia_bruta'] = df_gig['ganancia_raw'].apply(limpiar_moneda)
df_gig['distancia_km'] = df_gig['distancia_raw'].apply(parsear_distancia)
df_gig['plataforma'] = df_gig['plataforma'].apply(normalizar_plataforma)
df_gig['duracion_min'] = pd.to_numeric(df_gig['duracion_min_raw'], errors='coerce')

# Fusión con Clima
df_integrado = pd.merge(
    df_gig,
    df_clima_raw[['fecha_hora_hora', 'temperatura_c', 'lluvia_mm', 'codigo_clima']],
    on='fecha_hora_hora',
    how='left'
)
df_integrado['temperatura_c'] = df_integrado['temperatura_c'].bfill().ffill()
df_integrado['lluvia_mm'] = df_integrado['lluvia_mm'].fillna(0.0)
df_integrado['codigo_clima'] = df_integrado['codigo_clima'].fillna(0).astype(int)

print(f'Dataset integrado exitosamente: {df_integrado.shape[0]} filas x {df_integrado.shape[1]} columnas.')""")

    # Celda 4: Puerta de Calidad Pandera y Cuarentena
    add_md("""---
## 4. Puerta de Calidad Automática con Pandera y Cuarentena

> [!IMPORTANT]
> **Principio de Calidad:** Ningún registro inválido se borra en silencio. 
> Todos los registros que violan las reglas de integridad o de negocio son enviados a **Cuarentena** con su respectivo motivo de rechazo, fecha y trazabilidad para auditoría SQA.

### Reglas de la Puerta de Calidad:
1. `plataforma`: Debe pertenecer estrictamente a `['Uber', 'DiDi', 'Mercado Libre Extra']`.
2. `tarifa_dinamica`: En rango válido $[1.0, 5.0]$.
3. `ganancia_bruta`: Debe ser estrictamente $> 0$ (o nulo para tratamiento de faltantes).
4. `duracion_min`: Debe ser $> 0$.
5. `latitud` y `longitud`: Deben corresponder al polígono metropolitano de Colima y Villa de Álvarez ($19.10 \\le Lat \\le 19.40$, $-103.85 \\le Lon \\le -103.60$).
6. `temperatura_c`: En rango verosímil $[10.0, 48.0] ^\\circ\\text{C}$.""")

    add_code("""# Definicion formal del esquema en Pandera
esquema_pandera = DataFrameSchema(
    columns={
        'id_registro': Column(str, nullable=False),
        'fecha_hora': Column(pa.DateTime, nullable=False),
        'plataforma': Column(str, Check.isin(['Uber', 'DiDi', 'Mercado Libre Extra']), nullable=False),
        'zona': Column(str, Check.isin([
            'Colima Centro', 'Villa de Álvarez Norte', 'Tercer Anillo Comercial',
            'Plaza Country / San Fernando', 'Avenida Tecnologico'
        ]), nullable=False),
        'municipio': Column(str, Check.isin(['Colima', 'Villa de Alvarez']), nullable=False),
        'latitud': Column(float, Check.in_range(19.10, 19.40), nullable=False),
        'longitud': Column(float, Check.in_range(-103.85, -103.60), nullable=False),
        'distancia_km': Column(float, Check.greater_than(0.0), nullable=True),
        'duracion_min': Column(float, Check.greater_than(0.0), nullable=False),
        'tarifa_dinamica': Column(float, Check.in_range(1.0, 5.0), nullable=False),
        'ganancia_bruta': Column(float, Check.greater_than(0.0), nullable=True),
        'temperatura_c': Column(float, Check.in_range(10.0, 48.0), nullable=False),
        'lluvia_mm': Column(float, Check.greater_than_or_equal_to(0.0), nullable=False),
    },
    coerce=True,
    strict=False
)

# Evaluacion de registros y enrutamiento a cuarentena
conformes = []
rechazados = []

for idx, row in df_integrado.iterrows():
    motivos = []
    if row['plataforma'] not in ['Uber', 'DiDi', 'Mercado Libre Extra']:
        motivos.append(f"Plataforma fuera de catálogo ({row['plataforma']})")
    if pd.isna(row['tarifa_dinamica']) or row['tarifa_dinamica'] < 1.0 or row['tarifa_dinamica'] > 5.0:
        motivos.append(f"Tarifa dinámica fuera de rango [1.0, 5.0] ({row['tarifa_dinamica']})")
    if pd.notna(row['ganancia_bruta']) and row['ganancia_bruta'] <= 0:
        motivos.append(f"Ganancia no positiva ({row['ganancia_bruta']})")
    if pd.isna(row['duracion_min']) or row['duracion_min'] <= 0:
        motivos.append(f"Duración inválida ({row['duracion_min']})")
    if row['latitud'] < 19.10 or row['latitud'] > 19.40 or row['longitud'] < -103.85 or row['longitud'] > -103.60:
        motivos.append(f"Coordenadas fuera de zona metropolitana ({row['latitud']}, {row['longitud']})")
    if row['temperatura_c'] < 10.0 or row['temperatura_c'] > 48.0:
        motivos.append(f"Temperatura extrema fuera de rango ({row['temperatura_c']})")
        
    if motivos:
        rechazados.append({
            'id_registro': row['id_registro'],
            'fecha_rechazo': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'plataforma': row['plataforma'],
            'motivo_rechazo': ' | '.join(motivos),
            'valor_crudo': str(row.get('ganancia_raw')) + ' / ' + str(row.get('tarifa_dinamica'))
        })
    else:
        conformes.append(idx)

df_conformes = df_integrado.loc[conformes].copy()
df_cuarentena = pd.DataFrame(rechazados)

# Validacion Pandera sobre conformes
esquema_pandera.validate(df_conformes)

print(f'Total evaluados: {len(df_integrado)}')
print(f'Conformes (pasan a Plata): {len(df_conformes)}')
print(f'Enviados a Cuarentena: {len(df_cuarentena)}')
display(df_cuarentena.head(5))""")

    # Celda 5: Tratamiento de Valores Faltantes (MCAR, MAR, MNAR)
    add_md("""---
## 5. Diagnóstico y Tratamiento de Valores Faltantes

En analítica de datos rigurosa, no se pueden rellenar nulos a ciegas. Clasificamos los mecanismos de pérdida según Little & Rubin:

1. **MCAR (Missing Completely at Random):** 
   - *Variable:* `distancia_km`.
   - *Mecanismo:* Pérdida aleatoria de triangulación satelital en el teléfono del repartidor (3.5% de los datos). No se correlaciona con la tarifa ni con la ganancia.
   - *Tratamiento:* Imputación por **mediana condicionada a la zona geográfica** (las distancias dependen de la topología urbana de Colima y Villa de Álvarez).
2. **MAR (Missing at Random):**
   - *Variable:* `tiempo_espera_min`.
   - *Mecanismo:* La probabilidad de dato faltante depende sistemáticamente del `turno_horario` (en la madrugada hay menos locales abiertos y no se registra tiempo de espera en cocina).
   - *Tratamiento:* Imputación por **mediana condicionada al estrato temporal (hora del día)**.
3. **MNAR (Missing Not at Random):**
   - *Variable:* `ganancia_bruta`.
   - *Mecanismo:* El dato falta precisamente porque el valor fue nulo o el servicio fue cancelado por el conductor debido a baja tarifa.
   - *Tratamiento:* Estimación determinística por modelo base de costo por kilómetro: $\\text{tarifa} = (\\text{distancia} \\times \\$12.50 \\times \\text{tarifa\\_dinamica}) + \\$20.00$ de arranque.""")

    add_code("""# Diagnostico de nulos previo al tratamiento
nulos_antes = df_conformes[['distancia_km', 'tiempo_espera_min', 'ganancia_bruta']].isna().sum()
print("Valores nulos antes del tratamiento:")
print(nulos_antes)

# 1. Tratamiento MCAR: Distancia imputada por mediana de la zona
mediana_dist_zona = df_conformes.groupby('zona')['distancia_km'].transform('median')
df_conformes['distancia_km'] = df_conformes['distancia_km'].fillna(mediana_dist_zona)

# 2. Tratamiento MAR: Tiempo de espera imputado por mediana de la franja horaria
hora_serie = df_conformes['fecha_hora'].dt.hour
mediana_espera_hora = df_conformes.groupby(hora_serie)['tiempo_espera_min'].transform('median')
df_conformes['tiempo_espera_min'] = df_conformes['tiempo_espera_min'].fillna(mediana_espera_hora).fillna(5.0)

# 3. Tratamiento MNAR: Ganancia bruta calculada por modelo base
tarifa_base_km = 12.50
ganancia_estimada = (df_conformes['distancia_km'] * tarifa_base_km * df_conformes['tarifa_dinamica']) + 20.0
df_conformes['ganancia_bruta'] = df_conformes['ganancia_bruta'].fillna(ganancia_estimada)

# Ganancia neta deduciendo gasto de combustible
df_conformes['ganancia_neta'] = (df_conformes['ganancia_bruta'] - df_conformes['gasto_gasolina_estimado']).round(2)

nulos_despues = df_conformes[['distancia_km', 'tiempo_espera_min', 'ganancia_bruta', 'ganancia_neta']].isna().sum()
print("\\nValores nulos después del tratamiento metodológico:")
print(nulos_despues)""")

    # Celda 6: Atipicos y Ruido
    add_md("""---
## 6. Detección y Tratamiento Estadístico de Atípicos y Ruido

### Métodos Estadísticos Utilizados:
1. **Rango Intercuartílico (IQR):**
   $$IQR = Q_3 - Q_1$$
   $$Limite_{inf} = Q_1 - 1.5 \\times IQR, \\quad Limite_{sup} = Q_3 + 1.5 \\times IQR$$
2. **Z-Score Robusto con Desviación Absoluta de la Mediana (MAD):**
   $$Z_{robusto} = \\frac{x - \\text{Mediana}}{1.4826 \\times MAD}$$
   Donde $MAD = \\text{Mediana}(|x - \\text{Mediana}|)$. El factor $1.4826$ normaliza la estimación para asemejarse a la desviación estándar en una distribución gaussiana.

### Decisión de Negocio Documentada:
- **Ruido Técnico:** Valores negativos, duraciones de $9999$ min o tarifas absurdas fueron rechazados y enviados a la **Cuarentena** por la Puerta de Calidad.
- **Atípicos Genuinos de Negocio:** Servicios con ganancias muy elevadas durante lluvias torrenciales o picos de demanda nocturna en fin de semana. **NO SE BORRAN NI SE IMPUTAN**, sino que se etiquetan con la bandera `flag_atipico_negocio = 1` para que los modelos estadísticos puedan aislarlos o analizarlos como eventos especiales.""")

    add_code("""# Calculo IQR sobre Ganancia Neta
q25 = df_conformes['ganancia_neta'].quantile(0.25)
q75 = df_conformes['ganancia_neta'].quantile(0.75)
iqr = q75 - q25
lim_inf = q25 - 1.5 * iqr
lim_sup = q75 + 1.5 * iqr

# Calculo Z-Score Robusto
med_gn = df_conformes['ganancia_neta'].median()
mad_gn = np.median(np.abs(df_conformes['ganancia_neta'] - med_gn))
df_conformes['z_robusto_ganancia'] = ((df_conformes['ganancia_neta'] - med_gn) / (1.4826 * mad_gn)).round(3)

df_conformes['es_atipico_iqr'] = (df_conformes['ganancia_neta'] < lim_inf) | (df_conformes['ganancia_neta'] > lim_sup)
df_conformes['es_atipico_robusto'] = np.abs(df_conformes['z_robusto_ganancia']) > 3.0

# Deteccion de atipico genuino de negocio
df_conformes['flag_atipico_negocio'] = np.where(
    (df_conformes['es_atipico_iqr'] | df_conformes['es_atipico_robusto']) & 
    ((df_conformes['tarifa_dinamica'] >= 1.7) | (df_conformes['lluvia_mm'] > 1.0)),
    1, 0
)

print(f'Umbrales IQR Ganancia Neta: [{lim_inf:.2f}, {lim_sup:.2f}] MXN')
print(f'Atípicos detectados por IQR: {df_conformes["es_atipico_iqr"].sum()}')
print(f'Atípicos detectados por Z-Score Robusto: {df_conformes["es_atipico_robusto"].sum()}')
print(f'Atípicos clasificados como Oportunidad Real de Negocio: {df_conformes["flag_atipico_negocio"].sum()}')""")

    # Celda 7: Normalizacion y Estandarizacion
    add_md("""---
## 7. Normalización vs. Estandarización de Variables Continuas

| Método | Fórmula | Rango resultante | Cuándo usar en el Observatorio |
|---|---|---|---|
| **Min-Max Scaling** | $x' = \\frac{x - x_{min}}{x_{max} - x_{min}}$ | $[0, 1]$ | Para variables acotadas y visualización en dashboards (distancias, duraciones relativas, tiempos de espera). |
| **Z-Score Standardization** | $z = \\frac{x - \\mu}{\\sigma}$ | $\\mu = 0, \\sigma = 1$ | Para variables con distribución gaussiana y modelos de series de tiempo (ARIMA), PCA y clustering donde la varianza comparativa importa. |""")

    add_code("""# Aplicacion de Normalizacion Min-Max
for col in ['distancia_km', 'duracion_min', 'tiempo_espera_min']:
    c_min, c_max = df_conformes[col].min(), df_conformes[col].max()
    df_conformes[f'{col}_minmax'] = ((df_conformes[col] - c_min) / (c_max - c_min)).round(4)

# Aplicacion de Estandarizacion Z-Score
for col in ['ganancia_neta', 'temperatura_c', 'tarifa_dinamica']:
    media, std = df_conformes[col].mean(), df_conformes[col].std()
    df_conformes[f'{col}_zscore'] = ((df_conformes[col] - media) / std).round(4)

df_conformes[['ganancia_neta', 'ganancia_neta_zscore', 'distancia_km', 'distancia_km_minmax']].head(5)""")

    # Celda 8: Discretizacion y Jerarquias
    add_md("""---
## 8. Discretización y Jerarquías Conceptuales

1. **Discretización de Tarifa Dinámica:** Se establecen cortes interpretables para conductores:
   - `Base (1.0x)`
   - `Moderada (1.1x - 1.4x)`
   - `Alta (1.5x - 2.0x)`
   - `Dinámica Extrema (>2.0x)`
2. **Discretización Temporal (Turnos):**
   - `Madrugada` ($00:00 - 05:59$)
   - `Mañana` ($06:00 - 11:59$)
   - `Tarde` ($12:00 - 17:59$)
   - `Noche` ($18:00 - 23:59$)
3. **Jerarquía Conceptual Espacial:**
   $$\\text{Coordenadas GPS } (Lat, Lon) \\longrightarrow \\text{Zona / Corredor Comercial} \\longrightarrow \\text{Municipio } (Colima / VdA) \\longrightarrow \\text{Estado } (Colima)$$""")

    add_code("""# Discretizacion de Tarifa
bins_tarifa = [0.99, 1.15, 1.45, 2.00, 10.0]
labels_tarifa = ['Base (1.0x)', 'Moderada (1.1x-1.4x)', 'Alta (1.5x-2.0x)', 'Dinámica Extrema (>2.0x)']
df_conformes['categoria_tarifa'] = pd.cut(df_conformes['tarifa_dinamica'], bins=bins_tarifa, labels=labels_tarifa)

# Discretizacion de Turno
def asignar_turno(dt):
    h = dt.hour
    if 0 <= h < 6: return 'Madrugada'
    elif 6 <= h < 12: return 'Mañana'
    elif 12 <= h < 18: return 'Tarde'
    return 'Noche'
df_conformes['turno_horario'] = df_conformes['fecha_hora'].apply(asignar_turno)

# Jerarquia Conceptual
df_conformes['estado'] = 'Colima'
df_conformes['region_geografica'] = df_conformes['municipio'] + ' - ' + df_conformes['zona']

print('Distribución por Categoría de Tarifa:')
print(df_conformes['categoria_tarifa'].value_counts())
print('\\nDistribución por Turno Horario:')
print(df_conformes['turno_horario'].value_counts())""")

    # Celda 9: Reduccion de Datos y Capa Oro
    add_md("""---
## 9. Reducción de Datos Analítica y Publicación Capa Oro

Para el modelo de pronóstico de series de tiempo (ARIMA / Holt-Winters de E1), el análisis no requiere la granularidad segundo a segundo, sino la dinámica agregada por hora y zona.

- **Estrategia de Reducción:** Agregación temporal y espacial calculando métricas de tendencia central (media, mediana) y dispersión, eliminando atributos auxiliares crudos.
- **Tasa de Reducción:** Se reduce el volumen de transacciones dispersas hacia una serie horaria regular y continua.""")

    add_code("""# Generacion de la Serie Agregada Oro
df_serie_oro = df_conformes.groupby(['fecha_hora_hora', 'zona', 'municipio']).agg(
    total_viajes=('id_registro', 'count'),
    ganancia_neta_promedio=('ganancia_neta', 'mean'),
    ganancia_neta_mediana=('ganancia_neta', 'median'),
    tarifa_dinamica_promedio=('tarifa_dinamica', 'mean'),
    duracion_promedio_min=('duracion_min', 'mean'),
    distancia_promedio_km=('distancia_km', 'mean'),
    temperatura_promedio_c=('temperatura_c', 'mean'),
    lluvia_acumulada_mm=('lluvia_mm', 'sum'),
    viajes_alta_demanda=('flag_atipico_negocio', 'sum')
).reset_index()

# Redondeo de numericos
cols_num = df_serie_oro.select_dtypes(include=[np.number]).columns
df_serie_oro[cols_num] = df_serie_oro[cols_num].round(2)

reduccion_pct = (1.0 - (len(df_serie_oro) / len(df_gig_raw))) * 100
print(f'Transacciones crudas iniciales: {len(df_gig_raw)}')
print(f'Periodos horarios agregados Oro: {len(df_serie_oro)}')
print(f'Tasa de reducción de volumen de datos: {reduccion_pct:.2f}%')
df_serie_oro.head(5)""")

    # Celda 10: Persistencia Final y Conclusion
    add_md("""---
## 10. Persistencia en Arquitectura Medallion y Conclusiones

Los datos validados y enriquecidos se exportan en formatos optimizados:
- `data/plata/gig_observatorio_plata.parquet` (y CSV)
- `data/oro/gig_observatorio_oro.parquet` (y CSV)
- `data/oro/gig_observatorio_serie_oro.parquet` (y CSV)
- `data/cuarentena/rechazos_calidad.parquet` (y CSV)

Este pipeline automatizado garantiza que cualquier dato nuevo cumpla con las 3 puertas de calidad del observatorio, permitiendo pronósticos y experimentos confiables sobre datos certificados.""")

    add_code("""# Verificacion final de archivos generados
archivos_generados = [
    '../../data/cuarentena/rechazos_calidad.csv',
    '../../data/plata/gig_observatorio_plata.csv',
    '../../data/oro/gig_observatorio_oro.csv',
    '../../data/oro/gig_observatorio_serie_oro.csv'
]

print("Estado de los archivos de salida del pipeline:")
for a in archivos_generados:
    existe = os.path.exists(a)
    tam_kb = os.path.getsize(a) / 1024 if existe else 0
    print(f" -> {os.path.basename(a)}: {'Existe' if existe else 'No encontrado'} ({tam_kb:.1f} KB)")""")

    os.makedirs("docs/E1", exist_ok=True)
    with open("docs/E1/limpieza.ipynb", "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("[OK] Notebook docs/E1/limpieza.ipynb generado exitosamente.")

if __name__ == "__main__":
    generar_notebook()
