import pygame, sys, random, platform
from config import *
from personajes import PERSONAJES
from guardado import cargar, guardar
from niveles import ganar_xp
from jugador import Jugador
from oleadas import Oleadas
from dragon import Dragon
from efectos import Particulas
from stats import PanelStats
from npc import NPC
from inventario import Inventario
from ui_inventario import UIInventario
import mundo
import castillo_interior
import casa_interior
import herreria_interior
import misiones
import ui
from pantalla_carga import PantallaCarga
from menu_inicio import MenuInicio
import guardado as gd
from controles_tactiles import ControlesTactiles
from configuracion import MenuConfiguracion

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption(TITULO)
reloj = pygame.time.Clock()

ES_MOVIL = platform.system() in ["Android", "iOS"]

datos_config = {
    "volumen": 0.5,
    "modo_celular": ES_MOVIL, 
    "graficos_bajos": False
}

# 1. PANTALLA DE CARGA
carga = PantallaCarga(pantalla, "Anime Multiverse")
while not carga.terminado:
    reloj.tick(FPS)
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
    carga.actualizar()
    carga.dibujar()
    pygame.display.flip()

# 2. MENÚ DE INICIO
menu = MenuInicio(pantalla)
slot_actual = None
menu_terminado = False

while not menu_terminado:
    reloj.tick(FPS)
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        
        resultado = menu.procesar_eventos(e)
        if resultado == "jugar":
            slot_actual = menu.slot_seleccionado
            gd.guardar_perfil(menu.perfil)
            menu_terminado = True
            
    menu.dibujar()
    pygame.display.flip()

# 3. INICIO DEL JUEGO REAL
datos = gd.cargar(slot_actual)
misiones.asegurar_campos(datos)

particulas = Particulas()
inventario = Inventario(datos)
jugador = Jugador(PERSONAJES["Oni"], datos, inventario, particulas)

if inventario.contar("espada_infernal") > 0: jugador.espada_equipada = True
if inventario.contar("armadura_infernal") > 0: jugador.armadura_equipada = True

oleadas = Oleadas(particulas)
dragon = Dragon(particulas)
ui_inv = UIInventario()
camara = mundo.Camara()
panel = PanelStats()
camara.ir_a(jugador.rect.centerx)

controles = ControlesTactiles(ANCHO, ALTO)
menu_config = MenuConfiguracion(datos_config)

