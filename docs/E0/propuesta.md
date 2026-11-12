# Propuesta Metodológica y Ficha de Arranque
## Observatorio de Rentabilidad para Repartidores y Conductores (Gig Economy)
### Proyecto Integrador: TRUSTED DATA LAB
**Institución:** Tecnológico Nacional de México — Instituto Tecnológico de Colima  
**Fecha:** Noviembre de 2026 | **Versión:** 1.2 (Etapa E0 - Arranque)  

---

## 1. Ficha del Observatorio

| Dimensión | Especificación |
|---|---|
| **Nombre del Observatorio** | Observatorio de Rentabilidad para Repartidores y Conductores (*Gig Economy Colima*) |
| **Sector Económico** | Plataformas digitales de transporte privado y entrega de paquetería/alimentos (Uber, DiDi, Mercado Libre Extra) |
| **Delimitación Geográfica** | Zona metropolitana conurbada de Colima y Villa de Álvarez, Colima, México (incluyendo subzonas críticas: Centro de Colima, Villa de Álvarez Norte, Tercer Anillo Comercial, Plaza Country/San Fernando y Corredor Tecnológico) |
| **Pregunta Central** | ¿En qué ventanas horarias, subzonas geográficas y condiciones meteorológicas se maximiza la ganancia neta por hora de un conductor/repartidor independiente al descontar los costos operativos de combustible y tiempos muertos? |
| **Cliente Objetivo Identificado** | Conductores y repartidores de plataformas digitales independientes agremiados o particulares en Colima y Villa de Álvarez |
| **Justificación de Disposición de Pago** | En la economía de plataformas, un repartidor promedio pierde entre 1.5 y 2.5 horas diarias esperando pedidos en zonas de baja demanda o consumiendo combustible en embotellamientos viales. Un reporte o tablero predictivo semanal con un costo simbólico de \$30 a \$50 MXN (o \$150 MXN mensuales en esquema cooperativo) le ahorra más de \$600 MXN mensuales en gasolina desperdiciada y aumenta su facturación neta entre un 20% y 35% al conectarse en momentos de alta tarifa dinámica. |

---

## 2. Evidencia de la Entrevista de Campo

Para fundamentar el problema con evidencia del sector productivo real, se realizó una entrevista presencial estructurada de 25 minutos el día **4 de noviembre de 2026** a un conductor y repartidor activo con más de 3 años de experiencia en la zona conurbada Colima–Villa de Álvarez.

### Ficha de la Entrevista
- **Entrevistado:** Jesús Manuel Ochoa (31 años, repartidor en motocicleta para Uber Eats/DiDi Food y conductor de automóvil en plataforma Uber).
- **Lugar:** Estacionamiento de Plaza Zentralia / Tercer Anillo Periférico, Colima.
- **Entrevistadores:** Fernando Benavides Manzo y Milagros Andrade.

### Cuestionario y Respuestas Registradas
1. **¿En qué horarios, días y zonas notas que la tarifa dinámica sube más o que no te das abasto con pedidos?**  
   *Respuesta:* "Los picos fuertes son los viernes y sábados de 7:30 p.m. a 11:30 p.m. en el Tercer Anillo y Avenida Felipe Sevilla del Río por los restaurantes de comida rápida y bares. En las mañanas hay un pequeño pico entre 7:00 a.m. y 9:00 a.m. de viajes a escuelas o oficinas, pero es más corto. En Villa de Álvarez, el movimiento de comida fuerte es casi todo en la tarde-noche."
2. **¿Cómo influyen las condiciones climáticas (lluvia, calor extremo) en tu decisión de salir a trabajar?**  
   *Respuesta:* "Cuando empieza a llover fuerte en Colima, muchos repartidores en moto se apagan por seguridad o porque se inundan calles como el Tercer Anillo o el Río Colima. Ahí las plataformas activan multiplicadores de tarifa de 1.8x hasta 2.5x. Los que traemos impermeable o andamos en auto ganamos el doble por viaje, pero el riesgo de accidentes y el tráfico pesado aumentan el consumo de gasolina."
3. **¿Qué diferencias críticas observas entre plataformas (Uber vs. DiDi vs. Mercado Libre Extra)?**  
   *Respuesta:* "Uber tiene más volumen constante de viajes y su aplicación calcula mejor las rutas, pero cobra comisiones más altas (a veces hasta el 28-30%). DiDi paga un poco mejor la tarifa por kilómetro en horas valle, pero la dinámica es más caprichosa. Mercado Libre Extra paga una tarifa fija por paquete o por ruta (entre \$600 y \$900 por turno matutino), lo que te da certidumbre pero te desgasta mucho el vehículo si la ruta te manda a colonias lejanas."
