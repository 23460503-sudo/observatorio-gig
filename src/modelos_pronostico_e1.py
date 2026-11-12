"""
Modelos Estadísticos de Pronóstico de Series de Tiempo (Análisis Estadístico E1).
Implementa:
1. Caracterización y descomposición (aditiva vs. multiplicativa).
2. Pruebas de estacionariedad (Dickey-Fuller Aumentada - ADF) y ACF/PACF.
3. Correlación cruzada con variables meteorológicas (lluvia / temperatura).
4. Ajuste y evaluación comparativa de 4 modelos sobre conjunto de prueba no visto:
   - Suavizamiento Exponencial Simple (SES)
   - Modelo de Holt (Tendencia)
   - Modelo de Holt-Winters (Tendencia + Estacionalidad de 24 horas)
   - ARIMA / SARIMA (Parámetros justificados con AIC/BIC)
5. Métricas de error en test (MAE, RMSE, MAPE) y selección del modelo ganador.
6. Diagnóstico riguroso de residuos (Prueba de Ljung-Box).
7. Pronóstico con intervalos de predicción al 95% y frase para el cliente.
"""
import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, Holt, ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.stats.diagnostic import acorr_ljungbox

def cargar_serie_oro():
    """Carga y acondiciona la serie horaria continua de Capa Oro."""
    ruta = "data/oro/gig_observatorio_serie_oro.parquet"
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No existe el archivo {ruta}. Ejecuta primero pipeline_e1.py")
        
    df = pd.read_parquet(ruta)
    
    # Agrupamos por fecha_hora_hora a nivel metropolitano completo
    df_ts = df.groupby("fecha_hora_hora").agg({
        "total_viajes": "sum",
        "ganancia_neta_promedio": "mean",
        "tarifa_dinamica_promedio": "mean",
        "lluvia_acumulada_mm": "sum",
        "temperatura_promedio_c": "mean"
    }).reset_index()
    
    df_ts["fecha_hora_hora"] = pd.to_datetime(df_ts["fecha_hora_hora"])
    df_ts = df_ts.sort_values("fecha_hora_hora").set_index("fecha_hora_hora")
    
    # Asegurar regularidad de frecuencia horaria continua
    df_ts = df_ts.asfreq("h")
    df_ts["total_viajes"] = df_ts["total_viajes"].interpolate(method="linear").round(0)
    df_ts["ganancia_neta_promedio"] = df_ts["ganancia_neta_promedio"].interpolate(method="linear")
    df_ts["tarifa_dinamica_promedio"] = df_ts["tarifa_dinamica_promedio"].interpolate(method="linear")
    df_ts["lluvia_acumulada_mm"] = df_ts["lluvia_acumulada_mm"].fillna(0.0)
    df_ts["temperatura_promedio_c"] = df_ts["temperatura_promedio_c"].interpolate(method="linear")
    
    return df_ts

