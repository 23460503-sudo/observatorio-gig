import os, urllib.request, json 
LAT, LON = "19.2433", "-103.7247" 
URL = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=temperature_2m,rain,weathercode&forecast_days=3" 
os.makedirs("data/bronze", exist_ok=True) 
try: 
    with urllib.request.urlopen(URL) as r: data = json.loads(r.read().decode()) 
    with open("data/bronze/clima_colima_raw.json", "w") as f: json.dump(data, f, indent=4) 
    print("Datos guardados con exito (36 periodos+)") 
except Exception as e: print(e) 