4. **¿Cuál es el costo oculto o gasto imprevisto que más erosiona tu ganancia neta?**  
   *Respuesta:* "La gasolina quemada en ralentí o esperando asignación. Si te quedas estacionado en una zona con aire acondicionado o dando vueltas buscando pedidos ('viajes en vacío'), la ganancia por hora se te cae de \$120 a menos de \$45 MXN la hora. Saber exactamente dónde pararse a esperar es la diferencia entre salir con dinero o salir tablas."
5. **Si existiera un tablero interactivo o reporte predictivo en tu celular que te dijera con 95% de confianza dónde y cuándo conectarte, ¿pagarías por él?**  
   *Respuesta:* "Sin dudarlo. Con que me ahorre medio tanque a la semana (\$200 pesos) o me ayude a agarrar dos viajes con tarifa dinámica alta de \$150 pesos en lugar de viajes mínimos de \$35 pesos, pagaría \$50 pesos a la semana con gusto. Muchos compañeros en los grupos de WhatsApp estarían interesados."

### Aprendizajes Clave de la Entrevista
- La tarifa bruta es un espejismo si no se modela el **gasto de combustible por kilómetro** y el **tiempo de espera inactivo**.
- El clima (precipitación y lluvia acumulada) actúa como un catalizador directo de la tarifa dinámica.
- La zonificación urbana requiere comparar polos comerciales (Tercer Anillo / San Fernando) contra zonas residenciales y suburbanas de Villa de Álvarez.

---

## 3. Preguntas Analíticas Cuantitativas del Observatorio

Para guiar las fases analíticas del proyecto integrador, se formularon tres preguntas cuantitativas medibles, cada una asociada a las técnicas que se desarrollarán en las siguientes entregas:

1. **Pregunta E1 (Pronóstico de Series de Tiempo):**  
   *¿Cuál es el volumen proyectado de viajes/entregas y el multiplicador de tarifa dinámica para las próximas 24 a 48 horas en la zona metropolitana de Colima-Villa de Álvarez en función de la estacionalidad horaria y las alertas de precipitación pluvial?*  
   - **Técnicas aplicadas:** Descomposición de series de tiempo, pruebas de estacionariedad Dickey-Fuller, modelos de Suavizamiento Exponencial Simple, Holt, Holt-Winters y modelos autorregresivos integrados de media móvil (ARIMA/SARIMA) seleccionados por criterio de mínimo error (MAE, RMSE, MAPE).
2. **Pregunta E2 (Diseño de Experimentos Factorial $2^3$):**  
   *¿Qué combinación de factores controlables (Plataforma: Uber vs. DiDi $\times$ Franja Horaria: Matutina vs. Nocturna $\times$ Tipo de Unidad/Estrategia de Espera: Punto Fijo vs. Patrullaje Activo) maximiza significativamente la ganancia neta por hora neta y minimiza el tiempo muerto entre servicios?*  
   - **Técnicas aplicadas:** Diseño experimental factorial completo $2^3$ con aleatorización de corridas, réplicas independientes, bloqueo por día de la semana y análisis de varianza (ANOVA) de dos vías con interacción.
3. **Pregunta E3 (Análisis Estadístico Multivariado):**  
   *¿Existen conglomerados o perfiles homogéneos diferenciables de rentabilidad entre las 5 subzonas urbanas de Colima y Villa de Álvarez al analizar simultáneamente el vector de respuestas $\{\text{ganancia neta}, \text{tarifa dinámica}, \text{distancia promedio}, \text{duración promedio}, \text{tiempo de espera}\}$?*  
   - **Técnicas aplicadas:** Vectores de medias multivariadas, distancias de Mahalanobis, pruebas de normalidad multivariada (Mardia / Henze-Zirkler), Análisis de Varianza Multivariado (MANOVA con Lambda de Wilks y Traza de Pillai) y Análisis de Componentes Principales (PCA) proyectado en biplots interpretables.

---

## 4. Plan de Recopilación de Datos y Gobernanza Ética

El observatorio opera bajo una arquitectura multifuente estricta, ética y legal con costo \$0:

```
+---------------------------------------------------------------------------------------+
|                                FUENTES DE DATOS CRUDA                                 |
+--------------------------------------------+------------------------------------------+
|  Fuente 1: Open-Meteo Weather API          |  Fuente 2: Telemetría de Movilidad Gig   |
|  - Método: API REST sin token (Open)       |  - Método: Extractor Ético Programado    |
|  - Frecuencia: Actualización horaria       |  - Frecuencia: Ingestión cada 6 horas    |
|  - Formato: JSON crudo                     |  - Formato: CSV crudo particionado       |
|  - Variables: Temp, Lluvia, Clima WMO      |  - Variables: Tarifa, Duración, Distancia|
+--------------------------------------------+------------------------------------------+
                                     |
                                     v
+---------------------------------------------------------------------------------------+
|                 CAPA BRONCE (data/bronze/): Inmutable, auditada                       |
+---------------------------------------------------------------------------------------+
```

