"""
Generador y extractor de Capa Bronce para el Observatorio Gig Economy (Colima - Villa de Álvarez).
Genera datos crudos multifuente respetando el formato Bronze de la arquitectura Medallion:
1. Clima (Open-Meteo)
2. Viajes y entregas de repartidores/conductores (Uber, DiDi, Mercado Libre Extra)
Incluye imperfecciones realistas (MCAR, MAR, MNAR, atípicos, ruidos y casos para cuarentena).
"""
import os
import json
import random
import datetime
import urllib.request
import pandas as pd
import numpy as np

def extraer_clima_open_meteo(dias_historicos=14):
    """Descarga o genera serie climatica horaria para Colima (19.2433, -103.7247)."""
    os.makedirs("data/bronze", exist_ok=True)
    lat, lon = "19.2433", "-103.7247"
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,rain,weathercode&past_days={dias_historicos}&forecast_days=3"
    
    data = None
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TDL-Observatorio/1.0 (contacto: 23460507@colima.tecnm.mx)'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            with open("data/bronze/clima_colima_raw.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            print(f"[OK] Clima descargado exitosamente: {len(data['hourly']['time'])} periodos horarios.")
    except Exception as e:
        print(f"[AVISO] No se pudo conectar a Open-Meteo en vivo ({e}). Verificando archivo local existente...")
        if os.path.exists("data/bronze/clima_colima_raw.json"):
            with open("data/bronze/clima_colima_raw.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            print("[OK] Utilizando clima local existente.")
    return data

def generar_datos_crudos_gig(num_registros=450, semilla=42):
    """
    Genera el dataset crudo de viajes y entregas de Gig Economy en Colima y Villa de Álvarez.
    Introduce intencionalmente ruidos, desformatos y registros para probar la cuarentena.
    """
    random.seed(semilla)
    np.random.seed(semilla)
    
    zonas = [
        ("Colima Centro", 19.2433, -103.7247, "Colima"),
        ("Villa de Álvarez Norte", 19.2680, -103.7380, "Villa de Alvarez"),
        ("Tercer Anillo Comercial", 19.2610, -103.7120, "Colima"),
        ("Plaza Country / San Fernando", 19.2520, -103.7180, "Colima"),
        ("Avenida Tecnologico", 19.2630, -103.7420, "Villa de Alvarez")
    ]
    
    plataformas_base = ["Uber", "DiDi", "Mercado Libre Extra"]
    plataformas_con_ruido = ["Uber", "uber", "UBER", "DiDi", "didi", "DIDI", "Mercado Libre Extra", "ML_Extra", "Plataforma_Fantasma"]
    
    registros = []
    fecha_inicio = datetime.datetime(2026, 10, 26, 6, 0)
    
    for i in range(1, num_registros + 1):
        # Seleccion de tiempo cronologico ascendente con pequenas variaciones
        delta_min = int(i * 45 + random.randint(-15, 25))
        fecha_registro = fecha_inicio + datetime.timedelta(minutes=delta_min)
        
        # Formatos de fecha heterogeneos (para probar la resolucion de formatos en plata)
        fmt_choice = random.random()
        if fmt_choice < 0.70:
            fecha_str = fecha_registro.strftime("%Y-%m-%d %H:%M:%S")
        elif fmt_choice < 0.90:
            fecha_str = fecha_registro.strftime("%d/%m/%Y %H:%M")
        else:
            fecha_str = fecha_registro.isoformat()
            
        zona_info = random.choice(zonas)
        zona_nombre = zona_info[0]
        lat, lon = zona_info[1], zona_info[2]
        municipio = zona_info[3]
        
        hora = fecha_registro.hour
        es_fin_semana = fecha_registro.weekday() >= 4  # Vie, Sab, Dom
        
        # Dinamica y factores de negocio
        es_hora_pico = (13 <= hora <= 15) or (19 <= hora <= 22)
        if es_hora_pico and es_fin_semana:
            tarifa_dinamica = round(random.uniform(1.6, 2.8), 2)
        elif es_hora_pico:
            tarifa_dinamica = round(random.uniform(1.3, 1.9), 2)
        else:
            tarifa_dinamica = round(random.uniform(1.0, 1.25), 2)
            
        distancia = round(random.uniform(1.5, 14.0), 2)
        duracion = round(distancia * random.uniform(2.8, 4.5) + random.uniform(3, 10), 1)
        
        # Ganancia neta calculada con comision de plataforma y gasto de combustible
        tarifa_base_km = 12.50
        ganancia_bruta = round((distancia * tarifa_base_km * tarifa_dinamica) + random.uniform(15, 30), 2)
        costo_gasolina = round(distancia * 2.85, 2)
        
        # Formato de dinero heterogeneo (strings con $, MXN, espacios)
        if random.random() < 0.4:
            ganancia_str = f"${ganancia_bruta:.2f}"
        elif random.random() < 0.7:
            ganancia_str = f"$ {ganancia_bruta:.2f} MXN"
        else:
            ganancia_str = str(ganancia_bruta)
            
        plataforma = random.choice(plataformas_con_ruido)
        
        # Introduccion de mecanismos de datos faltantes:
        # 1. MCAR: Faltante de distancia aleatorio por falla de sensor GPS (3% de casos)
        dist_val = f"{distancia} km"
        if random.random() < 0.035:
            dist_val = None
            
        # 2. MAR: Tiempo de espera faltante condicionado al turno de noche/madrugada
        tiempo_espera = round(random.uniform(2.0, 18.0), 1)
        if hora < 7 and random.random() < 0.40:
            tiempo_espera = None  # MAR condicionado a la hora
            
        # 3. MNAR: Ganancia neta no registrada por cancelacion del viaje
        if random.random() < 0.02:
            ganancia_str = None  # MNAR (el conductor cancelo por baja tarifa)
            
        pedidos = random.randint(1, 3)
        
        # Casos intencionales para probar Puerta de Calidad y Cuarentena (aprox 12 registros)
        if i in [15, 65]:
            tarifa_dinamica = 9.99  # Regla rota: tarifa absurda > 5.0
        if i in [35, 120]:
            ganancia_str = "$-180.00"  # Regla rota: ganancia neta negativa
        if i in [75]:
            duracion = -15.0  # Regla rota: duracion negativa
        if i in [140, 210]:
            plataforma = "Servicio_Ilegal_App"  # Regla rota: plataforma fuera de catalogo permitido
        if i in [180]:
            zona_nombre = "Zona Desconocida Extranjera"
            lat = 48.8566  # Coordenada en Paris, fuera de Colima
            
        registros.append({
            "id_registro": f"REG-GIG-{i:04d}",
            "fecha_hora_captura": fecha_str,
            "plataforma": plataforma,
            "zona": zona_nombre,
            "latitud": lat,
            "longitud": lon,
            "municipio": municipio,
            "distancia_raw": dist_val,
            "duracion_min_raw": duracion,
            "tarifa_dinamica": tarifa_dinamica,
            "ganancia_raw": ganancia_str,
            "gasto_gasolina_estimado": costo_gasolina,
            "tiempo_espera_min": tiempo_espera,
            "pedidos_entregados": pedidos
        })
        
    df = pd.DataFrame(registros)
    os.makedirs("data/bronze", exist_ok=True)
    ruta_csv = "data/bronze/gig_viajes_raw.csv"
    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    print(f"[OK] Capa Bronce Gig generada: {len(df)} registros en {ruta_csv}")
    return df

if __name__ == "__main__":
    extraer_clima_open_meteo()
    generar_datos_crudos_gig()
