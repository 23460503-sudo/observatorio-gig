# Diccionario de Datos - Capa Oro
## Observatorio de Rentabilidad para Repartidores (Gig Economy Colima)

Este diccionario describe cada campo, tipo de dato, origen, unidad de medida y propósito analítico del dataset de la Capa Oro (`gig_observatorio_oro.parquet` y `gig_observatorio_serie_oro.parquet`).

---

### 1. Dataset Transaccional Enriquecido (`gig_observatorio_oro.parquet`)

| Nombre de Campo | Tipo | Origen | Descripción | Rango / Valores Permitidos | Regla de Negocio / Calidad |
|---|---|---|---|---|---|
| `id_registro` | String | Bronce (Gig) | Identificador único del viaje / entrega | Formato `REG-GIG-XXXX` | Único, no nulo |
| `fecha_hora` | DateTime | Bronce (Normalizado) | Fecha y hora exacta del registro | Timestamp local (America/Mexico_City) | No nulo, secuencial |
| `fecha_hora_hora` | DateTime | Bronce (Truncado) | Fecha y hora truncada a nivel hora para integración con clima | Timestamp `YYYY-MM-DD HH:00:00` | Llave foránea de unión con clima |
| `plataforma` | String (Categórico) | Bronce (Entity Resolution) | Plataforma de entrega o movilidad | `'Uber'`, `'DiDi'`, `'Mercado Libre Extra'` | Validado contra catálogo cerrado en Pandera |
| `zona` | String (Categórico) | Bronce | Zona geográfica del viaje | 5 zonas metropolitanas autorizadas | Pertenece a Colima o Villa de Álvarez |
| `municipio` | String (Categórico) | Bronce | Municipio correspondiente | `'Colima'`, `'Villa de Alvarez'` | Homologado en jerarquía conceptual |
| `estado` | String | Transformación Oro | Entidad federativa | `'Colima'` | Valor constante |
| `region_geografica` | String | Transformación Oro | Jerarquía compuesta para agregación | `"[municipio] - [zona]"` | Jerarquía conceptual de negocio |
| `latitud` | Float | Bronce | Latitud geográfica WGS84 | $[19.10, 19.40]$ | Validado por Pandera |
| `longitud` | Float | Bronce | Longitud geográfica WGS84 | $[-103.85, -103.60]$ | Validado por Pandera |
| `distancia_km` | Float | Plata (Imputado MCAR) | Distancia recorrida en kilómetros | $> 0.0$ km | Imputación por mediana por zona si faltaba por pérdida GPS |
| `distancia_km_minmax` | Float | Transformación Oro | Distancia escalada Min-Max | $[0.0, 1.0]$ | Normalización para dashboards |
| `duracion_min` | Float | Bronce / Plata | Tiempo de recorrido en minutos | $> 0.0$ min | Validado por Pandera |
| `duracion_min_minmax` | Float | Transformación Oro | Duración escalada Min-Max | $[0.0, 1.0]$ | Normalización analítica |
| `tarifa_dinamica` | Float | Bronce | Multiplicador de tarifa por demanda | $[1.00, 5.00]$ | Validado por Pandera contra anomalías |
| `tarifa_dinamica_zscore`| Float | Transformación Oro | Tarifa dinámica estandarizada | $\mu=0, \sigma=1$ | Para series de tiempo y modelos multivariados |
| `categoria_tarifa` | Categórico | Transformación Oro | Discretización por tramos de demanda | `'Base (1.0x)'`, `'Moderada (1.1x-1.4x)'`, `'Alta (1.5x-2.0x)'`, `'Dinamica Extrema (>2.0x)'` | Discretización por rangos de negocio |
| `turno_horario` | Categórico | Transformación Oro | Turno del día según franja horaria | `'Madrugada'`, `'Mañana'`, `'Tarde'`, `'Noche'` | Jerarquía conceptual temporal |
| `ganancia_bruta` | Float | Plata (Tratado MNAR) | Ganancia bruta antes de costos (MXN) | $> 0.0$ MXN | String crudo parseado y limpiado |
| `gasto_gasolina_estimado`| Float | Plata | Costo estimado de combustible (MXN) | $\ge 0.0$ MXN | Estimado a razón de \$2.85 MXN/km |
| `ganancia_neta` | Float | Plata | Ganancia final en el bolsillo (MXN) | $> 0.0$ MXN | $\text{ganancia\_bruta} - \text{gasto\_gasolina}$ |
| `ganancia_neta_zscore` | Float | Transformación Oro | Ganancia neta estandarizada | $\mu=0, \sigma=1$ | Variable objetivo centrada |
| `tiempo_espera_min` | Float | Plata (Imputado MAR) | Minutos de espera en asignación de pedido | $\ge 0.0$ min | Imputado condicionalmente a franja horaria |
| `tiempo_espera_min_minmax`| Float | Transformación Oro | Tiempo de espera escalado Min-Max | $[0.0, 1.0]$ | Métrica normalizada |
| `pedidos_entregados` | Entero | Bronce | Número de pedidos / paradas completadas | $[1, 10]$ | Conteo discreto |
| `temperatura_c` | Float | Bronce (Open-Meteo) | Temperatura ambiente horaria en °C | $[10.0, 48.0]^\circ\text{C}$ | Fuente externa integrada |
| `temperatura_c_zscore` | Float | Transformación Oro | Temperatura estandarizada | $\mu=0, \sigma=1$ | Preparación analítica |
| `lluvia_mm` | Float | Bronce (Open-Meteo) | Precipitación pluvial en milímetros | $\ge 0.0$ mm | Covariable meteorológica |
| `codigo_clima` | Entero | Bronce (Open-Meteo) | Código meteorológico estándar WMO | Códigos oficiales WMO | Categoría de tiempo presente |
| `z_score_robusto` | Float | Plata | Puntaje Z robusto (MAD) de ganancia | Decimal | $Z_{rob} = \frac{x - \text{mediana}}{1.4826 \times MAD}$ |
| `es_atipico_iqr` | Booleano | Plata | Flag por método Rango Intercuartílico | True / False | $Q_1 - 1.5 IQR$ o $Q_3 + 1.5 IQR$ |
| `es_atipico_robusto` | Booleano | Plata | Flag por método Z-Score Robusto | True / False | $|Z_{rob}| > 3.0$ |
| `flag_atipico_negocio` | Entero | Plata | Marca atípico real de alta rentabilidad | $0$ o $1$ | Atípico legítimo (no borrado, señalado) |

