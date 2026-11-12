# Auditoría de Seguridad y Respaldo del Sistema de Información
## Observatorio de Rentabilidad para Repartidores (Gig Economy Colima)
### Entrega E1: Calidad en los Sistemas de Información (Mtra. Isis)

---

## 1. Búsqueda de Secretos en el Historial (Gitleaks)

En cumplimiento con la rúbrica de Calidad en SI (E1), se auditó la totalidad del historial de commits del repositorio en búsqueda de secretos expuestos, tokens de API o credenciales embebidas:

```bash
# Comando de auditoría de secretos
gitleaks detect --source . --verbose
```

### Resultados de la Auditoría:
- **Total de commits analizados:** Todos los commits desde `0dc73ba` hasta el presente.
- **Fugas de credenciales detectadas:** 0
- **Hallazgos abiertos:** 0
- **Regla aplicada:** Todas las fuentes utilizadas (Open-Meteo API) son de acceso público sin token privado. Para fuentes futuras con autenticación (E2), las llaves se gestionarán exclusivamente mediante **GitHub Secrets** y variables de entorno protegidas (`.env` incluido en `.gitignore`).

---

## 2. Auditoría de Vulnerabilidades en Dependencias (pip-audit)

Se ejecutó un escaneo de seguridad sobre las librerías instaladas en el entorno de producción:

```bash
pip-audit
```

### Resumen de Dependencias Clave:
| Paquete | Versión Evaluada | Estado de Vulnerabilidad (CVE) | Recomendación SQA |
|---|---|---|---|
| `pandas` | 3.0.5 | Sin vulnerabilidades conocidas | Mantener versión estable |
| `pandera` | 0.36.0 | Sin vulnerabilidades conocidas | Mantener contratos de datos activos |
| `pyarrow` | 26.0.0 | Sin vulnerabilidades conocidas | Optimizado para formato Parquet |
| `scipy` | 1.18.1 | Sin vulnerabilidades conocidas | Núcleo matemático seguro |
| `requests` | 2.34.2 | Sin vulnerabilidades conocidas | Uso con verificación SSL obligatoria |

**Resultado:** Cero vulnerabilidades críticas detectadas en el árbol de dependencias.

---

## 3. Principio de Menor Privilegio (Least Privilege)

- **Tokens de GitHub Actions:** Los flujos automatizados de CI y de extracción operan con permisos limitados a nivel de job (`contents: write` para actualización de datos y `contents: read` para ejecución de pruebas), evitando permisos administrativos globales.
- **Acceso a Datos:** La capa Bronce es de solo lectura para los módulos de transformación analítica; únicamente los extractores certificados tienen permiso de escritura sobre `data/bronze/`.

---

## 4. Política de Respaldo de la Capa Bronce (Data Backup)

Dado que la Capa Bronce representa la verdad inmutable del observatorio:
1. **Versionado Git LFS / Commits Atómicos:** Cada extracción exitosa de Open-Meteo y telemetría de movilidad se versiona cronológicamente en el repositorio.
2. **Respaldo Local Redundante:** Copias espejo de `data/bronze/` se sincronizan en almacenamiento seguro de Google Drive universitario (`G:\Mi unidad\Ferssssni\...`).
3. **Prueba de Recuperación:** Se realizó una prueba de restauración eliminando temporalmente un archivo de bronce y restaurándolo mediante `git checkout` y respaldo local sin pérdida de registros.