npc_anciano = NPC(ANCHO // 2 - 50, nombre="Anciano", tipo="anciano")
npc_razas = NPC(ANCHO - 150, nombre="Maestro de Razas", tipo="anciano")
npc_herrero = NPC(ANCHO - 420, nombre="Herrero", tipo="herreria")
npc_comerciante = NPC(ANCHO - 650, nombre="Comerciante", tipo="comerciante")

ESCENA_MUNDO = "mundo"
ESCENA_CASTILLO = "castillo"
ESCENA_CASA = "casa"
ESCENA_HERRERIA = "herreria"
escena = ESCENA_MUNDO

fundido = 0.0
fundido_objetivo = 0.0
escena_pendiente = None
dragon_respawn_t = 0

menu_misiones_abierto = False
menu_herrero_abierto = False
menu_razas_abierto = False
menu_comerciante_abierto = False
mensaje_flotante = ""
mensaje_t = 0
ambient_t = 0

pygame.font.init()
# CAMBIO AQUÍ: Usamos Font(None, ...) en lugar de SysFont
fuente_msg = pygame.font.Font(None, 22)
fuente_menu = pygame.font.Font(None, 26)
fuente_titulo = pygame.font.Font(None, 34)
fuente_flotante = pygame.font.Font(None, 30)
fuente_boton = pygame.font.Font(None, 24)

COMERCIANTE_W, COMERCIANTE_H = 640, 460
COMERCIANTE_X = ANCHO // 2 - COMERCIANTE_W // 2
COMERCIANTE_Y = ALTO // 2 - COMERCIANTE_H // 2

COMERCIANTE_ITEMS = [
    ("corazon_dragon", "Corazón de dragón", (220, 30, 40), "corazon"),
    ("armadura_infernal", "Armadura infernal", (80, 30, 40), "armadura"),
    ("cuero", "Cuero", (150, 100, 60), "rect"),
    ("escama_dragon", "Escama de dragón", (190, 40, 50), "rombo"),
]

BTN_MISIONES = [
    pygame.Rect(ANCHO // 2 + 150, ALTO // 2 - 70 + i * 80, 100, 40) for i in range(2)
]
BTN_GIRAR_RAZAS = pygame.Rect(ANCHO // 2 - 100, ALTO // 2 + 50, 200, 50)

# Botones X para cerrar menús
BTN_CERRAR = {
    "misiones": pygame.Rect(ANCHO // 2 + 230, ALTO // 2 - 150, 30, 30),
    "herreria": pygame.Rect(ANCHO // 2 + 230, ALTO // 2 - 140, 30, 30),
    "razas": pygame.Rect(ANCHO // 2 + 210, ALTO // 2 - 130, 30, 30),
    "comerciante": pygame.Rect(COMERCIANTE_X + COMERCIANTE_W - 40, COMERCIANTE_Y + 10, 30, 30)
}

def boton_vender_rect(idx):
    bx = COMERCIANTE_X + COMERCIANTE_W - 190
    by = COMERCIANTE_Y + 100 + idx * 72 + 12
    return pygame.Rect(bx, by, 160, 36)

def boton_vender_todo_rect(idx):
    bx = COMERCIANTE_X + COMERCIANTE_W - 190
    by = COMERCIANTE_Y + 100 + idx * 72 + 50
    return pygame.Rect(bx, by, 160, 22)

def cambiar_escena(nueva):
    global fundido_objetivo, escena_pendiente
    fundido_objetivo = 1.0
    escena_pendiente = nueva

def aplicar_cambio_escena():
    global escena, escena_pendiente, fundido_objetivo
    global menu_misiones_abierto, menu_herrero_abierto, menu_razas_abierto, menu_comerciante_abierto

    if escena_pendiente is None: return
    escena_anterior = escena

    if escena_pendiente == ESCENA_CASTILLO:
        escena = ESCENA_CASTILLO
        jugador.limite_x = ANCHO
        jugador.teletransportar(220)
        dragon.reposicionar_para_interior()
        particulas.lista.clear()
    elif escena_pendiente == ESCENA_CASA:
        escena = ESCENA_CASA
        jugador.limite_x = ANCHO
        jugador.teletransportar(200)
        particulas.lista.clear()
        menu_misiones_abierto = False
        menu_razas_abierto = False
    elif escena_pendiente == ESCENA_HERRERIA:
        escena = ESCENA_HERRERIA
        jugador.limite_x = ANCHO
        jugador.teletransportar(200)
        particulas.lista.clear()
        menu_herrero_abierto = False
        menu_comerciante_abierto = False
    elif escena_pendiente == ESCENA_MUNDO:
        escena = ESCENA_MUNDO
        jugador.limite_x = MAPA_LARGO

        if escena_anterior == ESCENA_CASA: jugador.teletransportar(CASA_PUERTA_X - 60)
        elif escena_anterior == ESCENA_HERRERIA: jugador.teletransportar(HERRERIA_PUERTA_X - 60)
        else: jugador.teletransportar(PUERTA_X - 60)

        if dragon.vivo(): dragon.reposicionar_para_mundo()
        particulas.lista.clear()
        menu_misiones_abierto = False
        menu_herrero_abierto = False
        menu_razas_abierto = False
        menu_comerciante_abierto = False

    escena_pendiente = None
    fundido_objetivo = 0.0

def mostrar_mensaje(msg):
    global mensaje_flotante, mensaje_t
    mensaje_flotante = msg
    mensaje_t = 180

def vender_item_comerciante(item_id, cantidad=1):
    disponibles = inventario.contar(item_id)
    if disponibles <= 0: return 0
    if cantidad == "todo": cantidad = disponibles
    else: cantidad = min(cantidad, disponibles)
    if cantidad <= 0: return 0

    precio = PRECIOS_VENTA[item_id]
    total_gemas = precio * cantidad
    restantes = cantidad

    for i, s in enumerate(inventario.slots):
        if restantes <= 0: break
        if s and s["id"] == item_id:
            quitados = min(restantes, s["cantidad"])
            inventario.quitar(i, quitados)
            restantes -= quitados

    datos["gemas"] += total_gemas
    guardar(datos)
    return total_gemas

def dibujar_boton_x(pantalla, rect):
    pygame.draw.rect(pantalla, (200, 50, 50), rect, border_radius=6)
    pygame.draw.rect(pantalla, (50, 20, 20), rect, 2, border_radius=6)
    # Dibujar la X
    cx, cy = rect.center
    pygame.draw.line(pantalla, (255,255,255), (cx-8, cy-8), (cx+8, cy+8), 3)
    pygame.draw.line(pantalla, (255,255,255), (cx-8, cy+8), (cx+8, cy-8), 3)

def dibujar_menu_misiones(pantalla):
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    pantalla.blit(overlay, (0, 0))

    panel_w, panel_h = 560, 340
    px = ANCHO // 2 - panel_w // 2
    py = ALTO // 2 - panel_h // 2
    panel_rect = pygame.Rect(px, py, panel_w, panel_h)

    pygame.draw.rect(pantalla, (245, 235, 210), panel_rect, border_radius=12)
    pygame.draw.rect(pantalla, (60, 40, 20), panel_rect, 4, border_radius=12)

    titulo = fuente_titulo.render("Tablón de misiones", True, (60, 40, 20))
    pantalla.blit(titulo, (px + panel_w // 2 - titulo.get_width() // 2, py + 16))
    
    dibujar_boton_x(pantalla, BTN_CERRAR["misiones"])

    if misiones.puede_aceptar(datos):
        y = py + 90
        for i, (clave, m) in enumerate(misiones.MISIONES.items(), start=1):
            linea1 = fuente_menu.render(f"[{i}] {m['titulo']}", True, (40, 25, 15))
            linea2 = fuente_msg.render(f"Recompensa: {m['recompensa_oro']} oro | {m['recompensa_xp']} XP", True, (90, 60, 30))
            pantalla.blit(linea1, (px + 30, y))
            pantalla.blit(linea2, (px + 30, y + 26))
            
            btn = BTN_MISIONES[i-1]
            pygame.draw.rect(pantalla, (60, 160, 80), btn, border_radius=6)
            txt_aceptar = fuente_msg.render("Aceptar", True, (255, 255, 255))
            pantalla.blit(txt_aceptar, (btn.centerx - txt_aceptar.get_width()//2, btn.centery - txt_aceptar.get_height()//2))
            
            y += 80
    else:
        clave = datos["mision_activa"]
        m = misiones.MISIONES[clave]
        prog = datos["mision_progreso"]
        total = m["objetivo_total"]
        linea1 = fuente_menu.render(m["titulo"], True, (40, 25, 15))
        pantalla.blit(linea1, (px + 30, py + 90))
        progreso_txt = fuente_titulo.render(f"{prog} / {total}", True, (200, 30, 30) if prog >= total else (40, 80, 200))
        pantalla.blit(progreso_txt, (px + panel_w // 2 - progreso_txt.get_width() // 2, py + 140))
        if prog >= total: hint = fuente_menu.render("¡Completada! Habla con el anciano para cobrar.", True, (30, 140, 60))
        else: hint = fuente_msg.render("Progreso actual de la misión activa.", True, (90, 60, 30))
        pantalla.blit(hint, (px + panel_w // 2 - hint.get_width() // 2, py + 200))

def dibujar_menu_herreria(pantalla):
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    pantalla.blit(overlay, (0, 0))

    panel_w, panel_h = 560, 320
    px = ANCHO // 2 - panel_w // 2
    py = ALTO // 2 - panel_h // 2
    panel_rect = pygame.Rect(px, py, panel_w, panel_h)

    pygame.draw.rect(pantalla, (235, 220, 200), panel_rect, border_radius=12)
    pygame.draw.rect(pantalla, (50, 35, 25), panel_rect, 4, border_radius=12)

    titulo = fuente_titulo.render("Herrería", True, (50, 35, 25))
    pantalla.blit(titulo, (px + panel_w // 2 - titulo.get_width() // 2, py + 16))
    
    dibujar_boton_x(pantalla, BTN_CERRAR["herreria"])

    tiene = inventario.contar("espada_infernal") > 0
    corazones = inventario.contar("corazon_dragon")
    escamas = inventario.contar("escama_dragon")

    if tiene:
        txt1 = fuente_menu.render("Ya forjaste la Espada Infernal.", True, (30, 140, 60))
        pantalla.blit(txt1, (px + panel_w // 2 - txt1.get_width() // 2, py + 130))
        return

    txt1 = fuente_msg.render("¿Quieres craftear la Espada Infernal?", True, (40, 25, 15))
    pantalla.blit(txt1, (px + 30, py + 70))

    req_y = py + 110
    pantalla.blit(fuente_msg.render("Requisitos:", True, (60, 40, 20)), (px + 30, req_y))

    c_color = (30, 140, 60) if corazones >= ESPADA_INFER_CORAZONES else (200, 40, 40)
    pantalla.blit(fuente_menu.render(f"Corazones de dragón: {corazones}/{ESPADA_INFER_CORAZONES}", True, c_color), (px + 50, req_y + 30))

    e_color = (30, 140, 60) if escamas >= ESPADA_INFER_ESCAMAS else (200, 40, 40)
    pantalla.blit(fuente_menu.render(f"Escamas de dragón: {escamas}/{ESPADA_INFER_ESCAMAS}", True, e_color), (px + 50, req_y + 65))

    if corazones >= ESPADA_INFER_CORAZONES and escamas >= ESPADA_INFER_ESCAMAS:
        accion = fuente_titulo.render("Presiona [E] para forjar", True, (30, 140, 60))
    else:
        accion = fuente_msg.render("Te faltan materiales...", True, (200, 40, 40))
    pantalla.blit(accion, (px + panel_w // 2 - accion.get_width() // 2, py + 230))

def dibujar_menu_razas(pantalla):
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    pantalla.blit(overlay, (0, 0))

    panel_w, panel_h = 500, 350 # Más alto para el botón
    px = ANCHO // 2 - panel_w // 2
    py = ALTO // 2 - panel_h // 2
    panel_rect = pygame.Rect(px, py, panel_w, panel_h)

    pygame.draw.rect(pantalla, (240, 235, 250), panel_rect, border_radius=12)
    pygame.draw.rect(pantalla, (50, 40, 70), panel_rect, 4, border_radius=12)

    titulo = fuente_titulo.render("Maestro de Razas", True, (50, 40, 70))
    pantalla.blit(titulo, (px + panel_w // 2 - titulo.get_width() // 2, py + 20))
    
    dibujar_boton_x(pantalla, BTN_CERRAR["razas"])

    raza_actual = RAZAS[datos.get("raza", "humano")]["nombre"]
    pantalla.blit(fuente_menu.render(f"Raza actual: {raza_actual}", True, (80, 60, 100)), (px + panel_w // 2 - 80, py + 70))
    pantalla.blit(fuente_menu.render(f"Tus gemas: {datos['gemas']}", True, (200, 100, 200)), (px + panel_w // 2 - 60, py + 110))

    # Botón gigante de Girar
    color_btn = (30, 140, 60) if datos["gemas"] >= COSTO_GEMAS_RAZA else (150, 150, 150)
    pygame.draw.rect(pantalla, color_btn, BTN_GIRAR_RAZAS, border_radius=8)
    pygame.draw.rect(pantalla, (20, 70, 30), BTN_GIRAR_RAZAS, 2, border_radius=8)
    
    txt_girar = f"GIRAR ({COSTO_GEMAS_RAZA} Gemas)"
    render_girar = fuente_titulo.render(txt_girar, True, (255, 255, 255))
    pantalla.blit(render_girar, (BTN_GIRAR_RAZAS.centerx - render_girar.get_width()//2, BTN_GIRAR_RAZAS.centery - render_girar.get_height()//2))

def dibujar_icono_item(pantalla, item_id, rect, color):
    from items import ITEMS
    cx, cy = rect.center
    tam = int(rect.w * 0.6)
    info = ITEMS.get(item_id)
    forma = info["forma"] if info else "rect"
    borde = info["color_borde"] if info else (40, 30, 20)

    if forma == "rombo":
        pts = [(cx, cy - tam // 2), (cx + tam // 2, cy), (cx, cy + tam // 2), (cx - tam // 2, cy)]
        pygame.draw.polygon(pantalla, color, pts)
        pygame.draw.polygon(pantalla, borde, pts, 2)
    elif forma == "corazon":
        pygame.draw.circle(pantalla, color, (cx - tam // 4, cy - 2), tam // 3)
        pygame.draw.circle(pantalla, color, (cx + tam // 4, cy - 2), tam // 3)
        pts = [(cx - tam // 2 + 4, cy + 2), (cx + tam // 2 - 4, cy + 2), (cx, cy + tam // 2)]
        pygame.draw.polygon(pantalla, color, pts)
        pygame.draw.polygon(pantalla, borde, pts, 2)
    elif forma == "armadura":
        pts = [(cx - tam // 2, cy - tam // 2), (cx + tam // 2, cy - tam // 2), (cx + tam // 3, cy + tam // 2), (cx - tam // 3, cy + tam // 2)]
        pygame.draw.polygon(pantalla, color, pts)
        pygame.draw.polygon(pantalla, borde, pts, 2)
    else:
        r = pygame.Rect(0, 0, tam, tam)
        r.center = (cx, cy)
        pygame.draw.rect(pantalla, color, r)
        pygame.draw.rect(pantalla, borde, r, 2)

def dibujar_boton(pantalla, rect, texto, mouse_pos, activo=True, color_base=(60, 160, 80), color_hover=(90, 200, 110), color_off=(180, 180, 180)):
    color = color_off if not activo else (color_hover if rect.collidepoint(mouse_pos) else color_base)
    pygame.draw.rect(pantalla, color, rect, border_radius=6)
    pygame.draw.rect(pantalla, (30, 50, 30), rect, 2, border_radius=6)

    txt = fuente_boton.render(texto, True, (255, 255, 255))
    tx = rect.centerx - txt.get_width() // 2
    ty = rect.centery - txt.get_height() // 2
    pantalla.blit(fuente_boton.render(texto, True, (0, 0, 0)), (tx + 1, ty + 1))
    pantalla.blit(txt, (tx, ty))

def dibujar_menu_comerciante(pantalla, mouse_pos):
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    pantalla.blit(overlay, (0, 0))

    panel_rect = pygame.Rect(COMERCIANTE_X, COMERCIANTE_Y, COMERCIANTE_W, COMERCIANTE_H)
    pygame.draw.rect(pantalla, (235, 245, 220), panel_rect, border_radius=12)
    pygame.draw.rect(pantalla, (40, 80, 40), panel_rect, 4, border_radius=12)

    titulo = fuente_titulo.render("Comerciante", True, (40, 80, 40))
    pantalla.blit(titulo, (COMERCIANTE_X + COMERCIANTE_W // 2 - titulo.get_width() // 2, COMERCIANTE_Y + 16))
    
    dibujar_boton_x(pantalla, BTN_CERRAR["comerciante"])

    txt_gemas = fuente_menu.render(f"Tus gemas: {datos['gemas']}", True, (150, 80, 200))
    pantalla.blit(txt_gemas, (COMERCIANTE_X + COMERCIANTE_W // 2 - txt_gemas.get_width() // 2, COMERCIANTE_Y + 58))

    for idx, (item_id, nombre, color, _forma) in enumerate(COMERCIANTE_ITEMS):
        fila_y = COMERCIANTE_Y + 100 + idx * 72
        fila = pygame.Rect(COMERCIANTE_X + 20, fila_y, COMERCIANTE_W - 40, 64)
        pygame.draw.rect(pantalla, (250, 250, 240), fila, border_radius=8)
        pygame.draw.rect(pantalla, (120, 150, 120), fila, 2, border_radius=8)

        cuadro = pygame.Rect(COMERCIANTE_X + 30, fila_y + 8, 48, 48)
        dibujar_icono_item(pantalla, item_id, cuadro, color)
        pygame.draw.rect(pantalla, (60, 40, 20), cuadro, 2, border_radius=6)

        pantalla.blit(fuente_menu.render(nombre, True, (40, 60, 40)), (COMERCIANTE_X + 90, fila_y + 4))
        cantidad = inventario.contar(item_id)
        precio = PRECIOS_VENTA[item_id]
        pantalla.blit(fuente_msg.render(f"Tienes: {cantidad} · {precio} gemas c/u", True, (90, 90, 90)), (COMERCIANTE_X + 90, fila_y + 32))

        dibujar_boton(pantalla, boton_vender_rect(idx), f"Vender 1 (+{precio})", mouse_pos, activo=(cantidad > 0))
        dibujar_boton(pantalla, boton_vender_todo_rect(idx), f"Vender todo (+{precio * cantidad})", mouse_pos, activo=(cantidad > 0), color_base=(50, 130, 180), color_hover=(70, 170, 220))

def algo_bloquea_ui():
    return panel.abierto or ui_inv.abierto or menu_misiones_abierto or menu_herrero_abierto or menu_razas_abierto or menu_comerciante_abierto or menu_config.abierto

def click_menu_comerciante(pos):
    global menu_comerciante_abierto
    if not menu_comerciante_abierto: return False

    if BTN_CERRAR["comerciante"].collidepoint(pos):
        menu_comerciante_abierto = False
        return True

    for idx, (item_id, nombre, _, _) in enumerate(COMERCIANTE_ITEMS):
        if boton_vender_rect(idx).collidepoint(pos):
            if inventario.contar(item_id) > 0:
                mostrar_mensaje(f"Vendido 1 {nombre} (+{vender_item_comerciante(item_id, 1)} gemas)")
            return True
        if boton_vender_todo_rect(idx).collidepoint(pos):
            if inventario.contar(item_id) > 0:
                mostrar_mensaje(f"Vendido todo (+{vender_item_comerciante(item_id, 'todo')} gemas)")
            return True
    return True

def obtener_puede_transformar():
    raza = jugador.datos.get("raza")
    return raza in ["kitsune", "dragon", "demonio"]

# BUCLE PRINCIPAL
while True:
    reloj.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()

    teclas_reales = pygame.key.get_pressed()
    teclas_falsas = controles.obtener_teclas_falsas()
    
    clic_izquierdo_pc = pygame.mouse.get_pressed()[0] if not controles.mostrar else False
    clic_atacar = clic_izquierdo_pc or controles.atacar_click

    teclas_movimiento = {
        pygame.K_a: teclas_reales[pygame.K_a] or teclas_falsas[pygame.K_a],
        pygame.K_d: teclas_reales[pygame.K_d] or teclas_falsas[pygame.K_d],
        pygame.K_SPACE: teclas_reales[pygame.K_SPACE] or controles.saltar
    }

    if teclas_movimiento[pygame.K_SPACE] and not algo_bloquea_ui():
        jugador.saltar()

    # Interactuar en celular (botón E)
    interactuar_press = controles.interactuar_press

    if (teclas_reales[pygame.K_z] or controles.z_click) and not algo_bloquea_ui() and jugador.espada_equipada:
        objs = oleadas.enemigos if escena == ESCENA_MUNDO else (dragon.objetivos() if escena == ESCENA_CASTILLO else [])
        jugador.habilidad_z(objs)

    if controles.transformar_press and not algo_bloquea_ui():
        if jugador.datos.get("raza") == "kitsune":
            msg = jugador.toggle_transformacion_kitsune()
            if msg: mostrar_mensaje(msg)
        elif jugador.datos.get("raza") == "dragon":
            msg = jugador.toggle_transformacion_dragon()
            if msg: mostrar_mensaje(msg)
        elif jugador.datos.get("raza") == "demonio":
            msg = jugador.toggle_transformacion_demonio()
            if msg: mostrar_mensaje(msg)
        controles.transformar_press = False

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            guardar(datos)
            pygame.quit()
            sys.exit()

        if menu_config.procesar_eventos(e):
            continue

        controles.procesar_evento(e)

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                if ui_inv.abierto: ui_inv.abierto = False
                elif menu_misiones_abierto: menu_misiones_abierto = False
                elif menu_herrero_abierto: menu_herrero_abierto = False
                elif menu_razas_abierto: menu_razas_abierto = False
                elif menu_comerciante_abierto: menu_comerciante_abierto = False
                elif menu_config.abierto: menu_config.abierto = False
                else: panel.abierto = False

            if e.key == pygame.K_t and not algo_bloquea_ui():
                if jugador.datos.get("raza") == "kitsune":
                    msg = jugador.toggle_transformacion_kitsune()
                    if msg: mostrar_mensaje(msg)
                elif jugador.datos.get("raza") == "dragon":
                    msg = jugador.toggle_transformacion_dragon()
                    if msg: mostrar_mensaje(msg)
                elif jugador.datos.get("raza") == "demonio":
                    msg = jugador.toggle_transformacion_demonio()
                    if msg: mostrar_mensaje(msg)

            if e.key == pygame.K_e: interactuar_press = True
            
            # En PC, la E del teclado forja y sale
            if menu_herrero_abierto and e.key == pygame.K_e and inventario.contar("espada_infernal") == 0:
                if (inventario.contar("corazon_dragon") >= ESPADA_INFER_CORAZONES and inventario.contar("escama_dragon") >= ESPADA_INFER_ESCAMAS):
                    for _ in range(ESPADA_INFER_CORAZONES):
                        for i, s in enumerate(inventario.slots):
                            if s and s["id"] == "corazon_dragon":
                                inventario.quitar(i, 1)
                                break
                    for _ in range(ESPADA_INFER_ESCAMAS):
                        for i, s in enumerate(inventario.slots):
                            if s and s["id"] == "escama_dragon":
                                inventario.quitar(i, 1)
                                break
                    inventario.agregar("espada_infernal", 1)
                    mostrar_mensaje("¡Has forjado la Espada Infernal!")
                    guardar(datos)
                    menu_herrero_abierto = False

            if e.key == pygame.K_e and escena == ESCENA_CASA and not algo_bloquea_ui():
                interactuar_press = True

            if ui_inv.abierto: continue

            if e.key == pygame.K_w and not panel.abierto and fundido_objetivo == 0:
                interactuar_press = True

        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            # Clics para cerrar menús con [X]
            if menu_misiones_abierto and BTN_CERRAR["misiones"].collidepoint(e.pos):
                menu_misiones_abierto = False
                continue
            if menu_herrero_abierto and BTN_CERRAR["herreria"].collidepoint(e.pos):
                menu_herrero_abierto = False
                continue
            if menu_razas_abierto and BTN_CERRAR["razas"].collidepoint(e.pos):
                menu_razas_abierto = False
                continue

            if menu_misiones_abierto and misiones.puede_aceptar(datos):
                for i, (clave, m) in enumerate(misiones.MISIONES.items(), start=1):
                    if BTN_MISIONES[i-1].collidepoint(e.pos):
                        if misiones.aceptar(datos, clave):
                            mostrar_mensaje(f"Mision aceptada: {m['titulo']}")
                            menu_misiones_abierto = False
                        break

            if menu_razas_abierto and BTN_GIRAR_RAZAS.collidepoint(e.pos):
                if datos["gemas"] >= COSTO_GEMAS_RAZA:
                    datos["gemas"] -= COSTO_GEMAS_RAZA
                    opciones = [(k, v) for k, v in RAZAS.items() if v.get("prob", 0) > 0]
                    total_p = sum(v["prob"] for _, v in opciones)
                    if total_p > 0:
                        r = random.uniform(0, total_p)
                        acum = 0
                        nueva_raza = opciones[0][0]
                        for k, v in opciones:
                            acum += v["prob"]
                            if r <= acum:
                                nueva_raza = k
                                break
                    else: nueva_raza = "humano"

                    datos["raza"] = nueva_raza
                    jugador.vida = min(jugador.vida_max, jugador.vida + 20)
                    jugador.trans_activa = False
                    jugador.dragon_trans = False
                    jugador.demonio_trans = False
                    jugador.trans_cd = 0
                    jugador.dragon_trans_cd = 0
                    jugador.demonio_trans_cd = 0
                    jugador.huellas.clear()
                    jugador.bolas_fuego.clear()
                    jugador.bolas_infernales.clear()
                    mostrar_mensaje(f"¡Nueva Raza: {RAZAS[nueva_raza]['nombre']}!")
                    guardar(datos)
                    menu_razas_abierto = False

            if jugador.demonio_trans and not algo_bloquea_ui() and clic_atacar:
                if jugador.lanzar_bola_infernal(): pass 

            if menu_comerciante_abierto:
                click_menu_comerciante(e.pos)
                continue
            if ui_inv.abierto or ui_inv.boton.collidepoint(e.pos):
                ui_inv.click(e.pos, inventario, jugador)
            elif not menu_misiones_abierto and not menu_herrero_abierto and not menu_razas_abierto:
                panel.click(e.pos, datos, jugador)

        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if ui_inv.abierto:
                ui_inv.soltar(e.pos, inventario)

    # LÓGICA DE INTERACCIÓN (Puertas y NPCs)
    if interactuar_press and not algo_bloquea_ui():
        if escena == ESCENA_MUNDO:
            if jugador.cerca_de_puerta_casa(): cambiar_escena(ESCENA_CASA)
            elif jugador.cerca_de_puerta_herreria(): cambiar_escena(ESCENA_HERRERIA)
            elif jugador.cerca_de_puerta_exterior(): cambiar_escena(ESCENA_CASTILLO)
        elif escena == ESCENA_CASTILLO and jugador.cerca_de_puerta_interior(): cambiar_escena(ESCENA_MUNDO)
        elif escena == ESCENA_CASA and jugador.cerca_de_puerta_casa_interior(): cambiar_escena(ESCENA_MUNDO)
        elif escena == ESCENA_HERRERIA and jugador.cerca_de_puerta_herreria_interior(): cambiar_escena(ESCENA_MUNDO)
        elif escena == ESCENA_CASA:
            if npc_anciano.cerca(jugador):
                if misiones.completada(datos):
                    oro, xp = misiones.entregar(datos)
                    mostrar_mensaje(f"+{oro} oro +{xp} XP")
                else: menu_misiones_abierto = True
            elif npc_razas.cerca(jugador): menu_razas_abierto = True
        elif escena == ESCENA_HERRERIA:
            if not menu_herrero_abierto and not menu_comerciante_abierto:
                if npc_herrero.cerca(jugador): menu_herrero_abierto = True
                elif npc_comerciante.cerca(jugador): menu_comerciante_abierto = True

    interactuar_press = False # Resetear

    if fundido < fundido_objetivo:
        fundido = min(1.0, fundido + 0.08)
        if fundido >= 1.0 and escena_pendiente is not None: aplicar_cambio_escena()
    elif fundido > fundido_objetivo:
        fundido = max(0.0, fundido - 0.08)

    if mensaje_t > 0: mensaje_t -= 1

    if not algo_bloquea_ui():
        puede_atacar = not panel.mouse_encima(mouse_pos) and not ui_inv.mouse_encima(mouse_pos)

        if escena == ESCENA_MUNDO:
            jugador.actualizar(teclas_movimiento, oleadas.enemigos, puede_atacar, clic_atacar)
            oleadas.actualizar(jugador, datos, inventario)
            
            if not datos_config["graficos_bajos"]:
                particulas.actualizar()
                ambient_t += 1
                if ambient_t > 10:
                    particulas.emitir(camara.ox + random.randint(-100, ANCHO + 100), -20, [(50, 180, 50), (100, 200, 50)], 1, vel=1.5, vida=180, tam=4, gravedad=0.02)
                    ambient_t = 0

            if dragon_respawn_t > 0: dragon_respawn_t -= 1
            if jugador.rect.centerx > CASTILLO_X - 300: jugador.punto_reaparicion = CASTILLO_X - 300
            if jugador.vida <= 0:
                jugador.revivir()
                oleadas.reiniciar()

        elif escena == ESCENA_CASTILLO:
            jugador.actualizar(teclas_movimiento, dragon.objetivos(), puede_atacar, clic_atacar)
            dragon.actualizar(jugador, camara)
            
            if not datos_config["graficos_bajos"]:
                particulas.actualizar()
                ambient_t += 1
                if ambient_t > 15:
                    particulas.emitir(random.randint(0, ANCHO), ALTO, [(255, 100, 0), (200, 30, 0)], 1, vel=2, vida=100, tam=3, gravedad=-0.05)
                    ambient_t = 0
                    
            if dragon.recien_derrotado:
                dragon.recien_derrotado = False
                datos["oro"] += 300
                datos["gemas"] += 100
                ganar_xp(datos, 200)
                misiones.progreso(datos, "dragon", 1)
                if random.random() < 0.80: inventario.agregar("corazon_dragon", 1)
                if random.random() < 0.50: inventario.agregar("armadura_infernal", 1)
                if random.random() < 0.50: inventario.agregar("escama_dragon", random.randint(1, 50))
                guardar(datos)
                dragon_respawn_t = DRAGON_RESPAWN
            if jugador.vida <= 0:
                jugador.revivir()
                jugador.punto_reaparicion = PUERTA_X - 100
                jugador.limite_x = MAPA_LARGO
                dragon.reposicionar_para_mundo()
                particulas.lista.clear()
                cambiar_escena(ESCENA_MUNDO)

        elif escena == ESCENA_HERRERIA:
            jugador.actualizar(teclas_movimiento, [], puede_atacar, clic_atacar)
            if not datos_config["graficos_bajos"]:
                particulas.actualizar()
                ambient_t += 1
                if ambient_t > 10:
                    particulas.emitir(ANCHO - 150, SUELO - 100, [(255, 150, 0), (255, 200, 0)], 1, vel=2, vida=60, tam=2, gravedad=-0.08)
                    ambient_t = 0

        else:
            jugador.actualizar(teclas_movimiento, [], puede_atacar, clic_atacar)
            if not datos_config["graficos_bajos"]:
                particulas.actualizar()

    if escena == ESCENA_MUNDO: camara.seguir(jugador.rect.centerx)
    else:
        camara.ox = 0
        camara.temblor = 0

    t = pygame.time.get_ticks()

    if escena == ESCENA_MUNDO:
        mundo.dibujar_fondo(pantalla, camara.ox, jugador.cerca_de_puerta_exterior(), jugador.cerca_de_puerta_casa(), jugador.cerca_de_puerta_herreria())
        oleadas.dibujar(pantalla, camara.ox)
        jugador.dibujar(pantalla, camara.ox)
        if not datos_config["graficos_bajos"]: 
            particulas.dibujar(pantalla, camara.ox)

    elif escena == ESCENA_CASTILLO:
        castillo_interior.dibujar_interior(pantalla, t)
        castillo_interior.dibujar_puerta_salida_brillo(pantalla, jugador.cerca_de_puerta_interior(), t)
        dragon.dibujar(pantalla, 0)
        jugador.dibujar(pantalla, 0)
        if not datos_config["graficos_bajos"]:
            particulas.dibujar(pantalla, 0)
        if dragon_respawn_t > 0 and not dragon.vivo():
            msg = fuente_msg.render(f"El dragon reaparecera en {dragon_respawn_t // FPS}s", True, (200, 200, 255))
            pantalla.blit(msg, (ANCHO - msg.get_width() - 20, 20))

    elif escena == ESCENA_CASA:
        casa_interior.dibujar_interior(pantalla, t)
        casa_interior.dibujar_puerta_salida_brillo(pantalla, jugador.cerca_de_puerta_casa_interior(), t)
        npc_anciano.dibujar(pantalla, t)
        npc_razas.dibujar(pantalla, t)
        jugador.dibujar(pantalla, 0)
        if not datos_config["graficos_bajos"]:
            particulas.dibujar(pantalla, 0)

    elif escena == ESCENA_HERRERIA:
        herreria_interior.dibujar_interior(pantalla, t)
        herreria_interior.dibujar_puerta_salida_brillo(pantalla, jugador.cerca_de_puerta_herreria_interior(), t)
        npc_herrero.dibujar(pantalla, t)
        npc_comerciante.dibujar(pantalla, t)
        jugador.dibujar(pantalla, 0)
        if not datos_config["graficos_bajos"]:
            particulas.dibujar(pantalla, 0)

    controles.mostrar = datos_config["modo_celular"]
    if controles.mostrar:
        controles.dibujar(pantalla, jugador.espada_equipada, obtener_puede_transformar())

    ui.dibujar_hud(pantalla, datos, jugador)

    f_gemas = pygame.font.Font(None, 20)
    pantalla.blit(f_gemas.render(f"Gemas: {datos['gemas']}", True, (200, 100, 255)), (15, 145))

    if jugador.espada_equipada and not algo_bloquea_ui():
        f_z = pygame.font.Font(None, 20)
        txt_z = f_z.render("[Z] Fuego Listo", True, (255, 150, 50)) if jugador.z_cd <= 0 else f_z.render(f"[Z] {jugador.z_cd // FPS + 1}s", True, (150, 150, 150))
        pantalla.blit(txt_z, (15, 168))

    if jugador.datos.get("raza") == "kitsune":
        f_k = pygame.font.Font(None, 20)
        txt_k = f_k.render("[T] TRANSFORMADO (quitar)", True, (255, 160, 40)) if jugador.trans_activa else (f_k.render(f"[T] {jugador.trans_cd // FPS + 1}s", True, (150, 150, 150)) if jugador.trans_cd > 0 else f_k.render("[T] ¡Transformar!", True, (255, 200, 60)))
        pantalla.blit(txt_k, (15, 190))

    if jugador.datos.get("raza") == "dragon":
        f_d = pygame.font.Font(None, 20)
        txt_d = f_d.render("[T] DRAGÓN (quitar)", True, (255, 100, 40)) if jugador.dragon_trans else (f_d.render(f"[T] {jugador.dragon_trans_cd // FPS + 1}s", True, (150, 150, 150)) if jugador.dragon_trans_cd > 0 else f_d.render("[T] ¡Transformar Dragón!", True, (255, 160, 60)))
        pantalla.blit(txt_d, (15, 190))

    if jugador.datos.get("raza") == "demonio":
        f_dem = pygame.font.Font(None, 20)
        txt_dem = f_dem.render("[T] DEMONIO (quitar)", True, (255, 50, 150)) if jugador.demonio_trans else (f_dem.render(f"[T] {jugador.demonio_trans_cd // FPS + 1}s", True, (150, 150, 150)) if jugador.demonio_trans_cd > 0 else f_dem.render("[T] ¡Transformar Demonio!", True, (200, 100, 255)))
        pantalla.blit(txt_dem, (15, 190))

    if not menu_misiones_abierto and not menu_herrero_abierto and not menu_razas_abierto and not menu_comerciante_abierto and not menu_config.abierto:
        panel.dibujar(pantalla, datos, jugador)

    if menu_misiones_abierto: dibujar_menu_misiones(pantalla)
    if menu_herrero_abierto: dibujar_menu_herreria(pantalla)
    if menu_razas_abierto: dibujar_menu_razas(pantalla)
    if menu_comerciante_abierto: dibujar_menu_comerciante(pantalla, mouse_pos)

    ui_inv.dibujar(pantalla, inventario, jugador, mouse_pos)

    if mensaje_t > 0 and mensaje_flotante:
        alpha = min(255, mensaje_t * 4)
        txt = fuente_flotante.render(mensaje_flotante, True, (255, 240, 150))
        surf_txt = pygame.Surface(txt.get_size(), pygame.SRCALPHA)
        surf_txt.blit(fuente_flotante.render(mensaje_flotante, True, (0, 0, 0)), (1, 1))
        surf_txt.blit(txt, (0, 0))
        surf_txt.set_alpha(alpha)
        pantalla.blit(surf_txt, (ANCHO // 2 - txt.get_width() // 2, 90 - int((180 - mensaje_t) / 6)))

    menu_config.dibujar(pantalla, mouse_pos)

    if fundido > 0:
        negro = pygame.Surface((ANCHO, ALTO))
        negro.set_alpha(int(255 * fundido))
        pantalla.blit(negro, (0, 0))

    pygame.display.flip()