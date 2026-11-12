# Especificación de Requerimientos del Sistema y Datos (SRS)
## Observatorio de Rentabilidad para Repartidores (Gig Economy Colima)
### Proyecto Integrador: TRUSTED DATA LAB
**Norma de Referencia:** IEEE Std 830 / ISO/IEC/IEEE 29148  
**Fecha:** Noviembre de 2026 | **Versión:** 1.0 (Entrega E1)  

---

## 1. Criterios de Calidad de los Requerimientos
Cada requerimiento ha sido evaluado y validado contra las 4 características fundamentales exigidas por el modelo SQA:
- **Necesario:** Satisface una necesidad crítica del cliente o una restricción legal/técnica del sistema.
- **No Ambiguo:** Posee una redacción precisa con una única interpretación cuantificable.
- **Verificable:** Cuenta con un método de prueba finito, determinístico y reproducible para comprobar su cumplimiento.
- **Rastreable:** Está indexado con identificador único que vincula el diseño, el código y los casos de prueba.

---

## 2. Matriz de Requerimientos Verificables

| ID | Tipo | Descripción del Requerimiento | Criterio de Verificación / Forma de Comprobación | Estado |
|---|---|---|---|---|
| **REQ-ING-01** | Funcional (Datos) | El sistema debe ingerir automáticamente observaciones climáticas horarias desde la API pública de Open-Meteo para las coordenadas metropolitanas $(19.2433, -103.7247)$ almacenándolas en Capa Bronce sin transformación. | Inspección de `data/bronze/clima_colima_raw.json` verificando presencia de campos `temperature_2m`, `rain`, `weathercode` y al menos 36 periodos cronológicos. | Verificado |
| **REQ-ING-02** | Calidad (Pandera) | Todo registro antes de promoverse a Capa Plata debe validarse contra el esquema estricto de Pandera; cualquier registro con tarifa dinámica fuera de $[1.0, 5.0]$, ganancia $\le 0$, o plataforma no autorizada debe enviarse a cuarentena. | Ejecución de `src/pipeline_e1.py` comprobando que los registros inválidos ingresen a `data/cuarentena/rechazos_calidad.parquet` con motivo documentado y 0 fugas a Plata. | Verificado |
| **REQ-ING-03** | Calidad (Cuarentena) | El sistema nunca debe borrar registros no conformes en silencio; cada descarte debe registrar identificador, fecha/hora de rechazo, atributo fallido y descripción de regla infringida. | Verificación de columnas `id_registro`, `fecha_rechazo`, `columna_error`, `motivo_rechazo` en `data/cuarentena/rechazos_calidad.csv`. | Verificado |
| **REQ-ING-04** | Datos (Faltantes) | El sistema debe diagnosticar el mecanismo de pérdida de nulos (MCAR, MAR, MNAR) e imputar distancias por mediana de zona (MCAR), esperas por mediana de turno (MAR) y estimar ganancias por modelo base km (MNAR). | Ejecución del test de nulos en `tests/test_calidad_datos.py` confirmando cero valores `NaN` en `data/plata/gig_observatorio_plata.parquet`. | Verificado |
| **REQ-ING-05** | Datos (Atípicos) | Los valores atípicos identificados mediante IQR o Z-Score Robusto (MAD) que correspondan a picos reales de demanda o lluvia no deben ser eliminados, sino etiquetados con `flag_atipico_negocio = 1`. | Comprobación de existencia de la columna `flag_atipico_negocio` en Capa Plata y Oro con registros debidamente clasificados. | Verificado |
| **REQ-EST-01** | Analítico (Modelado) | El observatorio debe ajustar y comparar cuatro familias de modelos de series de tiempo (SES, Holt, Holt-Winters y ARIMA/SARIMA) sobre la serie horaria agregada de Capa Oro. | Inspección de `laboratorio/pronostico_e1.ipynb` verificando cálculo de métricas de error (MAE, RMSE, MAPE) en conjunto de prueba no visto. | Verificado |
| **REQ-EST-02** | Estadístico (Residuos) | El modelo ganador seleccionado por mínimo error debe someterse a la prueba de Ljung-Box sobre sus residuos, comprobando ausencia de autocorrelación serial ($p\text{-valor} > 0.05$). | Verificación del reporte de prueba de Ljung-Box y gráfico de residuos en el notebook de pronóstico. | Verificado |
| **REQ-CAL-01** | Fiabilidad | El flujo de captura programada debe registrar cada ciclo de extracción en `calidad/bitacora_captura.csv` manteniendo una disponibilidad $A \ge 95.0\%$. | Cálculo automático mediante `src/generar_bitacora_captura.py`: disponibilidad empírica obtenida $= 99.43\% \ge 95.0\%$. | Verificado |
| **REQ-CAL-02** | Seguridad | El repositorio no debe exponer secretos, credenciales API ni tokens en el historial de Git, verificado mediante escaneo con `gitleaks`. | Ejecución del workflow de seguridad en `.github/workflows/ci.yml` con 0 hallazgos abiertos. | Verificado |
| **REQ-CAL-03** | Calidad (PSP) | Cada integrante del equipo debe registrar individualmente sus tiempos y defectos encontrados por fase en archivos CSV según el estándar PSP. | Verificación de bitácoras activas `calidad/defectos-*.csv` y `calidad/tiempo-*.csv` con fases y minutos netos registrados. | Verificado |
