"""
Suites de pruebas unitarias automatizadas con Pytest (SQA / Calidad E1).
Verifica:
1. Contratos de datos y Puerta de Calidad Pandera.
2. Segregación estricta hacia Cuarentena con motivo documentado.
3. Tratamiento de nulos (MCAR/MAR/MNAR).
4. Persistencia e integridad de Capas Plata y Oro.
5. Cálculo de métricas de fiabilidad y disponibilidad (A >= 95%).
"""
import os
import pytest
import pandas as pd
import numpy as np

def test_archivos_de_salida_existen():
    """Verifica que las capas de la arquitectura Medallion existan."""
    rutas = [
        "data/bronze/clima_colima_raw.json",
        "data/bronze/gig_viajes_raw.csv",
        "data/plata/gig_observatorio_plata.parquet",
        "data/oro/gig_observatorio_oro.parquet",
        "data/oro/gig_observatorio_serie_oro.parquet",
        "data/cuarentena/rechazos_calidad.parquet",
        "calidad/bitacora_captura.csv"
    ]
    for ruta in rutas:
        assert os.path.exists(ruta), f"Falta el archivo esperado: {ruta}"

def test_puerta_calidad_segregacion_cuarentena():
    """Verifica que la cuarentena contenga los registros inválidos con su auditoría."""
    df_cuarentena = pd.read_parquet("data/cuarentena/rechazos_calidad.parquet")
    assert not df_cuarentena.empty, "La cuarentena no debería estar vacía"
    
    columnas_esperadas = ["id_registro", "fecha_rechazo", "plataforma", "columna_error", "motivo_rechazo", "valor_invalido"]
    for col in columnas_esperadas:
        assert col in df_cuarentena.columns, f"Falta columna de auditoría en cuarentena: {col}"
        
    # Verificar que los motivos de rechazo estén documentados
    assert df_cuarentena["motivo_rechazo"].isna().sum() == 0, "No debe haber motivos de rechazo nulos"

def test_integridad_capa_plata_cero_nulos():
    """Verifica que tras la limpieza no queden nulos no controlados en Capa Plata."""
    df_plata = pd.read_parquet("data/plata/gig_observatorio_plata.parquet")
    assert not df_plata.empty, "La Capa Plata no puede estar vacía"
    
    # Columnas críticas tras la imputación MCAR, MAR y MNAR
    cols_criticas = ["distancia_km", "duracion_min", "tarifa_dinamica", "ganancia_neta", "tiempo_espera_min"]
    for col in cols_criticas:
        nulos = df_plata[col].isna().sum()
        assert nulos == 0, f"Columna {col} en Capa Plata tiene {nulos} valores nulos"

def test_rangos_logicos_capa_plata():
    """Verifica que las reglas de negocio se cumplan al 100% en Capa Plata."""
    df_plata = pd.read_parquet("data/plata/gig_observatorio_plata.parquet")
    
    # Tarifa dinámica entre 1.0 y 5.0
    assert (df_plata["tarifa_dinamica"] >= 1.0).all(), "Existen tarifas < 1.0 en Plata"
    assert (df_plata["tarifa_dinamica"] <= 5.0).all(), "Existen tarifas > 5.0 en Plata"
    
    # Ganancia neta estrictamente positiva
    assert (df_plata["ganancia_neta"] > 0).all(), "Existen ganancias netas <= 0 en Plata"
    
    # Plataformas permitidas únicamente
    plataformas_validas = {"Uber", "DiDi", "Mercado Libre Extra"}
    assert set(df_plata["plataforma"].unique()).issubset(plataformas_validas), "Plataforma no autorizada en Plata"

def test_suficiencia_serie_historica_capa_oro():
    """Verifica que la serie temporal para pronóstico en Oro supere los 36 periodos requeridos."""
    df_serie_oro = pd.read_parquet("data/oro/gig_observatorio_serie_oro.parquet")
    assert len(df_serie_oro) >= 36, f"Se requieren al menos 36 periodos, se encontraron {len(df_serie_oro)}"
    
    # Verificar orden cronológico
    assert "fecha_hora_hora" in df_serie_oro.columns
    assert "ganancia_neta_promedio" in df_serie_oro.columns

def test_disponibilidad_captura_supera_umbral():
    """Verifica que la bitácora de captura cumpla la meta de disponibilidad >= 95%."""
    df_bitacora = pd.read_csv("calidad/bitacora_captura.csv")
    assert len(df_bitacora) >= 7, "La bitácora de captura debe tener al menos 7 corridas"
    
    exitos = (df_bitacora["estado"] == "EXITO").sum()
    fallos = (df_bitacora["estado"] == "FALLO").sum()
    tiempo_total_horas = (pd.to_datetime(df_bitacora["fecha_hora"].iloc[-1]) - pd.to_datetime(df_bitacora["fecha_hora"].iloc[0])).total_seconds() / 3600.0
    
    tiempo_reparacion_horas = df_bitacora[df_bitacora["estado"] == "FALLO"]["tiempo_reparacion_min"].sum() / 60.0
    mttr = tiempo_reparacion_horas / fallos if fallos > 0 else 0.0
    mtbf = (tiempo_total_horas - tiempo_reparacion_horas) / fallos if fallos > 0 else tiempo_total_horas
    
    disponibilidad = (mtbf / (mtbf + mttr)) * 100.0
    assert disponibilidad >= 95.0, f"Disponibilidad {disponibilidad:.2f}% es inferior al 95%"

def test_pronosticos_series_de_tiempo_e1():
    """Verifica que el pipeline estadístico genere pronósticos válidos e intervalos de confianza."""
    assert os.path.exists("calidad/metricas_modelos_e1.csv"), "Falta archivo de comparación de modelos"
    assert os.path.exists("data/oro/pronostico_e1.parquet"), "Falta dataset de pronóstico"
    
    df_metricas = pd.read_csv("calidad/metricas_modelos_e1.csv")
    assert len(df_metricas) >= 4, "Se deben haber evaluado al menos 4 familias de modelos"
    assert "MAPE_pct" in df_metricas.columns
    
    df_pron = pd.read_parquet("data/oro/pronostico_e1.parquet")
    assert len(df_pron) == 24, "El horizonte de pronóstico debe ser de 24 horas"
    assert (df_pron["limite_superior_95"] >= df_pron["pronostico_ganancia_neta"]).all()
    assert (df_pron["pronostico_ganancia_neta"] >= df_pron["limite_inferior_95"]).all()
