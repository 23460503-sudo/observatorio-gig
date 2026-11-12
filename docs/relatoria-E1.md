# Relatoría E1 · Observatorio de Rentabilidad para Repartidores (Gig Economy Colima)
**Equipo:** Fernando Benavides Manzo, Milagros Andrade  
**Periodo:** 09 de noviembre de 2026 al 12 de noviembre de 2026  

---

## 1. Qué nos propusimos
Diseñar, construir y certificar de manera automatizada el flujo completo de la Entrega E1 integrando las tres asignaturas del Proyecto Integrador TRUSTED DATA LAB:
1. **Ingeniería de Datos:** Ingestar datos multifuente (Open-Meteo y Gig Mobility), resolver discrepancias de esquema y tipos, evaluar el 100% de los datos mediante una Puerta de Calidad declarativa con Pandera enrutando registros corruptos a Cuarentena, y ejecutar limpieza estadística (imputación justificada MCAR/MAR/MNAR, detección IQR/MAD, normalización, estandarización y discretización) poblando Capas Plata y Oro.
2. **Análisis Estadístico:** Caracterizar la serie temporal horaria de demanda y rentabilidad, descomponerla estacionalmente (24h), comprobar estacionariedad con la prueba de Dickey-Fuller aumentada (ADF), ajustar cuatro familias de modelos de pronóstico (SES, Holt, Holt-Winters y ARIMA), seleccionar el modelo ganador por menor error de prueba (MAE, RMSE, MAPE) y comprobar que sus residuos sean ruido blanco mediante la prueba de Ljung-Box.
3. **Calidad en los Sistemas de Información:** Redactar la especificación de requerimientos verificables, formalizar el Plan SQA bajo norma IEEE 730, auditar la seguridad del repositorio (cero secretos con Gitleaks y dependencias limpias con pip-audit), medir empíricamente la disponibilidad del sistema de captura con 7 días de bitácora ($A \ge 95\%$) e implementar Integración Continua (CI) en GitHub Actions con pruebas unitarias en `pytest`.

---

## 2. Qué hicimos (cronología con fechas, responsable y horas)
A partir de las bitácoras individuales de tiempo del Personal Software Process (PSP):

- **2026-11-09 (15:00 - 16:30 | 80 min netos):** Fernando Benavides diseñó la arquitectura Medallion por capas (Bronce $\rightarrow$ Plata $\rightarrow$ Oro $\rightarrow$ Cuarentena) y definió las reglas de validación en Pandera para segregar registros defectuosos.
- **2026-11-09 (15:00 - 16:30 | 90 min netos):** Milagros Andrade auditó la estructura JSON de la API de Open-Meteo y definió las jerarquías conceptuales de zonificación (Coordenadas $\rightarrow$ Corredor Comercial $\rightarrow$ Municipio $\rightarrow$ Estado).
- **2026-11-09 (16:30 - 18:30 | 105 min netos):** Fernando Benavides implementó el script maestro `src/pipeline_e1.py`, codificando el tratamiento formal de faltantes (MCAR, MAR, MNAR) y los algoritmos de detección de atípicos (IQR y MAD).
- **2026-11-10 (10:00 - 12:00 | 105 min netos):** Milagros Andrade revisó el esquema de Pandera contra las reglas de negocio, elaboró el diccionario de datos de la Capa Oro y documentó las discrepancias de esquemas y tipos resueltas.
- **2026-11-10 (14:00 - 16:00 | 120 min netos):** Fernando Benavides ejecutó las pruebas de integración del pipeline, validó la persistencia en formato Parquet y CSV, y verificó que los 60 registros corruptos cayeran en `data/cuarentena/`.
- **2026-11-10 (14:00 - 15:30 | 90 min netos):** Milagros Andrade redactó la ficha técnica preliminar y compiló el notebook interactivo `docs/E1/limpieza.ipynb`.
- **2026-11-11 (15:30 - 17:30 | 105 min netos):** Milagros Andrade elaboró la matriz de requerimientos verificables del observatorio (`docs/requerimientos.md`) bajo lineamientos IEEE 830 y redactó el informe de auditoría de seguridad (`docs/E1/seguridad.md`).
- **2026-11-11 (16:00 - 18:00 | 110 min netos):** Fernando Benavides construyó la suite de pruebas unitarias automatizadas con `pytest` (`tests/test_calidad_datos.py`), el flujo de integración continua `.github/workflows/ci.yml` y formalizó el Plan SQA bajo norma IEEE 730 (`docs/plan_SQA.md`).
- **2026-11-12 (10:00 - 12:00 | 120 min netos):** Fernando Benavides implementó el pipeline de modelos de pronóstico en `src/modelos_pronostico_e1.py`, ajustando los cuatro modelos de series de tiempo y la prueba de diagnóstico de residuos de Ljung-Box.
- **2026-11-12 (10:30 - 12:15 | 105 min netos):** Milagros Andrade evaluó la tabla de métricas comparativas de error (MAE, RMSE, MAPE), compiló los notebooks de pronóstico (`laboratorio/pronostico_e1.ipynb` y `docs/E1/pronostico.ipynb`) y redactó la frase ejecutiva para el cliente.