---

### 2. Dataset Agregado de Series Temporales (`gig_observatorio_serie_oro.parquet`)

Este dataset reduce la dimensionalidad transaccional y agrega a nivel de fecha/hora y zona, optimizado directamente para los modelos de series de tiempo (ARIMA, Holt-Winters) y análisis comparativo de grupos (MANOVA/ANOVA):

| Campo | Tipo | Descripción |
|---|---|---|
| `fecha_hora_hora` | DateTime | Marca temporal horaria continua |
| `zona` | Categórico | Zona de operación dentro de la zona conurbada |
| `municipio` | Categórico | Municipio sede (`Colima` o `Villa de Alvarez`) |
| `total_viajes` | Entero | Conteo de viajes/entregas completados en la hora |
| `ganancia_neta_promedio` | Float | Promedio de ganancia neta horaria (\$ MXN) |
| `ganancia_neta_mediana` | Float | Mediana robusta de ganancia neta horaria (\$ MXN) |
| `tarifa_dinamica_promedio` | Float | Promedio ponderado del multiplicador dinámico |
| `duracion_promedio_min` | Float | Tiempo medio de viaje en minutos |
| `distancia_promedio_km` | Float | Distancia media recorrida por entrega |
| `temperatura_promedio_c` | Float | Temperatura media horaria (°C) |
| `lluvia_acumulada_mm` | Float | Lluvia total acumulada en la hora (mm) |
| `viajes_alta_demanda` | Entero | Número de servicios con atípicos de alta demanda |
