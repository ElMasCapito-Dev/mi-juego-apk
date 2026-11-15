import pygame, sys
import guardado as gd
from config import ANCHO, ALTO

pygame.font.init()
f_titulo = pygame.font.SysFont(None, 60)
f_texto = pygame.font.SysFont(None, 36)
f_boton = pygame.font.SysFont(None, 40)

class MenuInicio:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.estado = "perfil" # "perfil", "seleccion", "slots"
        self.perfil = gd.cargar_perfil()
        self.texto_activo = False
        self.slot_seleccionado = None
        
        # Cuadro de texto táctil para el nombre
        self.rect_input = pygame.Rect(ANCHO//2 - 200, ALTO//2 - 25, 400, 50)
        
        # Botones generales
        self.btn_continuar = pygame.Rect(ANCHO//2 - 100, ALTO//2 + 60, 200, 50)
        self.btn_nueva = pygame.Rect(ANCHO//2 - 220, ALTO//2, 200, 60)
        self.btn_cargar = pygame.Rect(ANCHO//2 + 20, ALTO//2, 200, 60)
        
        # Botones de los 3 slots
        self.btn_slots_jugar = [pygame.Rect(ANCHO//2 - 200, 150 + i*90, 250, 60) for i in range(3)]
        self.btn_slots_eliminar = [pygame.Rect(ANCHO//2 + 70, 150 + i*90, 130, 60) for i in range(3)]

    def _dibujar_fondo(self):
        self.pantalla.fill((20, 25, 40))
        for y in range(ALTO):
            color = (int(20 - 10*(y/ALTO)), int(25 - 10*(y/ALTO)), int(40 - 10*(y/ALTO)))
            pygame.draw.line(self.pantalla, color, (0, y), (ANCHO, y))

    def _dibujar_boton(self, rect, texto, color=(60, 160, 80), hover_color=(90, 200, 110)):
        mouse = pygame.mouse.get_pos()
        c = hover_color if rect.collidepoint(mouse) else color
        pygame.draw.rect(self.pantalla, c, rect, border_radius=10)
        pygame.draw.rect(self.pantalla, (255, 255, 255), rect, 2, border_radius=10)
        txt = f_boton.render(texto, True, (255, 255, 255))
        self.pantalla.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

    def procesar_eventos(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            # --- PANTALLA PERFIL ---
            if self.estado == "perfil":
                if self.rect_input.collidepoint(evento.pos):
                    self.texto_activo = True
                    pygame.key.start_text_input() # ABRE EL TECLADO EN CELULAR
                else:
                    self.texto_activo = False
                    pygame.key.stop_text_input()
                    
                if self.btn_continuar.collidepoint(evento.pos) and self.perfil["nombre"].strip():
                    self.estado = "seleccion"
                    pygame.key.stop_text_input()
                    self.texto_activo = False
            
            # --- PANTALLA SELECCION ---
            elif self.estado == "seleccion":
                if self.btn_nueva.collidepoint(evento.pos): self.estado = "slots"
                elif self.btn_cargar.collidepoint(evento.pos): self.estado = "slots"

            # --- PANTALLA SLOTS ---
            elif self.estado == "slots":
                for i in range(3):
                    if self.btn_slots_jugar[i].collidepoint(evento.pos):
                        if not gd.existe_slot(i):
                            gd.guardar(gd.cargar(i), i) # Crea partida nueva
                        self.slot_seleccionado = i
                        return "jugar" # Le dice al main que empiece
                    
                    if self.btn_slots_eliminar[i].collidepoint(evento.pos):
                        if gd.existe_slot(i):
                            gd.eliminar_slot(i)

        # --- ESCRIBIR TEXTO ---
        if evento.type == pygame.TEXTINPUT and self.texto_activo:
            if len(self.perfil["nombre"]) < 15:
                self.perfil["nombre"] += evento.text
        if evento.type == pygame.KEYDOWN and self.texto_activo:
            if evento.key == pygame.K_BACKSPACE:
                self.perfil["nombre"] = self.perfil["nombre"][:-1]
            elif evento.key == pygame.K_RETURN:
                self.texto_activo = False
                pygame.key.stop_text_input()
        
        return None

    def dibujar(self):
        self._dibujar_fondo()

        if self.estado == "perfil":
            titulo = f_titulo.render("Tu Nombre de Cuenta", True, (255, 255, 255))
            self.pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 100))
            
            sub = f_texto.render("(Puedes cambiarlo cuando quieras)", True, (150, 150, 150))
            self.pantalla.blit(sub, (ANCHO//2 - sub.get_width()//2, 150))

            # Cuadro de texto
            color_borde = (100, 200, 255) if self.texto_activo else (100, 100, 100)
            pygame.draw.rect(self.pantalla, (40, 40, 50), self.rect_input, border_radius=8)
            pygame.draw.rect(self.pantalla, color_borde, self.rect_input, 3, border_radius=8)
            
            txt_nombre = f_boton.render(self.perfil["nombre"], True, (255, 255, 255))
            self.pantalla.blit(txt_nombre, (self.rect_input.x + 10, self.rect_input.centery - txt_nombre.get_height()//2))
            
            if self.texto_activo and pygame.time.get_ticks() % 1000 < 500:
                pygame.draw.line(self.pantalla, (255, 255, 255), 
                                 (self.rect_input.x + 15 + txt_nombre.get_width(), self.rect_input.y + 10),
                                 (self.rect_input.x + 15 + txt_nombre.get_width(), self.rect_input.bottom - 10), 2)

            self._dibujar_boton(self.btn_continuar, "Continuar", (50, 120, 200), (70, 150, 230))

        elif self.estado == "seleccion":
            titulo = f_titulo.render("¿Qué quieres hacer?", True, (255, 255, 255))
            self.pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 150))
            
            self._dibujar_boton(self.btn_nueva, "Nueva Partida", (60, 160, 80), (90, 200, 110))
            self._dibujar_boton(self.btn_cargar, "Cargar Partida", (50, 120, 200), (70, 150, 230))

        elif self.estado == "slots":
            titulo = f_titulo.render("Tus Partidas (Máx 3)", True, (255, 255, 255))
            self.pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 60))

            for i in range(3):
                info = gd.info_slot(i)
                
                # Fondo de la ranura
                rect_fondo = pygame.Rect(ANCHO//2 - 220, 140 + i*90, 440, 70)
                pygame.draw.rect(self.pantalla, (30, 35, 45), rect_fondo, border_radius=10)
                
                if info:
                    texto_slot = f"Mundo {i+1}: Nivel {info['nivel']} ({info['raza'].capitalize()})"
                    self._dibujar_boton(self.btn_slots_jugar[i], texto_slot, (50, 120, 200))
                    self._dibujar_boton(self.btn_slots_eliminar[i], "Borrar", (200, 60, 60), (230, 80, 80))
                else:
                    self._dibujar_boton(self.btn_slots_jugar[i], f"Mundo {i+1}: Vacío (Crear)", (60, 160, 80))