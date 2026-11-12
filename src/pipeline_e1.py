"""
Pipeline E1: Automatización de Capas Bronce -> Plata -> Oro
Observatorio de Rentabilidad para Repartidores y Conductores (Gig Economy Colima).
Implementa:
1. Integración de fuentes heterogéneas (Open-Meteo JSON + Gig Economy CSV).
2. Resolución de conflictos (tipos, unidades, fechas y entity resolution).
3. Puerta de Calidad Automática con Pandera y Cuarentena de registros inválidos.
4. Limpieza estadística: Tratamiento formal de nulos (MCAR/MAR/MNAR) y atípicos (IQR / Z-Score Robusto).
5. Preparación analítica para Capa Oro: Normalización (Min-Max), Estandarización (Z-Score),
   Discretización, Jerarquías conceptuales y Reducción de datos.
"""
import os
import re
import json
import datetime
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import pandera as pa
from pandera import Column, Check, DataFrameSchema

# ==============================================================================
# 1. ESQUEMA DE PUERTA DE CALIDAD (PANDERA)
# ==============================================================================
esquema_puerta_calidad = DataFrameSchema(
    columns={
        "id_registro": Column(str, nullable=False),
        "fecha_hora": Column(pa.DateTime, nullable=False),
        "plataforma": Column(str, Check.isin(["Uber", "DiDi", "Mercado Libre Extra"]), nullable=False),
        "zona": Column(str, Check.isin([
            "Colima Centro",
            "Villa de Álvarez Norte",
            "Tercer Anillo Comercial",
            "Plaza Country / San Fernando",
            "Avenida Tecnologico"
        ]), nullable=False),
        "municipio": Column(str, Check.isin(["Colima", "Villa de Alvarez"]), nullable=False),
        "latitud": Column(float, Check.in_range(19.10, 19.40), nullable=False),
        "longitud": Column(float, Check.in_range(-103.85, -103.60), nullable=False),
        "distancia_km": Column(float, Check.greater_than(0.0), nullable=True),  # Nulos se trataran en limpieza
        "duracion_min": Column(float, Check.greater_than(0.0), nullable=False),
        "tarifa_dinamica": Column(float, Check.in_range(1.0, 5.0), nullable=False),
        "ganancia_bruta": Column(float, Check.greater_than(0.0), nullable=True),  # Nulos se trataran en limpieza
        "gasto_gasolina_estimado": Column(float, Check.greater_than_or_equal_to(0.0), nullable=False),
        "tiempo_espera_min": Column(float, Check.greater_than_or_equal_to(0.0), nullable=True),
        "pedidos_entregados": Column(int, Check.in_range(1, 10), nullable=False),
        "temperatura_c": Column(float, Check.in_range(10.0, 48.0), nullable=False),
        "lluvia_mm": Column(float, Check.greater_than_or_equal_to(0.0), nullable=False),
        "codigo_clima": Column(int, nullable=False)
    },
    coerce=True,
    strict=False
)

