# Propuesta del Observatorio de Rentabilidad para Repartidores (Gig Economy)
# A. Ficha del Observatorio
 Nombre: Observatorio de Rentabilidad para Repartidores y Conductores
Sector Económico:Plataformas digitales de transporte privado y entrega de paquetería
Región:Zona metropolitana de Colima y Villa de Álvarez, Colima, México
Pregunta Detonadora: ¿En qué horarios, zonas geográficas y condiciones climáticas es más rentable conectarse para maximizar la ganancia neta por hora?
Cliente Potencial: Conductores y repartidores independientes de plataformas (Uber, DiDi, Mercado Libre Extra).

 B. Entrevista de Campo
1. ¿En qué horarios y zonas notas que la tarifa dinámica sube más? R: En horas pico de la tarde y fines de semana por la noche en zonas comerciales.
2. ¿Cómo afecta el clima a tu decisión de conectarte? R: La lluvia aumenta los pedidos pero vuelve el tráfico más lento.
3. ¿Qué diferencia notas entre plataformas? R: Uber tiene mayor volumen de viajes, pero Mercado Libre Extra paga una tarifa fija por ruta.
4. ¿Qué costo reduce más tu ganancia por hora? R: El consumo excesivo de gasolina en zonas de tráfico pesado.
5. ¿Qué dato clave necesitarías en un tablero interactivo? R: Mapas de calor en tiempo real con las mejores zonas por hora.

 C. Preguntas Analíticas
E1 (Variable a pronosticar):Tarifa dinámica promedio o cantidad de viajes/pedidos por hora.
E2 (Factores a experimentar):Plataforma (Uber vs. DiDi) x Turno (Mañana vs. Noche) x Día (Lunes a Domingo).
E3 (Grupos a comparar): Zona Colima Centro vs. Zona Villa de Álvarez considerando volumen de tráfico y clima (Open-Meteo).

D. Plan de Recopilación de Datos
Open-Meteo API:Datos de clima históricos y pronóstico (uso libre no comercial).
Portal de Tráfico / Movilidad: Scraping/API respetando términos del archivo `robots.txt`.