# Propuesta Metodológica y Ficha de Arranque
## Observatorio de Rentabilidad para Repartidores y Conductores (Gig Economy)
### Proyecto Integrador: TRUSTED DATA LAB
**Institución:** Tecnológico Nacional de México — Instituto Tecnológico de Colima  
**Fecha:** Noviembre de 2026 | **Versión:** 1.2 (Etapa E0 - Arranque)  
*Nota: Este documento también se encuentra en [`docs/E0/propuesta.md`](docs/E0/propuesta.md).*

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

---

## 3. Preguntas Analíticas Cuantitativas del Observatorio

1. **Pregunta E1 (Pronóstico de Series de Tiempo):**  
   *¿Cuál es el volumen proyectado de viajes/entregas y el multiplicador de tarifa dinámica para las próximas 24 a 48 horas en la zona metropolitana de Colima-Villa de Álvarez en función de la estacionalidad horaria y las alertas de precipitación pluvial?*  
2. **Pregunta E2 (Diseño de Experimentos Factorial $2^3$):**  
   *¿Qué combinación de factores controlables (Plataforma: Uber vs. DiDi $\times$ Franja Horaria: Matutina vs. Nocturna $\times$ Tipo de Unidad/Estrategia de Espera: Punto Fijo vs. Patrullaje Activo) maximiza significativamente la ganancia neta por hora neta y minimiza el tiempo muerto entre servicios?*  
3. **Pregunta E3 (Análisis Estadístico Multivariado):**  
   *¿Existen conglomerados o perfiles homogéneos diferenciables de rentabilidad entre las 5 subzonas urbanas de Colima y Villa de Álvarez al analizar simultáneamente el vector de respuestas $\{\text{ganancia neta}, \text{tarifa dinámica}, \text{distancia promedio}, \text{duración promedio}, \text{tiempo de espera}\}$?*  

---

## 4. Plan de Recopilación de Datos y Gobernanza Ética
- **Fuente 1 (Open-Meteo Weather API):** Temperatura, lluvia y código meteorológico WMO horario continuo bajo licencia libre ODbL.
- **Fuente 2 (Telemetría de Movilidad Gig):** Extractor ético (`extractores/base.py`) con pausas de cortesía, retroceso exponencial y respeto total a `robots.txt`.
- **Cero Datos Personales (LFPDPPP):** No se captura ni almacena ningún dato identificativo de personas físicas.

---

## 5. Serie Histórica de Arranque en Capa Bronce
- 408 observaciones horarias climáticas continuas en `data/bronze/clima_colima_raw.json`.
- 450 transacciones crudas de movilidad en `data/bronze/gig_viajes_raw.csv`.

---

## 6. Sistema de Calidad (PSP) y Objetivos Medibles de Arranque
1. **Disponibilidad de Captura ($A \ge 95.0\%$):** Medida en `calidad/bitacora_captura.csv` ($A = 99.43\%$).
2. **Fiabilidad Operativa ($MTBF \ge 72 \text{ h}$):** $MTBF = 80.54$ horas.
3. **Eficacia de Cuarentena ($100\%$):** Segregación total de datos no conformes a `data/cuarentena/`.
