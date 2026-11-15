import json, os, sys

def obtener_ruta_archivo(nombre_archivo):
    if getattr(sys, 'frozen', False):
        carpeta = os.path.dirname(sys.executable)
    else:
        carpeta = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(carpeta, nombre_archivo)

ARCHIVO_PERFIL = obtener_ruta_archivo("perfil.json")
SLOT_ACTIVO = 0 # <--- Variable global que recordará tu ranura

# --- PERFIL DEL JUGADOR ---
def cargar_perfil():
    if os.path.exists(ARCHIVO_PERFIL):
        try:
            with open(ARCHIVO_PERFIL) as f:
                return json.load(f)
        except Exception: pass
    return {"nombre": "Invitado"}

def guardar_perfil(datos):
    with open(ARCHIVO_PERFIL, "w") as f:
        json.dump(datos, f)

# --- PARTIDAS (SLOTS) ---
def ruta_slot(slot_id):
    return obtener_ruta_archivo(f"guardado_{slot_id}.json")

def existe_slot(slot_id):
    return os.path.exists(ruta_slot(slot_id))

def info_slot(slot_id):
    if not existe_slot(slot_id): return None
    try:
        with open(ruta_slot(slot_id)) as f:
            d = json.load(f)
            return {"nivel": d.get("nivel", 1), "oro": d.get("oro", 0), "raza": d.get("raza", "humano")}
    except Exception:
        return None

def cargar(slot_id):
    global SLOT_ACTIVO
    SLOT_ACTIVO = slot_id # <--- Se guarda en la memoria global
    
    datos = {
        "oro": 0, "gemas": 0, "etapa": 1,
        "nivel": 1, "xp": 0, "puntos": 0,
        "poder": 0, "combate": 0, "vida": 0,
        "mision_activa": None, "mision_progreso": 0,
        "inventario": [None] * 36,
        "raza": "humano",
    }
    archivo = ruta_slot(slot_id)
    if os.path.exists(archivo):
        try:
            with open(archivo) as f:
                datos.update(json.load(f))
        except Exception: pass
    else:
        guardar(datos) # Ya no pide slot_id, usa el global
    return datos

def guardar(datos):
    with open(ruta_slot(SLOT_ACTIVO), "w") as f: # <--- Usa SLOT_ACTIVO
        json.dump(datos, f)

def eliminar_slot(slot_id):
    archivo = ruta_slot(slot_id)
    if os.path.exists(archivo):
        os.remove(archivo)