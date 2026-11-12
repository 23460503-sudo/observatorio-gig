# Plan de Aseguramiento de la Calidad del Software (SQA Plan)
## Observatorio de Rentabilidad para Repartidores (Gig Economy Colima)
### Proyecto Integrador: TRUSTED DATA LAB
**Estándar de Referencia:** IEEE Std 730-2014 (IEEE Standard for Software Quality Assurance Processes)  
**Fecha:** Noviembre de 2026 | **Versión:** 1.0 (Entrega E1)  

---

## 1. Propósito y Alcance

### 1.1 Propósito
Este Plan SQA establece las actividades sistemáticas, procedimientos, estándares de ingeniería, puertas de calidad y métricas objetivas necesarias para asegurar que el **Observatorio de Rentabilidad para Repartidores y Conductores (Gig Economy Colima)** cumpla cabalmente con los requerimientos funcionales, estadísticos y de confiabilidad de datos especificados para el Proyecto Integrador TRUSTED DATA LAB, sirviendo de base para la posterior certificación bajo las normas ISO/IEC 25010 e ISO/IEC 25012.

### 1.2 Alcance
El plan abarca la totalidad del ciclo de vida del producto:
- Ingestión automatizada multifuente hacia la **Capa Bronce** (`data/bronze/`).
- Homologación, resolución de conflictos y Puerta de Calidad Pandera hacia la **Capa Plata** (`data/plata/`) y **Cuarentena** (`data/cuarentena/`).
- Enriquecimiento analítico, estandarización y reducción hacia la **Capa Oro** (`data/oro/`).
- Modelado estadístico y pronóstico en Jupyter Notebooks (`laboratorio/`).
- Pipelines de Integración Continua (CI/CD) en GitHub Actions (`.github/workflows/`).
- Registros individuales de proceso PSP (`calidad/`).

---

## 2. Roles y Responsabilidades

| Rol SQA | Asignado a | Responsabilidades Principales | Criterio de Independencia |
|---|---|---|---|
| **Data Engineer Lead** | Fernando Benavides Manzo | Diseño de arquitectura Medallion, implementación de extractores éticos, resolución de esquemas y construcción del pipeline ETL. | Responde técnicamente ante auditorías del Mtro. Román; auditado en calidad por el Quality Lead. |
| **Data Statistician Lead** | Milagros Andrade | Caracterización de series temporales, diseño de modelos de pronóstico (ARIMA, Holt-Winters), validación de supuestos y pruebas de residuos. | Responde técnicamente ante auditorías del Mtro. Joel; auditada en calidad por el Quality Lead. |
| **Quality Assurance Lead (Rotativo E1/E2)** | Fernando Benavides / Milagros Andrade | Verificación independiente de la Puerta de Calidad Pandera, auditoría de bitácoras PSP, cálculo de fiabilidad/disponibilidad (MTBF, MTTR), monitoreo de cuarentena y ejecución de escaneos de seguridad. | En cada entrega uno asume el rol de revisor independiente del trabajo del compañero con listas de comprobación. |

---

## 3. Estándares, Prácticas, Convenciones y Métricas

### 3.1 Estándares de Codificación e Ingeniería
- **Lenguaje:** Python 3.11+ con tipado estático opcional (`typing`) y docstrings descriptivos.
- **Formateo y Linting:** Reglas PEP 8 supervisadas mediante `ruff` o `flake8`.
- **Estructura Modular:** Separación estricta entre capa de ingestión (`src/`), validación de esquemas (`src/puerta_calidad.py` / `pipeline_e1.py`), almacenamiento (`data/`) y experimentación (`laboratorio/`).

### 3.2 Métricas de Calidad de Producto y Datos
1. **Disponibilidad de Captura ($A$):**
   $$A = \frac{MTBF}{MTBF + MTTR} \times 100 \ge 95.0\%$$
2. **Completitud de Capa Oro (ISO/IEC 25012):**
   $$C = \left( 1 - \frac{\text{Valores Nulos no Justificados}}{\text{Total de Celdas Oro}} \right) \times 100 \ge 95.0\%$$
3. **Eficacia de Cuarentena:**
   $$100\% \text{ de registros que violan reglas de negocio segregados a cuarentena sin fugas a Plata}.$$
4. **Calidad de Pronóstico (Error de Prueba):**
   $$MAPE < 15.0\% \quad \text{en el horizonte de validación temporal}.$$

---

## 4. Revisiones y Auditorías

