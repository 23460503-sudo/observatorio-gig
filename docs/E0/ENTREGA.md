# Entrega E0 · Observatorio de Rentabilidad para Repartidores (Gig Economy Colima)
Equipo: Fernando Benavides Manzo, Milagros Andrade · Etiqueta: e0 · Tablero: https://github.com/23460503-sudo/observatorio-gig

## Resumen en tres líneas
Se fundamentó el Observatorio de Rentabilidad para Repartidores mediante una entrevista de campo estructurada a un repartidor activo en Colima, identificando una clara disposición a pagar por certidumbre en tarifas dinámicas y ahorro de combustible.
Se consolidó la arquitectura Medallion multifuente con costo \$0 integrando la API de Open-Meteo y telemetría de movilidad de plataformas, asegurando más de 400 periodos horarios históricos en la Capa Bronce bajo estrictos principios de ética y legalidad.
Se formalizó el sistema de calidad PSP con bitácoras individuales de tiempo y defectos, bitácora de ejecuciones de captura activa en GitHub Actions y tres objetivos cuantitativos medibles de disponibilidad y fiabilidad.

## Ingeniería de Datos
| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
|---|---|---|
| **Plan de recopilación** | [`docs/E0/propuesta.md`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/docs/E0/propuesta.md#4-plan-de-recopilación-de-datos-y-gobernanza-ética) | Especificación técnica de 2 fuentes con formato, endpoints, latencias, análisis de `robots.txt`, User-Agent institucional y política de cero datos personales (LFPDPPP). |
| **Captura y serie histórica** | [`data/bronze/`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/data/bronze/) / [`src/bronce_extractor.py`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/src/bronce_extractor.py) | Dos fuentes activas en Capa Bronce: 408 observaciones horarias de clima y 450 transacciones crudas de movilidad en Colima y Villa de Álvarez ($> 36$ periodos requeridos). |
| **Automatización programada** | [`.github/workflows/extractor.yml`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/.github/workflows/extractor.yml) | Flujo de GitHub Actions con cron programado cada 6 horas (`0 */6 * * *`) y ejecución manual `workflow_dispatch`. |

## Análisis Estadístico
| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
|---|---|---|
| **Preguntas analíticas medibles** | [`docs/E0/propuesta.md`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/docs/E0/propuesta.md#3-preguntas-analíticas-cuantitativas-del-observatorio) | Tres preguntas formales alineadas a las técnicas del proyecto: E1 (Pronóstico de demanda y tarifa con series temporales), E2 (Experimento factorial $2^3$ de plataformas y turnos) y E3 (Análisis multivariado MANOVA/PCA entre 5 subzonas metropolitanas). |
| **Suficiencia de serie histórica** | [`data/bronze/clima_colima_raw.json`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/data/bronze/clima_colima_raw.json) | Serie cronológica con 408 periodos horarios continuos en Capa Bronce, cumpliendo con creces el umbral mínimo de 36 periodos para descomposición y pronóstico. |

## Calidad en los Sistemas de Información
| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
|---|---|---|
| **Objetivos de calidad medibles** | [`docs/E0/propuesta.md`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/docs/E0/propuesta.md#6-sistema-de-calidad-psp-y-objetivos-medibles-de-arranque) | Tres objetivos numéricos formalizados: Disponibilidad de captura $\ge 95\%$, MTBF $\ge 72$ horas operativas, y 100% de segregación de registros corruptos a cuarentena. |
| **Registros individuales PSP** | [`calidad/defectos-fernando.csv`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/calidad/defectos-fernando.csv) / [`calidad/defectos-milagros.csv`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/calidad/defectos-milagros.csv) | Bitácoras de defectos y de tiempos abiertas y activas por cada integrante siguiendo las fases y tipologías oficiales de PSP. |
| **Bitácora de captura activa** | [`calidad/bitacora_captura.csv`](file:///G:/Mi%20unidad/Ferssssni/IINF/Semestre/2026/2026-2/INGENIERIA%20DE%20DATOS/observatorio-gig/calidad/bitacora_captura.csv) | Registro de corridas continuas de extracción con timestamps, estado HTTP, latencias y conteos para alimentar el cálculo de fiabilidad en E1. |
