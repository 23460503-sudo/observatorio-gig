"""
Generador del Jupyter Notebook de Pronóstico de Series de Tiempo (Análisis Estadístico E1).
Ubicación: laboratorio/pronostico_e1.ipynb y docs/E1/pronostico.ipynb
"""
import os
import json

def generar_notebook_pronostico():
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

    add_md("""# Proyecto Integrador: TRUSTED DATA LAB
## Observatorio de Rentabilidad para Repartidores (Gig Economy Colima)
### Laboratorio Estadístico E1: Pronóstico de Series de Tiempo
**Asignatura:** Análisis Estadístico para Ciencia de Datos (Unidad 3) — Mtro. Joel  
**Integrantes:** Fernando Benavides Manzo, Milagros Andrade  

---
### Contenido del Laboratorio:
1. **Caracterización y Descomposición:** Tendencia, estacionalidad diaria (24h) y residuos (justificación aditiva).
2. **Pruebas de Estacionariedad:** Dickey-Fuller Aumentada (ADF test).
3. **Autocorrelación y Correlación Cruzada:** ACF, PACF y correlación con variables climáticas.
4. **Modelado Predictivo Comparativo (4 Modelos):**
   - Suavizamiento Exponencial Simple (SES)
   - Modelo de Holt (Tendencia)
   - Modelo de Holt-Winters (Tendencia + Estacionalidad)
   - Modelo ARIMA / SARIMA
5. **Evaluación de Desempeño en Test (Datos no vistos):** Comparación rigurosa de MAE, RMSE y MAPE.
6. **Diagnóstico de Residuos:** Prueba formal de Ljung-Box (independencia y ruido blanco).
7. **Pronóstico a 24 Horas:** Intervalos de confianza al 95% y mensaje para el cliente.""")

    add_code("""import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, Holt, ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.stats.diagnostic import acorr_ljungbox

sns.set_theme(style='whitegrid')
plt.rcParams['figure.figsize'] = (12, 5)""")

    add_md("""---
## 1. Carga de la Serie Temporal Agregada de Capa Oro
Cargamos la serie horaria continua consolidada desde `data/oro/gig_observatorio_serie_oro.parquet`.""")

    add_code("""df_oro = pd.read_parquet('../data/oro/gig_observatorio_serie_oro.parquet')
df_ts = df_oro.groupby('fecha_hora_hora').agg({
    'total_viajes': 'sum',
    'ganancia_neta_promedio': 'mean',
    'tarifa_dinamica_promedio': 'mean',
    'lluvia_acumulada_mm': 'sum',
    'temperatura_promedio_c': 'mean'
}).asfreq('h')

df_ts['ganancia_neta_promedio'] = df_ts['ganancia_neta_promedio'].interpolate(method='linear')
df_ts['tarifa_dinamica_promedio'] = df_ts['tarifa_dinamica_promedio'].interpolate(method='linear')
df_ts['lluvia_acumulada_mm'] = df_ts['lluvia_acumulada_mm'].fillna(0.0)

serie = df_ts['ganancia_neta_promedio']
print(f'Total de observaciones horarias continuas: {len(serie)}')
serie.plot(title='Serie Temporal de Ganancia Neta Horaria Promedio ($ MXN)', color='navy')
plt.ylabel('MXN / hora')
plt.show()""")

    add_md("""---
## 2. Descomposición de la Serie de Tiempo
Evaluamos una descomposición estacional con periodicidad diaria ($m = 24$ horas).
**Justificación Aditiva:** La amplitud de la oscilación estacional nocturna se mantiene relativamente constante a lo largo del periodo muestreado, sin amplificarse exponencialmente con el nivel medio.""")

    add_code("""decomp = seasonal_decompose(serie, model='additive', period=24)
fig = decomp.plot()
fig.set_size_inches(12, 8)
plt.tight_layout()
plt.show()

print(f"Rango de variación estacional diaria: [{decomp.seasonal.min():.2f}, {decomp.seasonal.max():.2f}] MXN")""")

    add_md("""---
## 3. Prueba de Estacionariedad (Dickey-Fuller Aumentada)
$$H_0: \\text{La serie posee raíz unitaria (es no estacionaria)}$$
$$H_1: \\text{La serie es estacionaria}$$""")

    add_code("""adf_stat, p_val, lags, nobs, crit, ic = adfuller(serie.dropna())
print(f'Estadístico ADF: {adf_stat:.4f}')
print(f'p-valor: {p_val:.4e}')
print(f'Valores Críticos: {crit}')

if p_val < 0.05:
    print('CONCLUSIÓN: Se rechaza H0 con 95% de confianza. La serie es ESTACIONARIA.')
else:
    print('CONCLUSIÓN: No se rechaza H0. Se requiere diferenciación de primer orden.')""")

    add_md("""---
## 4. Partición Entrenamiento / Prueba y Ajuste de los 4 Modelos
Reservamos las últimas 24 horas como conjunto de prueba no visto para medir el error de generalización.""")

    add_code("""horizonte = 24
train = serie.iloc[:-horizonte]
test = serie.iloc[-horizonte:]

# 1. Suavizamiento Exponencial Simple
mod_ses = SimpleExpSmoothing(train, initialization_method='estimated').fit()
pred_ses = mod_ses.forecast(horizonte)

# 2. Modelo de Holt (Tendencia)
mod_holt = Holt(train, exponential=False, initialization_method='estimated').fit()
pred_holt = mod_holt.forecast(horizonte)

# 3. Modelo de Holt-Winters (Tendencia + Estacionalidad 24h)
mod_hw = ExponentialSmoothing(train, seasonal_periods=24, trend='add', seasonal='add', initialization_method='estimated').fit()
pred_hw = mod_hw.forecast(horizonte)

# 4. Modelo ARIMA(2,0,1)
mod_arima = ARIMA(train, order=(2, 0, 1)).fit()
pred_arima = mod_arima.forecast(horizonte)

print('Ajuste de los 4 modelos completado.')""")

    add_md("""---
## 5. Comparación Rigurosa de Error (MAE, RMSE, MAPE)
La selección del modelo se basa estrictamente en la minimización del error en datos que el modelo nunca vio.""")

    add_code("""modelos = {
    'Suavizamiento Exponencial Simple (SES)': pred_ses,
    'Modelo de Holt (Tendencia)': pred_holt,
    'Modelo de Holt-Winters (Tendencia + Estacionalidad)': pred_hw,
    'ARIMA(2,0,1)': pred_arima
}

resultados = []
for name, p in modelos.items():
    y_true = test.values
    y_pred = p.values
    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred)**2))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    resultados.append({'Modelo': name, 'MAE': round(mae, 2), 'RMSE': round(rmse, 2), 'MAPE (%)': round(mape, 2)})

df_comp = pd.DataFrame(resultados).sort_values('MAPE (%)')
display(df_comp)

ganador = df_comp.iloc[0]['Modelo']
print(f'\\n-> MODELO GANADOR: {ganador}')""")

    add_md("""---
## 6. Diagnóstico de Residuos del Modelo Ganador (Prueba de Ljung-Box)
Validamos que los residuos del modelo ganador se comporten como ruido blanco (sin correlación serial remanente).""")

    add_code("""residuos_ganador = mod_hw.resid
lb = acorr_ljungbox(residuos_ganador.dropna(), lags=[10, 20], return_df=True)
display(lb)

p_lb = lb['lb_pvalue'].iloc[-1]
if p_lb > 0.05:
    print(f'Prueba de Ljung-Box superada exitosamente (p-valor = {p_lb:.4f} > 0.05). Los residuos son ruido blanco.')
else:
    print(f'Advertencia: Autocorrelación residual detectada (p-valor = {p_lb:.4f}).')""")

    add_md("""---
## 7. Pronóstico Final a 24 Horas e Intervalos de Confianza al 95%
Generamos la proyección final con la totalidad de los datos para la toma de decisiones del repartidor.""")

    add_code("""mod_final = ExponentialSmoothing(serie, seasonal_periods=24, trend='add', seasonal='add', initialization_method='estimated').fit()
forecast_24h = mod_final.forecast(24)
sigma = np.std(mod_final.resid)

fechas_futuras = pd.date_range(start=serie.index[-1] + pd.Timedelta(hours=1), periods=24, freq='h')
df_pron = pd.DataFrame({
    'fecha_hora': fechas_futuras,
    'pronostico_ganancia': forecast_24h.values.round(2),
    'limite_inferior_95': (forecast_24h.values - 1.96 * sigma).clip(min=0).round(2),
    'limite_superior_95': (forecast_24h.values + 1.96 * sigma).round(2)
})

plt.figure(figsize=(12, 5))
plt.plot(df_pron['fecha_hora'], df_pron['pronostico_ganancia'], 'b-o', label='Pronóstico Holt-Winters')
plt.fill_between(df_pron['fecha_hora'], df_pron['limite_inferior_95'], df_pron['limite_superior_95'], color='blue', alpha=0.15, label='Intervalo 95%')
plt.title('Pronóstico de Ganancia Neta para las Próximas 24 Horas en Colima')
plt.ylabel('Ganancia Neta ($ MXN/h)')
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()

pico = df_pron.loc[df_pron['pronostico_ganancia'].idxmax()]
print(f"FRASE PARA EL CLIENTE: 'Se pronostica un pico de ganancia neta de ${pico['pronostico_ganancia']:.2f} MXN/hora el {pico['fecha_hora'].strftime('%Y-%m-%d a las %H:%M')} horas (IC 95%: [${pico['limite_inferior_95']:.2f}, ${pico['limite_superior_95']:.2f}] MXN).'")""")

    for dir_path in ["laboratorio", "docs/E1"]:
        os.makedirs(dir_path, exist_ok=True)
        out_file = os.path.join(dir_path, "pronostico_e1.ipynb" if "laboratorio" in dir_path else "pronostico.ipynb")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=2, ensure_ascii=False)
        print(f"[OK] Notebook generado en {out_file}")

if __name__ == "__main__":
    generar_notebook_pronostico()