| Hito SQA | Frecuencia | Participantes | Entregable / Artefacto Revisado |
|---|---|---|---|
| **Revisión de Código y Puerta de Calidad** | Por commit / PR | Ambos integrantes | Validación cruzada con Pandera y ejecución de suites de `pytest`. |
| **Auditoría de Bitácoras PSP** | Semanal (Cierre de Etapa) | Quality Lead | Consistencia de tiempos netos (`tiempo-*.csv`) y clasificación de defectos (`defectos-*.csv`). |
| **Auditoría Cruzada Externa** | Etapa E2 | Equipo par asignado | Evaluación formal con listas de comprobación bajo ISO/IEC 25010 e ISO/IEC 25012. |

---

## 5. Estrategia de Pruebas (Testing)

El aseguramiento de la calidad del código y de los datos se implementa en tres niveles:
1. **Pruebas de Esquema y Contrato de Datos (Data Contract Testing):**
   - Ejecutadas en tiempo de ejecución por **Pandera** antes de escribir en disco.
   - Verifican tipos de datos, rangos numéricos de tarifas ($1.0 \le \text{tarifa} \le 5.0$), no negatividad de ganancias y catálogos cerrados de zonas y plataformas.
2. **Pruebas Unitarias Automatizadas (Unit Tests con Pytest):**
   - Archivo de suite: `tests/test_calidad_datos.py`.
   - Prueban de forma determinística la lógica de imputación de nulos (MCAR/MAR/MNAR), el algoritmo de detección de atípicos (IQR y MAD) y la segregación de cuarentena.
3. **Pruebas de Integración y Regresión en CI/CD:**
   - Flujo de GitHub Actions (`.github/workflows/ci.yml`) que se activa en cada `push` o `pull_request` a la rama `main`.
   - Un cambio que rompa una prueba unitaria o exponga secretos tiene prohibida la integración.

---

## 6. Reporte de Problemas y Acciones Correctivas (Defect Management)

El sistema formal de reporte y seguimiento de defectos del proyecto está constituido por las bitácoras individuales de PSP (`calidad/defectos-fernando.csv` y `calidad/defectos-milagros.csv`):
- **Ciclo de vida del defecto:** Inyección $\rightarrow$ Detección/Remoción $\rightarrow$ Corrección $\rightarrow$ Registro de tiempo invertido.
- **Clasificación estándar PSP:**
  1. Documentación
  2. Sintaxis
  3. Construcción
  4. Asignación
  5. Interfaz
  6. Verificación
  7. Datos
  8. Función
  9. Sistema
  10. Entorno
- **Acciones correctivas:** Ante cualquier defecto clasificado como crítico (que impida la ejecución del pipeline o corrompa datos), se aplica una reunión de causa raíz y se actualizan los casos de prueba automáticos para evitar su reaparición.

---

## 7. Herramientas, Técnicas y Metodologías

| Categoría | Herramienta / Tecnología | Propósito en el Aseguramiento |
|---|---|---|
| **Validación de Datos** | Pandera (Python) | Validación declarativa de esquemas y contratos de datos en tiempo real. |
| **Framework de Pruebas** | Pytest | Ejecución automatizada de pruebas unitarias y de aserción de calidad. |
| **Control de Versiones** | Git + GitHub | Trazabilidad completa de cambios, commits atómicos y etiquetado (`e0`, `e1`). |
| **Integración Continua** | GitHub Actions | Ejecución automática de pruebas, linters y validación de esquemas en la nube. |
| **Seguridad SQA** | Gitleaks + Pip-audit | Prevención de fuga de credenciales y escaneo de vulnerabilidades en dependencias. |
| **Proceso de Medición** | PSP (Personal Software Process) | Registro riguroso de tiempos de desarrollo y densidad de defectos. |

---

## 8. Gestión de Riesgos SQA

| Riesgo Identificado | Probabilidad | Impacto | Estrategia de Mitigación SQA |
|---|---|---|---|
| **Caída o bloqueo de la API de Open-Meteo** | Media | Alto | Mecanismo de reintentos exponenciales en el extractor ético y respaldo local inmutable en Capa Bronce. |
| **Corrupción de datos por valores atípicos absurdos** | Alta | Crítico | La Puerta de Calidad Pandera captura anomalías en el límite de entrada y las envía a Cuarentena con motivo documentado. |
| **Fuga de secretos o tokens al repositorio público** | Baja | Crítico | Escaneo de pre-commit y paso automatizado de `gitleaks` en el flujo de integración continua de GitHub Actions. |
| **Sobreajuste o residuos correlacionados en pronósticos** | Media | Alto | Separación obligatoria de datos de prueba no vistos (Train/Test) y prueba formal de Ljung-Box sobre residuos. |