**Total tiempo acumulado invertido en E1:** 1,030 minutos (17.17 horas) de esfuerzo neto de ingeniería, estadística y aseguramiento de calidad.

---

## 3. Qué decidimos y por qué (alternativas descartadas)

1. **Selección del modelo de pronóstico ganador por MAPE y no por sofisticación:**
   - *Decisión:* Se seleccionó el **Modelo de Holt-Winters con estacionalidad aditiva de 24 horas**, el cual arrojó el menor error porcentual absoluto medio ($MAPE = 36.02\%$, $MAE = 62.04$), superando a ARIMA(2,0,1) ($MAPE = 41.27\%$) y a SES ($MAPE = 41.24\%$).
   - *Alternativa descartada:* Imponer ARIMA de forma dogmática por ser más complejo matemáticamente. La rúbrica establece explícitamente: *"Gana el modelo con menor error, no el más sofisticado"*.
2. **Uso de Pandera frente a validación manual con asserts o Great Expectations:**
   - *Decisión:* Se eligió **Pandera** debido a su integración nativa y tipado estático con DataFrames de pandas, permitiendo validaciones declarativas directas en código y ejecución ultra-rápida (1.47 s) en suites de pruebas `pytest` y en el runner de GitHub Actions.
   - *Alternativa descartada:* Great Expectations fue descartado por su excesivo overhead de configuración para pipelines de arranque.
3. **Mecanismo de Cuarentena auditable frente al descarte silencioso:**
   - *Decisión:* Segregar anomalías a `data/cuarentena/rechazos_calidad.parquet` con trazabilidad completa (ID, fecha, columna de error y motivo detallado).
   - *Alternativa descartada:* Utilizar métodos destructivos (`dropna()` o filtrado directo) que ocultan errores sistemáticos en los extractores o intentos de inyección de datos corruptos.
4. **Descomposición aditiva vs. multiplicativa en series de tiempo:**
   - *Decisión:* Se adoptó la descomposición aditiva tras comprobar que la variabilidad estacional pico de fin de semana ($[-44.10, +66.93]$ MXN) no crece de forma proporcional al nivel base de la serie.

---

## 4. Qué salió mal y cómo lo corregimos (con número de defecto)

- **Defecto Fernando #2 (Tipo: Datos | 20 min corrección):**  
  *Problema:* Al parsear la columna cruda `ganancia_raw`, la presencia mixta de prefijos `$` y sufijos `MXN` provocaba que la conversión directa a float devolviera `NaN`, corrompiendo cálculos en cascada.  
  *Solución:* Se programó una función de desinfección con expresiones regulares que limpia cualquier carácter no numérico previo al casting a `float`.
- **Defecto Fernando #3 (Tipo: Interfaz | 15 min corrección):**  
  *Problema:* Al realizar el redondeo final con `.round(2)` sobre el DataFrame agregado de Capa Oro, pandas arrojó un `UserWarning` advirtiendo que columnas tipo `datetime` no aceptan redondeo numérico.  
  *Solución:* Se aisló el redondeo aplicando `select_dtypes(include=[np.number])` exclusivamente sobre métricas continuas.
- **Defecto Fernando #4 (Tipo: Datos | 15 min corrección):**  
  *Problema:* Al parsear fechas mixtas con `pd.to_datetime(..., format='mixed')`, cadenas como `01/11/2026` fueron interpretadas como 11 de enero en lugar de 1 de noviembre (confusión día/mes en formatos latinoamericanos vs. anglosajones).  
  *Solución:* Se diseñó la función `parse_fecha_robusta` que discrimina prefijos de 4 dígitos (ISO YYYY-MM-DD) de formatos DD/MM/YYYY aplicando `dayfirst=True` condicionalmente.
- **Defecto Fernando #5 (Tipo: Interfaz | 10 min corrección):**  
  *Problema:* `statsmodels 0.15` en Python 3.14 arrojaba `TypeError: initialization_method must be a string` en `SimpleExpSmoothing` y `Holt-Winters` si no se pasaba explícitamente el argumento `"estimated"`.  
  *Solución:* Se especificó `initialization_method="estimated"` en todas las instanciaciones de modelos de suavizamiento.
- **Defecto Milagros #2 (Tipo: Verificación | 25 min corrección):**  
  *Problema:* Desfase de horas entre los datos de Open-Meteo (emitidos en UTC por defecto) y los registros de campo de viajes en Colima (tiempo local UTC-6).  
  *Solución:* Se unificó el truncamiento de `fecha_hora_hora` sobre la misma base horaria local antes del merge.
- **Defecto Milagros #3 (Tipo: Datos | 15 min corrección):**  
  *Problema:* El esquema estricto inicial de Pandera rechazaba filas que tenían distancia nula (`NaN`) directamente en la puerta de calidad, enviando a cuarentena datos que debían ser imputados metodológicamente (MCAR).  
  *Solución:* Se ajustó la regla de Pandera para permitir `nullable=True` en campos sujetos a imputación estadística controlada, reservando el rechazo a cuarentena para inconsistencias irrecuperables.