### Detalle de Fuentes
1. **Fuente Meteorológica (Open-Meteo):**
   - **Endpoint:** `https://api.open-meteo.com/v1/forecast?latitude=19.2433&longitude=-103.7247&hourly=temperature_2m,rain,weathercode`
   - **Licencia:** Abierta para fines académicos y no comerciales bajo licencia *Open Database License (ODbL) / CC BY 4.0*.
   - **Políticas de acceso:** No requiere credenciales API; latencia promedio $< 250$ ms; se implementa un `User-Agent` explícito con datos de contacto del equipo estudiantil.
2. **Fuente de Movilidad Gig (Telemetría de Plataformas y Corredores Comerciales):**
   - **Estructura:** Registros transaccionales de viajes y entregas en Colima y Villa de Álvarez con datos de tarifa dinámica, tiempos de espera, distancias y comisiones.
   - **Análisis de `robots.txt` y términos de uso:** Se respeta la política de crawling y scraping ético:
     - Identificación honesta mediante `User-Agent: TDL-Observatorio/1.0 (proyecto academico; contacto: 23460507@colima.tecnm.mx)`.
     - Frecuencia controlada con intervalo de espera (*crawl delay*) mínimo de 1.5 a 2.0 segundos entre solicitudes sucesivas para prevenir saturación de servidores ajenos.
     - Retroceso exponencial (*exponential backoff*) ante códigos de respuesta HTTP 429 (Too Many Requests) o 5xx.
   - **Protección de Datos Personales (LFPDPPP):**
     - Principio de cero datos personales: **No se recolecta, procesa ni almacena ningún nombre, teléfono, placa vehicular, identificador de pasajero ni correo de personas físicas**. Si alguna telemetría contiene identificadores locales, estos se ofuscan o descartan en el punto de captura antes de ingresar a la Capa Bronce.

---

## 5. Serie Histórica de Arranque en Capa Bronce

Para dar cumplimiento inmediato a los requisitos de la Unidad 3 de Análisis Estadístico (que exige un mínimo de 36 periodos cronológicos continuos para el ajuste de pronósticos), se cuenta con:
- **Serie Climática Horaria:** 408 observaciones horarias continuas descargadas desde la API de Open-Meteo cubriendo 17 días continuos en la Capa Bronce (`data/bronze/clima_colima_raw.json`).
- **Serie de Movilidad Gig:** 450 transacciones crudas distribuidas en las 5 zonas metropolitanas (`data/bronze/gig_viajes_raw.csv`), garantizando una base empírica suficiente para el entrenamiento de modelos de series temporales y evaluación de calidad.

---

## 6. Sistema de Calidad (PSP) y Objetivos Medibles de Arranque

El observatorio no concibe la calidad como una revisión posterior, sino como un principio intrínseco del desarrollo de software y datos:

### Tres Objetivos de Calidad Cuantitativos del Sistema:
1. **Disponibilidad del Flujo de Captura:**  
   $$\text{Disponibilidad } (A) \ge 95.0\% \quad \text{en las ejecuciones automáticas programadas}.$$
2. **Fiabilidad Operativa (MTBF):**  
   $$\text{Tiempo Medio Entre Fallas } (MTBF) \ge 72 \text{ horas operativas continuas sin interrupción no programada}.$$
3. **Eficacia de la Puerta de Calidad (Cero Fugas a Capa Plata):**  
   $$100\% \text{ de registros corruptos, fuera de rango o con violaciones de catálogo detectados y enrutados a Cuarentena}.$$

### Bitácoras del Personal Software Process (PSP):
Se establecieron bitácoras individuales estandarizadas en la carpeta `calidad/` para ambos ingenieros:
- `defectos-fernando.csv` y `defectos-milagros.csv`: Clasificación de defectos bajo los 10 tipos oficiales de PSP (Datos, Interfaz, Lógica, Sintaxis, Documentación, etc.), indicando fase de inyección, fase de remoción y minutos invertidos en corrección.
- `tiempo-fernando.csv` y `tiempo-milagros.csv`: Registro de esfuerzo por fase (Plan, Diseño, Código, Compilación, Pruebas, Postmortem) con cálculo de tiempo neto e interrupciones.
- `bitacora_captura.csv`: Registro automático de cada ciclo de extracción programada (timestamp, estado HTTP, registros recolectados y tiempo de respuesta en milisegundos).
