# Observatorio de Rentabilidad para Repartidores y Conductores (Gig Economy)
### Proyecto Integrador: TRUSTED DATA LAB
**Tecnológico Nacional de México — Instituto Tecnológico de Colima**

---

## 📌 Visión General
El **Observatorio de Rentabilidad Gig Economy** analiza en qué horarios, zonas geográficas y condiciones meteorológicas se maximiza la ganancia neta por hora de los conductores y repartidores de plataformas digitales (**Uber, DiDi, Mercado Libre Extra**) en la zona conurbada de **Colima y Villa de Álvarez**.

El sistema integra datos meteorológicos en tiempo real de Open-Meteo con telemetría de movilidad urbana, aplicando una **arquitectura Medallion por capas**, **puertas de calidad declarativas con Pandera**, **modelos estadísticos de series de tiempo (Holt-Winters, ARIMA)** y aseguramiento continuo de software bajo la norma **IEEE 730**.

---

## 👥 Integrantes del Equipo
- **Fernando Benavides Manzo** (Data Engineer / Quality Lead)
- **Milagros Andrade** (Data Statistician / Quality Lead)

### Asignaturas Integradas
1. **Ingeniería de Datos (CMD-2602, Unidades 3 y 4)** — Mtro. Román
2. **Análisis Estadístico para Ciencia de Datos (Unidades 3, 4 y 5)** — Mtro. Joel
3. **Calidad en los Sistemas de Información (IFC-1008, Unidades 3 y 4)** — Mtra. Isis

---

## 🏛️ Estructura del Repositorio

```
observatorio-gig/
├── data/
│   ├── bronze/          # Datos crudos inmutables (Clima Open-Meteo + Gig CSV)
│   ├── plata/           # Datos limpios, integrados y validados (Parquet y CSV)
│   ├── oro/             # Datos preparados para modelos analíticos, series y pronósticos
│   └── cuarentena/      # Registros rechazados por la Puerta de Calidad con auditoría
├── docs/
│   ├── E0/              # Entrega E0: Ficha técnica y Propuesta metodológica (3-5 páginas)
│   ├── E1/              # Entrega E1: Ficha técnica, notebooks de limpieza y pronóstico, y seguridad
│   ├── requerimientos.md# Matriz de requerimientos verificables del observatorio (SRS)
│   ├── plan_SQA.md      # Plan de Aseguramiento de Calidad bajo norma IEEE 730
│   └── relatoria-E1.md  # Relatoría oficial de etapa con estándares PSP
├── extractores/         # Extractores éticos con robots.txt y rate-limit
│   └── base.py
├── laboratorio/         # Notebooks reproducibles de modelado estadístico
│   └── pronostico_e1.ipynb
├── tests/               # Suites de pruebas unitarias automatizadas (Pytest)
│   └── test_calidad_datos.py
├── calidad/             # Bitácoras de calidad PSP (tiempos, defectos y captura activa)
│   ├── defectos-fernando.csv
│   ├── defectos-milagros.csv
│   ├── tiempo-fernando.csv
│   ├── tiempo-milagros.csv
│   ├── bitacora_captura.csv
│   └── metricas_modelos_e1.csv
├── src/                 # Pipelines de datos, extractores y scripts ejecutables
│   ├── pipeline_e1.py
│   ├── modelos_pronostico_e1.py
│   ├── generar_fuentes_bronce.py
│   └── generar_bitacora_captura.py
└── .github/workflows/   # Captura programada y CI/CD con GitHub Actions
    ├── ci.yml
    └── extractor.yml
```

---

## 🚀 Instrucciones de Ejecución y Reproducibilidad

### 1. Clonar el repositorio e instalar dependencias
```bash
git clone https://github.com/23460503-sudo/observatorio-gig.git
cd observatorio-gig
pip install pandas pandera pyarrow fastparquet requests pytest scipy statsmodels
```

### 2. Ejecutar el Pipeline de Ingeniería de Datos (Bronce -> Plata -> Oro)
```bash
python src/pipeline_e1.py
```
- Ingesta y homogeniza fuentes heterogéneas.
- Valida reglas de negocio con **Pandera** y segrega anomalías a `data/cuarentena/`.
- Aplica tratamiento de nulos (MCAR/MAR/MNAR), atípicos (IQR/MAD), normalización Min-Max, Z-Score y discretización.

### 3. Ejecutar los Modelos de Pronóstico Estadístico
```bash
python src/modelos_pronostico_e1.py
```
- Realiza descomposición aditiva de la serie horaria continua (337 periodos).
- Evalúa estacionariedad con prueba Dickey-Fuller aumentada (ADF).
- Entrena y compara 4 modelos (SES, Holt, Holt-Winters y ARIMA) en un conjunto de prueba no visto de 24 horas.
- Selecciona el modelo ganador por menor error (**Holt-Winters**, MAPE: $36.02\%$).
- Valida independencia de residuos con la prueba de **Ljung-Box** ($p = 0.9435$).
- Publica el pronóstico e intervalos de confianza al 95% en `data/oro/pronostico_e1.parquet`.

### 4. Ejecutar las Suites de Pruebas Unitarias Automatizadas
```bash
python -m pytest tests/ -v
```
Ejecuta 7 pruebas unitarias de contratos de datos, cuarentena, rangos válidos, completitud y cálculo de disponibilidad.

### 5. Medir la Fiabilidad y Disponibilidad del Flujo de Captura
```bash
python src/generar_bitacora_captura.py
```
Calcula métricas reales a partir de 7 días de bitácoras continuas:
- **Tasa de Éxito:** $92.86\%$
- **MTBF:** $80.54$ horas
- **MTTR:** $27.5$ minutos
- **Disponibilidad ($A$):** $99.43\%$ (Supera el objetivo $\ge 95.0\%$).

---

## 🏷️ Entregables y Etiquetas Git
- **`e0`:** Arranque del observatorio, propuesta metodológica formal, primer extractor ético y bitácoras PSP.
- **`e1`:** Pipeline Medallion completo, Puerta de Calidad Pandera con cuarentena, modelos de series de tiempo evaluados, Plan SQA IEEE 730, integración continua (CI) y relatoría de etapa.