- **Defecto Milagros #4 (Tipo: Verificación | 15 min corrección):**  
  *Problema:* Al ajustar ARIMA(2,0,1) se generaba advertencia de no estacionariedad inicial en los parámetros autorregresivos.  
  *Solución:* Se verificó que la serie es estacionaria en niveles tras la prueba ADF ($p = 1.67 \times 10^{-8}$) y se optimizaron los puntos de partida de máxima verosimilitud.

---

## 5. Qué aprendimos de cada materia

### Ingeniería de Datos
Comprendimos que la arquitectura Medallion es la columna vertebral de un sistema analítico confiable. La inmutabilidad de la Capa Bronce permite reproducir cualquier cálculo desde el origen; la Capa Plata resuelve la heterogeneidad de fuentes dispares (Entity Resolution, formatos de fecha confusos y limpieza de cadenas monetarias); y la Capa Oro sintetiza los datos en modelos dimensionales optimizados para el consumo analítico, logrando una reducción de volumen del 17.1% sin pérdida de resolución temporal.

### Análisis Estadístico para Ciencia de Datos
Aprendimos que un pronóstico jamás debe elegirse por la popularidad o sofisticación del algoritmo, sino por su desempeño empírico en un conjunto de prueba no visto (*out-of-sample testing*). El modelo de Holt-Winters capturó con precisión el ritmo circadiano de 24 horas del comportamiento urbano de Colima, superando a ARIMA. Asimismo, confirmamos la importancia crucial del diagnóstico de residuos: la prueba de Ljung-Box ($p = 0.9435$) demostró que los errores del modelo carecen de autocorrelación y se comportan como ruido blanco, garantizando la validez de los intervalos de predicción al 95%.

### Calidad en los Sistemas de Información
Aprendimos a aplicar el principio del Personal Software Process (PSP): registrar defectos y tiempos en el momento exacto en que ocurren permite identificar qué fases del proceso inyectan más errores (en nuestro caso, la fase de código por discrepancias de tipos de datos). Asimismo, la formalización del Plan SQA bajo IEEE 730 y la creación de una suite automatizada de pruebas con `pytest` integrada a GitHub Actions transforma el control de calidad en un guardián automático continuo: ningún cambio de código puede integrarse a la rama principal si corrompe los contratos de datos o reduce la disponibilidad del sistema por debajo del 95%.

---

## 6. Evidencias
- **Pipeline ETL maestro:** [`src/pipeline_e1.py`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/src/pipeline_e1.py)
- **Modelos de pronóstico:** [`src/modelos_pronostico_e1.py`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/src/modelos_pronostico_e1.py)
- **Notebooks interactivos:**
  - Limpieza y Puerta de Calidad: [`docs/E1/limpieza.ipynb`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/docs/E1/limpieza.ipynb)
  - Pronóstico y Series de Tiempo: [`laboratorio/pronostico_e1.ipynb`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/laboratorio/pronostico_e1.ipynb) y [`docs/E1/pronostico.ipynb`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/docs/E1/pronostico.ipynb)
- **Métricas de error de modelos:** [`calidad/metricas_modelos_e1.csv`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/calidad/metricas_modelos_e1.csv)
- **Pronóstico futuro a 24 horas:** [`data/oro/pronostico_e1.parquet`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/data/oro/pronostico_e1.parquet)
- **Plan SQA (IEEE 730):** [`docs/plan_SQA.md`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/docs/plan_SQA.md)
- **Requerimientos verificables (SRS):** [`docs/requerimientos.md`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/docs/requerimientos.md)
- **Auditoría de seguridad:** [`docs/E1/seguridad.md`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/docs/E1/seguridad.md)
- **Suite de pruebas Pytest (7 aprobadas):** [`tests/test_calidad_datos.py`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/tests/test_calidad_datos.py)
- **Flujo de Integración Continua (CI):** [`.github/workflows/ci.yml`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/.github/workflows/ci.yml)
- **Bitácoras PSP de defectos y tiempo:** Carpeta [`calidad/`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/calidad/)

---

## Uso de IA generativa (herramienta y para qué)
Se utilizó el asistente de inteligencia artificial **Antigravity (Google DeepMind)** como compañero de pair-programming para:
1. Diseñar y optimizar la estructura del `DataFrameSchema` de Pandera para la validación estricta de reglas de negocio en la Puerta de Calidad.
2. Formular los algoritmos de detección de atípicos con estimadores de escala robusta (MAD y factor normalizador $1.4826$).
3. Estructurar y depurar el pipeline comparativo de series de tiempo con `statsmodels` (SES, Holt, Holt-Winters y ARIMA) y la prueba diagnóstica de Ljung-Box.
4. Diseñar las suites de pruebas unitarias en `pytest` y configurar el flujo de GitHub Actions para Integración Continua bajo estándares IEEE 730.  
Todos los modelos, pruebas, código fuente y formulaciones matemáticas fueron minuciosamente auditados, ajustados y ejecutados localmente por los integrantes del equipo.
