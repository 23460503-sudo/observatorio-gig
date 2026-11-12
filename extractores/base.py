"""
Extractor ético: respeta robots.txt, se identifica y no satura sitios.
Módulo base del Kit de Arranque del Proyecto Integrador TRUSTED DATA LAB.
"""
import time
import urllib.robotparser
from urllib.parse import urlparse
import requests

UA = "TDL-Observatorio/1.0 (proyecto academico; contacto: 23460507@colima.tecnm.mx)"

class ExtractorEtico:
    def __init__(self, pausa=1.5):
        self.pausa = pausa  # segundos mínimos entre peticiones al mismo dominio
        self.robots = {}
        self.ultimo = {}
        self.sesion = requests.Session()
        self.sesion.headers["User-Agent"] = UA

    def _reglas(self, url):
        p = urlparse(url)
        base = f"{p.scheme}://{p.netloc}"
        if base not in self.robots:
            rp = urllib.robotparser.RobotFileParser(base + "/robots.txt")
            try:
                rp.read()
            except Exception:
                pass
            self.robots[base] = rp
        return self.robots[base]

    def get(self, url, intentos=3):
        reglas = self._reglas(url)
        try:
            if not reglas.can_fetch(UA, url):
                raise PermissionError(f"robots.txt no permite el acceso a {url}")
        except Exception as e:
            if isinstance(e, PermissionError):
                raise
            # Si no hay robots.txt accesible, continuar con cautela

        dominio = urlparse(url).netloc
        crawl_delay = 0
        try:
            crawl_delay = reglas.crawl_delay(UA) or 0
        except Exception:
            pass
            
        pausa = max(self.pausa, crawl_delay)
        espera = pausa - (time.time() - self.ultimo.get(dominio, 0))
        if espera > 0:
            time.sleep(espera)

        for i in range(intentos):
            try:
                r = self.sesion.get(url, timeout=20)
                self.ultimo[dominio] = time.time()
                if r.status_code == 429 or r.status_code >= 500:
                    time.sleep(pausa * (2 ** i))  # espera exponencial ante saturación
                    continue
                r.raise_for_status()
                return r
            except requests.exceptions.RequestException as req_err:
                if i == intentos - 1:
                    raise RuntimeError(f"Sin respuesta válida de {url} tras {intentos} intentos: {req_err}")
                time.sleep(pausa * (2 ** i))
                
        raise RuntimeError(f"Sin respuesta válida de {url} tras {intentos} intentos")