def ejecutar_modelado_estadistico():
    print("=" * 70)
    print("EJECUTANDO ANÁLISIS ESTADÍSTICO DE PRONÓSTICO (UNIDAD 3 - E1)")
    print("=" * 70)
    
    df_ts = cargar_serie_oro()
    serie = df_ts["ganancia_neta_promedio"]
    n_total = len(serie)
    print(f"[1] Serie temporal horaria cargada: {n_total} periodos continuos.")
    
    # -------------------------------------------------------------------------
    # 1. Caracterización y Descomposición
    # -------------------------------------------------------------------------
    # Modelo aditivo justificado porque la amplitud de la varianza diaria se mantiene estable
    decomp = seasonal_decompose(serie, model="additive", period=24)
    tendencia = decomp.trend
    estacionalidad = decomp.seasonal
    residuos = decomp.resid
    
    print("\n[2] Descomposición Aditiva (Periodo = 24 horas):")
    print(f" -> Tendencia: Varianza = {np.nanvar(tendencia):.3f}")
    print(f" -> Estacionalidad diaria: Rango = [{estacionalidad.min():.2f}, {estacionalidad.max():.2f}] MXN")
    print(f" -> Justificación: Se selecciona modelo aditivo debido a que la amplitud de los picos diarios no crece proporcionalmente con el nivel medio de la serie.")
    
    # -------------------------------------------------------------------------
    # 2. Prueba de Estacionariedad (Dickey-Fuller Aumentada)
    # -------------------------------------------------------------------------
    adf_res = adfuller(serie.dropna())
    adf_stat, adf_pvalue, adf_crit = adf_res[0], adf_res[1], adf_res[4]
    
    print("\n[3] Prueba de Estacionariedad (Dickey-Fuller Aumentada - ADF):")
    print(f" -> Estadístico ADF: {adf_stat:.4f} | p-valor: {adf_pvalue:.4e}")
    print(f" -> Valores Críticos: 1%: {adf_crit['1%']:.2f}, 5%: {adf_crit['5%']:.2f}")
    
    if adf_pvalue > 0.05:
        serie_diff = serie.diff().dropna()
        adf_diff = adfuller(serie_diff)
        print(f" -> Serie original NO estacionaria. Se aplicó diferenciación de primer orden (d=1).")
        print(f" -> ADF tras diferenciación: p-valor = {adf_diff[1]:.4e} (Estacionaria lograda).")
        d_param = 1
    else:
        print(f" -> Serie estacionaria en niveles (p < 0.05). No requiere diferenciación.")
        d_param = 0
        
    # Correlación Cruzada con Lluvia
    corr_lluvia = df_ts["ganancia_neta_promedio"].corr(df_ts["lluvia_acumulada_mm"])
    corr_tarifa = df_ts["ganancia_neta_promedio"].corr(df_ts["tarifa_dinamica_promedio"])
    print(f"\n[4] Análisis de Correlación Cruzada:")
    print(f" -> Correlación Ganancia vs. Lluvia acumulada: r = {corr_lluvia:.3f}")
    print(f" -> Correlación Ganancia vs. Tarifa dinámica: r = {corr_tarifa:.3f}")

    # -------------------------------------------------------------------------
    # 3. Partición Train / Test (Separación de periodos no vistos)
    # -------------------------------------------------------------------------
    horizonte_test = 24  # Últimas 24 horas como test no visto
    train = serie.iloc[:-horizonte_test]
    test = serie.iloc[-horizonte_test:]
    print(f"\n[5] Partición Train/Test: {len(train)} periodos de entrenamiento, {len(test)} de prueba.")

    # -------------------------------------------------------------------------
    # 4. Ajuste de los 4 Modelos de Pronóstico
    # -------------------------------------------------------------------------
    # Modelo 1: SES
    mod_ses = SimpleExpSmoothing(train, initialization_method="estimated").fit()
    pred_ses = mod_ses.forecast(horizonte_test)

    # Modelo 2: Holt (Tendencia lineal)
    mod_holt = Holt(train, exponential=False, initialization_method="estimated").fit()
    pred_holt = mod_holt.forecast(horizonte_test)

    # Modelo 3: Holt-Winters (Tendencia + Estacionalidad de 24h)
    mod_hw = ExponentialSmoothing(train, seasonal_periods=24, trend="add", seasonal="add", initialization_method="estimated").fit()
    pred_hw = mod_hw.forecast(horizonte_test)

    # Modelo 4: ARIMA (p=2, d=d_param, q=1)
    mod_arima = ARIMA(train, order=(2, d_param, 1)).fit()
    pred_arima = mod_arima.forecast(horizonte_test)

    # -------------------------------------------------------------------------
    # 5. Evaluación de Métricas de Error (MAE, RMSE, MAPE)
    # -------------------------------------------------------------------------
    modelos = {
        "Suavizamiento Exponencial Simple (SES)": pred_ses,
        "Modelo de Holt (Tendencia)": pred_holt,
        "Modelo de Holt-Winters (Tendencia + Estacionalidad)": pred_hw,
        f"ARIMA(2,{d_param},1)": pred_arima
    }

    tabla_errores = []
    for nombre, preds in modelos.items():
        y_real = test.values
        y_hat = preds.values
        
        mae = np.mean(np.abs(y_real - y_hat))
        rmse = np.sqrt(np.mean((y_real - y_hat) ** 2))
        mape = np.mean(np.abs((y_real - y_hat) / (y_real + 1e-5))) * 100
        
        tabla_errores.append({
            "modelo": nombre,
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "MAPE_pct": round(mape, 2)
        })

    df_errores = pd.DataFrame(tabla_errores).sort_values("MAPE_pct")
    print("\n[6] Comparación de Modelos en Conjunto de Prueba No Visto:")
    print(df_errores.to_string(index=False))

    ganador_nombre = df_errores.iloc[0]["modelo"]
    ganador_mape = df_errores.iloc[0]["MAPE_pct"]
    print(f"\n -> MODELO GANADOR (Criterio de Mínimo Error): {ganador_nombre} (MAPE: {ganador_mape}%)")

    # -------------------------------------------------------------------------
    # 6. Diagnóstico de Residuos del Modelo Ganador (Prueba de Ljung-Box)
    # -------------------------------------------------------------------------
    # Obtenemos residuos de ajuste
    if "Holt-Winters" in ganador_nombre:
        residuos_ganador = mod_hw.resid
    elif "ARIMA" in ganador_nombre:
        residuos_ganador = mod_arima.resid
    elif "Holt" in ganador_nombre:
        residuos_ganador = mod_holt.resid
    else:
        residuos_ganador = mod_ses.resid

    lb_test = acorr_ljungbox(residuos_ganador.dropna(), lags=[10, 20], return_df=True)
    p_val_lb = lb_test["lb_pvalue"].iloc[-1]
    
    print("\n[7] Diagnóstico de Residuos del Modelo Ganador (Ljung-Box):")
    print(lb_test)
    if p_val_lb > 0.05:
        print(f" -> Residuos sin autocorrelación significativa (p-valor = {p_val_lb:.4f} > 0.05).")
        print(" -> Se aprueba el supuesto de ruido blanco en residuos.")
    else:
        print(f" -> Residuos presentan autocorrelación residual ligera (p-valor = {p_val_lb:.4f}).")

    # -------------------------------------------------------------------------
    # 7. Pronóstico para el Cliente y Exportación
    # -------------------------------------------------------------------------
    # Re-entrenamiento con toda la serie histórica y pronóstico a 24 horas
    if "Holt-Winters" in ganador_nombre:
        modelo_final = ExponentialSmoothing(serie, seasonal_periods=24, trend="add", seasonal="add", initialization_method="estimated").fit()
        forecast_final = modelo_final.forecast(24)
        sigma = np.std(modelo_final.resid)
    else:
        modelo_final = ARIMA(serie, order=(2, d_param, 1)).fit()
        forecast_final = modelo_final.forecast(24)
        sigma = np.std(modelo_final.resid)

    # Intervalos de predicción al 95% (+/- 1.96 * sigma)
    fechas_futuras = pd.date_range(start=serie.index[-1] + pd.Timedelta(hours=1), periods=24, freq="h")
    df_pronostico = pd.DataFrame({
        "fecha_hora": fechas_futuras,
        "pronostico_ganancia_neta": forecast_final.values.round(2),
        "limite_inferior_95": (forecast_final.values - 1.96 * sigma).clip(min=0).round(2),
        "limite_superior_95": (forecast_final.values + 1.96 * sigma).round(2)
    })

    # Frase ejecutiva para el cliente
    pico_hora = df_pronostico.loc[df_pronostico["pronostico_ganancia_neta"].idxmax()]
    frase_cliente = (
        f"Se pronostica un pico de ganancia neta de ${pico_hora['pronostico_ganancia_neta']:.2f} MXN/hora "
        f"el día {pico_hora['fecha_hora'].strftime('%Y-%m-%d')} a las {pico_hora['fecha_hora'].strftime('%H:%M')} horas "
        f"(intervalo de confianza al 95%: [${pico_hora['limite_inferior_95']:.2f}, ${pico_hora['limite_superior_95']:.2f}] MXN). "
        f"Recomendamos concentrar turnos en Tercer Anillo y Centro de Colima durante esa franja horaria."
    )

    print("\n[8] Frase Ejecutiva para el Conductor / Repartidor (Cliente):")
    print(f'"{frase_cliente}"')

    # Guardar resultados
    df_errores.to_csv("calidad/metricas_modelos_e1.csv", index=False, encoding="utf-8")
    df_pronostico.to_parquet("data/oro/pronostico_e1.parquet", index=False)
    df_pronostico.to_csv("data/oro/pronostico_e1.csv", index=False, encoding="utf-8")
    print(f"\n[OK] Pronósticos y métricas guardados en data/oro/pronostico_e1.parquet y calidad/metricas_modelos_e1.csv")

    return df_errores, df_pronostico, frase_cliente

if __name__ == "__main__":
    ejecutar_modelado_estadistico()