# ==============================================================================
# 2. CARGA DE CAPA BRONCE Y RESOLUCIÓN DE CONFLICTOS
# ==============================================================================
def cargar_fuente_clima_bronce(ruta_json="data/bronze/clima_colima_raw.json") -> pd.DataFrame:
    """Extrae y estructura la serie temporal climatica de Open-Meteo."""
    if not os.path.exists(ruta_json):
        raise FileNotFoundError(f"No existe el archivo de clima crudo en {ruta_json}")
        
    with open(ruta_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    hourly = data["hourly"]
    df_clima = pd.DataFrame({
        "fecha_hora_iso": hourly["time"],
        "temperatura_c": hourly["temperature_2m"],
        "lluvia_mm": hourly["rain"],
        "codigo_clima": hourly["weathercode"]
    })
    
    # Conversion de fecha a datetime truncada a la hora
    df_clima["fecha_hora_hora"] = pd.to_datetime(df_clima["fecha_hora_iso"])
    return df_clima

def limpiar_texto_moneda(valor) -> float:
    """Resuelve conflictos de formato de moneda: $120.50 MXN -> 120.50"""
    if pd.isna(valor) or valor is None:
        return np.nan
    val_str = str(valor).replace("$", "").replace("MXN", "").replace(",", "").strip()
    try:
        return float(val_str)
    except ValueError:
        return np.nan

def normalizar_nombre_plataforma(plataforma) -> str:
    """Entity Resolution: Homologa nombres heterogeneos de plataformas."""
    if pd.isna(plataforma):
        return "Desconocida"
    p = str(plataforma).strip().lower()
    if "uber" in p:
        return "Uber"
    elif "didi" in p:
        return "DiDi"
    elif "mercado" in p or "ml" in p:
        return "Mercado Libre Extra"
    else:
        return str(plataforma).strip()

def cargar_y_preparar_bronce_gig(ruta_csv="data/bronze/gig_viajes_raw.csv") -> pd.DataFrame:
    """Carga viajes crudos y unifica tipos basicos antes de la puerta de calidad."""
    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(f"No existe el archivo de viajes crudos en {ruta_csv}")
        
    df = pd.read_csv(ruta_csv)
    
    # 1. Resolucion de formatos de fechas dispares (ISO YYYY-MM-DD vs DD/MM/YYYY)
    def parse_fecha_robusta(v):
        if pd.isna(v): return pd.NaT
        v_str = str(v).strip()
        if v_str[:4].isdigit():
            return pd.to_datetime(v_str)
        return pd.to_datetime(v_str, dayfirst=True)
        
    df["fecha_hora"] = df["fecha_hora_captura"].apply(parse_fecha_robusta)
    df["fecha_hora_hora"] = df["fecha_hora"].dt.floor("h")
    
    # 2. Resolucion de discrepancias en texto de moneda
    df["ganancia_bruta"] = df["ganancia_raw"].apply(limpiar_texto_moneda)
    
    # 3. Limpieza de texto de distancia ('12.5 km' -> 12.5)
    def parse_dist(v):
        if pd.isna(v): return np.nan
        m = re.search(r"[-+]?\d*\.\d+|\d+", str(v))
        return float(m.group()) if m else np.nan
    df["distancia_km"] = df["distancia_raw"].apply(parse_dist)
    
    # 4. Homologacion de plataformas
    df["plataforma"] = df["plataforma"].apply(normalizar_nombre_plataforma)
    
    # Renombrar duracion
    df["duracion_min"] = pd.to_numeric(df["duracion_min_raw"], errors="coerce")
    
    return df

# ==============================================================================
# 3. INTEGRACIÓN MULTIFUENTE (CLIMA + GIG ECONOMY)
# ==============================================================================
def integrar_fuentes(df_gig: pd.DataFrame, df_clima: pd.DataFrame) -> pd.DataFrame:
    """Combina los datos de viajes con las condiciones meteorologicas de la hora exacta."""
    df_merged = pd.merge(
        df_gig,
        df_clima[["fecha_hora_hora", "temperatura_c", "lluvia_mm", "codigo_clima"]],
        on="fecha_hora_hora",
        how="left"
    )
    
    # Imputacion de respaldo si el clima horario exacto no coincidio
    df_merged["temperatura_c"] = df_merged["temperatura_c"].bfill().ffill()
    df_merged["lluvia_mm"] = df_merged["lluvia_mm"].fillna(0.0)
    df_merged["codigo_clima"] = df_merged["codigo_clima"].fillna(0).astype(int)
    
    return df_merged

# ==============================================================================
# 4. PUERTA DE CALIDAD Y CUARENTENA
# ==============================================================================
def evaluar_puerta_calidad(df: pd.DataFrame):
    """
    Evalua cada fila contra las reglas de calidad y negocio.
    Segrega los registros invalidos hacia cuarentena con motivo documentado.
    """
    os.makedirs("data/cuarentena", exist_ok=True)
    
    conformes_idx = []
    rechazados = []
    
    for idx, row in df.iterrows():
        errores = []
        
        # Validacion 1: Plataforma permitida
        if row["plataforma"] not in ["Uber", "DiDi", "Mercado Libre Extra"]:
            errores.append(f"Plataforma no autorizada en catalogo ('{row['plataforma']}')")
            
        # Validacion 2: Rango de tarifa dinamica
        if pd.isna(row["tarifa_dinamica"]) or row["tarifa_dinamica"] < 1.0 or row["tarifa_dinamica"] > 5.0:
            errores.append(f"Tarifa dinamica fuera de rango [1.0, 5.0] (valor: {row['tarifa_dinamica']})")
            
        # Validacion 3: Ganancia no negativa
        if pd.notna(row["ganancia_bruta"]) and row["ganancia_bruta"] <= 0:
            errores.append(f"Ganancia neta debe ser estrictamente positiva (valor: {row['ganancia_bruta']})")
            
        # Validacion 4: Duracion valida
        if pd.isna(row["duracion_min"]) or row["duracion_min"] <= 0:
            errores.append(f"Duracion invalida (valor: {row['duracion_min']})")
            
        # Validacion 5: Rango geografico de Colima / Villa de Alvarez
        if row["latitud"] < 19.10 or row["latitud"] > 19.40 or row["longitud"] < -103.85 or row["longitud"] > -103.60:
            errores.append(f"Coordenadas fuera del area metropolitana Colima/VdA ({row['latitud']}, {row['longitud']})")
            
        # Validacion 6: Rango de temperatura logica
        if row["temperatura_c"] < 10.0 or row["temperatura_c"] > 48.0:
            errores.append(f"Temperatura extrema inverosimil ({row['temperatura_c']} C)")
            
        if errores:
            rechazados.append({
                "id_registro": row["id_registro"],
                "fecha_hora_captura": str(row["fecha_hora_captura"]),
                "fecha_rechazo": datetime.datetime.now().isoformat(),
                "plataforma": row["plataforma"],
                "columna_error": "Múltiple" if len(errores) > 1 else errores[0].split()[0],
                "motivo_rechazo": " | ".join(errores),
                "valor_invalido": str(row.get("ganancia_raw", "")) + " / " + str(row.get("tarifa_dinamica", ""))
            })
        else:
            conformes_idx.append(idx)
            
    df_conformes = df.loc[conformes_idx].copy()
    df_cuarentena = pd.DataFrame(rechazados)
    
    # Validacion formal con Pandera del subconjunto conforme
    esquema_puerta_calidad.validate(df_conformes)
    
    # Guardar cuarentena
    if not df_cuarentena.empty:
        df_cuarentena.to_parquet("data/cuarentena/rechazos_calidad.parquet", index=False)
        df_cuarentena.to_csv("data/cuarentena/rechazos_calidad.csv", index=False, encoding="utf-8")
        
    print(f"[PUERTA DE CALIDAD] Evaluados: {len(df)} | Conformes: {len(df_conformes)} | Cuarentena: {len(df_cuarentena)}")
    return df_conformes, df_cuarentena

# ==============================================================================
# 5. LIMPIEZA ESTADÍSTICA (FALTANTES Y ATÍPICOS) -> CAPA PLATA
# ==============================================================================
def ejecutar_limpieza_estadistica(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica tratamiento justificado de datos faltantes y deteccion/gestion de atipicos:
    - MCAR: Distancia -> Imputacion por mediana condicionada por zona.
    - MAR: Tiempo de espera -> Imputacion por mediana por franja horaria.
    - MNAR: Ganancia neta faltante -> Estimacion por modelo base de tarifa/km.
    - Atipicos: IQR y Z-Score Robusto (MAD).
    """
    df = df.copy()
    
    # --- A. TRATAMIENTO DE FALTANTES ---
    # 1. MCAR: distancia_km (perdida aleatoria de satelite)
    mediana_dist_zona = df.groupby("zona")["distancia_km"].transform("median")
    df["distancia_km"] = df["distancia_km"].fillna(mediana_dist_zona)
    
    # 2. MAR: tiempo_espera_min (condicionado a turnos nocturnos)
    df["hora"] = df["fecha_hora"].dt.hour
    mediana_espera_hora = df.groupby("hora")["tiempo_espera_min"].transform("median")
    df["tiempo_espera_min"] = df["tiempo_espera_min"].fillna(mediana_espera_hora).fillna(5.0)
    
    # 3. MNAR: ganancia_bruta faltante
    # Formula de tarifa base: (distancia * $12.50 * tarifa_dinamica) + $20 base
    estimacion_ganancia = (df["distancia_km"] * 12.50 * df["tarifa_dinamica"]) + 20.0
    df["ganancia_bruta"] = df["ganancia_bruta"].fillna(estimacion_ganancia)
    
    # Ganancia neta real (descontando gasto de combustible)
    df["ganancia_neta"] = (df["ganancia_bruta"] - df["gasto_gasolina_estimado"]).round(2)
    
    # --- B. DETECCIÓN Y TRATAMIENTO DE ATÍPICOS ---
    # Metodo IQR sobre ganancia_neta
    q25 = df["ganancia_neta"].quantile(0.25)
    q75 = df["ganancia_neta"].quantile(0.75)
    iqr = q75 - q25
    limite_inf_iqr = q25 - 1.5 * iqr
    limite_sup_iqr = q75 + 1.5 * iqr
    
    # Metodo Z-Score Robusto con Desviacion Absoluta de la Mediana (MAD)
    mediana_gn = df["ganancia_neta"].median()
    mad = np.median(np.abs(df["ganancia_neta"] - mediana_gn))
    if mad == 0: mad = 1.0
    df["z_score_robusto"] = ((df["ganancia_neta"] - mediana_gn) / (1.4826 * mad)).round(3)
    
    # Etiquetar atipicos legitimos de negocio vs anomalías
    # Si la tarifa dinamica es alta o hay lluvia fuerte, es un atipico genuino de negocio
    df["es_atipico_iqr"] = (df["ganancia_neta"] < limite_inf_iqr) | (df["ganancia_neta"] > limite_sup_iqr)
    df["es_atipico_robusto"] = np.abs(df["z_score_robusto"]) > 3.0
    
    df["flag_atipico_negocio"] = np.where(
        (df["es_atipico_iqr"] | df["es_atipico_robusto"]) & ((df["tarifa_dinamica"] >= 1.8) | (df["lluvia_mm"] > 2.0)),
        1, 0
    )
    
    return df

# ==============================================================================
# 6. TRANSFORMACIÓN Y REDUCCIÓN -> CAPA ORO
# ==============================================================================
def transformar_a_capa_oro(df_plata: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Genera la capa Oro:
    1. Normalizacion Min-Max y Estandarizacion Z-Score.
    2. Discretizacion de tarifas y turnos.
    3. Jerarquias conceptuales.
    4. Reduccion de datos analitica (agregacion horaria para series de tiempo).
    """
    df = df_plata.copy()
    
    # 1. Normalizacion Min-Max [0, 1]
    for col in ["distancia_km", "duracion_min", "tiempo_espera_min"]:
        c_min = df[col].min()
        c_max = df[col].max()
        df[f"{col}_minmax"] = ((df[col] - c_min) / (c_max - c_min + 1e-6)).round(4)
        
    # 2. Estandarizacion Z-Score (media=0, std=1)
    for col in ["ganancia_neta", "temperatura_c", "tarifa_dinamica"]:
        media = df[col].mean()
        std = df[col].std()
        df[f"{col}_zscore"] = ((df[col] - media) / (std + 1e-6)).round(4)
        
    # 3. Discretizacion de Variables
    # Rangos de Tarifa Dinamica
    bins_tarifa = [0.99, 1.15, 1.45, 2.00, 10.0]
    labels_tarifa = ["Base (1.0x)", "Moderada (1.1x-1.4x)", "Alta (1.5x-2.0x)", "Dinamica Extrema (>2.0x)"]
    df["categoria_tarifa"] = pd.cut(df["tarifa_dinamica"], bins=bins_tarifa, labels=labels_tarifa)
    
    # Turnos Horarios
    def clasificar_turno(hora):
        if 0 <= hora < 6: return "Madrugada"
        elif 6 <= hora < 12: return "Mañana"
        elif 12 <= hora < 18: return "Tarde"
        else: return "Noche"
    df["turno_horario"] = df["hora"].apply(clasificar_turno)
    
    # 4. Jerarquia Conceptual Geografica
    # Coordenadas -> Zona -> Municipio -> Estado
    df["estado"] = "Colima"
    df["region_geografica"] = df["municipio"] + " - " + df["zona"]
    
    # 5. Reduccion de Datos Analitica (Agregacion temporal horaria para la serie de tiempo E1)
    # Agrupamos por (fecha_hora_hora, zona, municipio)
    df_oro_agregado = df.groupby(["fecha_hora_hora", "zona", "municipio"]).agg(
        total_viajes=("id_registro", "count"),
        ganancia_neta_promedio=("ganancia_neta", "mean"),
        ganancia_neta_mediana=("ganancia_neta", "median"),
        tarifa_dinamica_promedio=("tarifa_dinamica", "mean"),
        duracion_promedio_min=("duracion_min", "mean"),
        distancia_promedio_km=("distancia_km", "mean"),
        temperatura_promedio_c=("temperatura_c", "mean"),
        lluvia_acumulada_mm=("lluvia_mm", "sum"),
        viajes_alta_demanda=("flag_atipico_negocio", "sum")
    ).reset_index()
    
    # Redondeo de columnas numericas
    cols_num = df_oro_agregado.select_dtypes(include=[np.number]).columns
    df_oro_agregado[cols_num] = df_oro_agregado[cols_num].round(2)
    
    return df, df_oro_agregado

# ==============================================================================
# 7. EJECUCIÓN MAESTRA DEL PIPELINE
# ==============================================================================
def ejecutar_pipeline_completo():
    """Ejecuta el pipeline completo de Bronce a Plata y Oro con persistencia."""
    print("=" * 70)
    print("INICIANDO PIPELINE DE CALIDAD E1 - OBSERVATORIO GIG ECONOMY")
    print("=" * 70)
    
    # Crear directorios de la arquitectura Medallion
    for carpeta in ["data/plata", "data/oro", "data/cuarentena", "docs/E1"]:
        os.makedirs(carpeta, exist_ok=True)
        
    # Paso 1: Cargar fuentes crudas
    print("\n[PASO 1] Ingestion de Capa Bronce...")
    df_clima = cargar_fuente_clima_bronce()
    df_gig = cargar_y_preparar_bronce_gig()
    print(f" -> Registros Clima Bronce: {len(df_clima)}")
    print(f" -> Registros Gig Bronce: {len(df_gig)}")
    
    # Paso 2: Integracion y Resolucion de Conflictos
    print("\n[PASO 2] Integracion Multifuente y Homologacion de Esquema...")
    df_integrado = integrar_fuentes(df_gig, df_clima)
    print(f" -> Dataset Integrado: {df_integrado.shape[0]} filas x {df_integrado.shape[1]} columnas")
    
    # Paso 3: Puerta de Calidad Pandera y Cuarentena
    print("\n[PASO 3] Evaluando Puerta de Calidad con Pandera...")
    df_conformes, df_cuarentena = evaluar_puerta_calidad(df_integrado)
    
    # Paso 4: Limpieza Estadistica (Faltantes y Atipicos)
    print("\n[PASO 4] Tratamiento de Faltantes e Identificacion de Atipicos...")
    df_plata = ejecutar_limpieza_estadistica(df_conformes)
    
    # Guardar Capa Plata
    df_plata.to_parquet("data/plata/gig_observatorio_plata.parquet", index=False)
    df_plata.to_csv("data/plata/gig_observatorio_plata.csv", index=False, encoding="utf-8")
    print(f" -> Capa Plata exportada: {len(df_plata)} registros validados en data/plata/")
    
    # Paso 5: Capa Oro (Transformaciones, Jerarquias y Reduccion de Datos)
    print("\n[PASO 5] Generacion de Capa Oro y Reduccion Analitica...")
    df_oro_completo, df_oro_reducido = transformar_a_capa_oro(df_plata)
    
    # Guardar Capa Oro
    df_oro_completo.to_parquet("data/oro/gig_observatorio_oro.parquet", index=False)
    df_oro_completo.to_csv("data/oro/gig_observatorio_oro.csv", index=False, encoding="utf-8")
    
    df_oro_reducido.to_parquet("data/oro/gig_observatorio_serie_oro.parquet", index=False)
    df_oro_reducido.to_csv("data/oro/gig_observatorio_serie_oro.csv", index=False, encoding="utf-8")
    
    tasa_reduccion = (1 - (len(df_oro_reducido) / len(df_gig))) * 100
    print(f" -> Capa Oro Completa: {len(df_oro_completo)} registros")
    print(f" -> Capa Oro Reducida (Series Temporales): {len(df_oro_reducido)} periodos agregados")
    print(f" -> Tasa de Reduccion de Volumen de Datos: {tasa_reduccion:.2f}% de reduccion")
    
    print("\n" + "=" * 70)
    print("[PIPELINE COMPLETADO EXITOSAMENTE]")
    print(f"Cuarentena: {len(df_cuarentena)} registros | Plata: {len(df_plata)} | Oro: {len(df_oro_reducido)}")
    print("=" * 70)

if __name__ == "__main__":
    ejecutar_pipeline_completo()
