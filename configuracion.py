import pygame
from config import ANCHO, ALTO

class MenuConfiguracion:
    def __init__(self, datos_config):
        self.abierto = False
        self.datos = datos_config # Diccionario con "volumen", "modo_celular", "graficos_bajos"
        
        # Botón de engranaje (arriba a la derecha)
        self.btn_abrir = pygame.Rect(ANCHO - 50, 15, 35, 35)
        
        # Panel central
        self.panel = pygame.Rect(ANCHO//2 - 200, ALTO//2 - 150, 400, 300)
        
        # Botones internos del panel
        self.btn_modo = pygame.Rect(self.panel.x + 50, self.panel.y + 100, 300, 40)
        self.btn_graficos = pygame.Rect(self.panel.x + 50, self.panel.y + 160, 300, 40)
        self.btn_cerrar = pygame.Rect(self.panel.right - 40, self.panel.y + 10, 30, 30)
        
        # Barra de volumen
        self.barra_volumen = pygame.Rect(self.panel.x + 50, self.panel.y + 60, 300, 10)
        self.arrastrando_volumen = False
        
        pygame.font.init()
        self.f_titulo = pygame.font.SysFont(None, 34)
        self.f_texto = pygame.font.SysFont(None, 24)

    def procesar_eventos(self, evento):
        # Clic en el engranaje para abrir/cerrar
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if not self.abierto:
                if self.btn_abrir.collidepoint(evento.pos):
                    self.abierto = True
                    return True
            else:
                if self.btn_cerrar.collidepoint(evento.pos) or not self.panel.collidepoint(evento.pos):
                    self.abierto = False
                    return True
                
                # Clic en la barra de volumen
                if self.barra_volumen.inflate(10, 20).collidepoint(evento.pos):
                    self.arrastrando_volumen = True
                    self._actualizar_volumen(evento.pos[0])
                # Cambiar modo (PC / Celular)
                elif self.btn_modo.collidepoint(evento.pos):
                    self.datos["modo_celular"] = not self.datos["modo_celular"]
                # Cambiar gráficos
                elif self.btn_graficos.collidepoint(evento.pos):
                    self.datos["graficos_bajos"] = not self.datos["graficos_bajos"]
                    
        # Soltar el ratón
        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self.arrastrando_volumen = False
            
        # Arrastrar la barra de volumen
        if evento.type == pygame.MOUSEMOTION and self.arrastrando_volumen:
            self._actualizar_volumen(evento.pos[0])

        return False

    def _actualizar_volumen(self, mouse_x):
        # Calcula el volumen entre 0.0 y 1.0 según dónde esté el ratón
        x = max(self.barra_volumen.x, min(mouse_x, self.barra_volumen.right))
        self.datos["volumen"] = (x - self.barra_volumen.x) / self.barra_volumen.width

    def dibujar(self, pantalla, mouse_pos):
        # 1. Dibujar siempre el botón de engranaje
        pygame.draw.rect(pantalla, (200, 200, 200), self.btn_abrir, border_radius=8)
        pygame.draw.rect(pantalla, (50, 50, 50), self.btn_abrir, 2, border_radius=8)
        pygame.draw.circle(pantalla, (50, 50, 50), self.btn_abrir.center, 10, 2)
        pygame.draw.circle(pantalla, (50, 50, 50), self.btn_abrir.center, 4)

        if not self.abierto:
            return

        # 2. Panel oscuro
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        pantalla.blit(overlay, (0, 0))
        
        pygame.draw.rect(pantalla, (30, 35, 45), self.panel, border_radius=12)
        pygame.draw.rect(pantalla, (100, 150, 200), self.panel, 3, border_radius=12)

        # Título
        txt_titulo = self.f_titulo.render("Configuración", True, (255, 255, 255))
        pantalla.blit(txt_titulo, (self.panel.centerx - txt_titulo.get_width()//2, self.panel.y + 15))

        # Botón Cerrar (X)
        pygame.draw.rect(pantalla, (200, 50, 50), self.btn_cerrar, border_radius=6)
        txt_x = self.f_texto.render("X", True, (255, 255, 255))
        pantalla.blit(txt_x, (self.btn_cerrar.centerx - 5, self.btn_cerrar.centery - 10))

        # Volumen
        txt_vol = self.f_texto.render(f"Volumen: {int(self.datos['volumen'] * 100)}%", True, (200, 200, 200))
        pantalla.blit(txt_vol, (self.panel.x + 50, self.panel.y + 30))
        
        pygame.draw.rect(pantalla, (80, 80, 80), self.barra_volumen, border_radius=5)
        ancho_relleno = int(self.barra_volumen.width * self.datos["volumen"])
        if ancho_relleno > 0:
            pygame.draw.rect(pantalla, (100, 200, 100), (self.barra_volumen.x, self.barra_volumen.y, ancho_relleno, self.barra_volumen.height), border_radius=5)
        
        # Círculo en la barra
        pos_x = self.barra_volumen.x + ancho_relleno
        pygame.draw.circle(pantalla, (255, 255, 255), (pos_x, self.barra_volumen.centery), 8)

        # Modo PC / Celular
        texto_modo = "Modo Celular (Botones en pantalla)" if self.datos["modo_celular"] else "Modo Laptop (Teclado)"
        color_modo = (50, 150, 200) if self.datos["modo_celular"] else (100, 100, 100)
        pygame.draw.rect(pantalla, color_modo, self.btn_modo, border_radius=6)
        txt_modo = self.f_texto.render(texto_modo, True, (255, 255, 255))
        pantalla.blit(txt_modo, (self.btn_modo.centerx - txt_modo.get_width()//2, self.btn_modo.centery - 10))

        # Gráficos
        texto_graf = "Gráficos: Bajos (Rápido)" if self.datos["graficos_bajos"] else "Gráficos: Altos (Hermoso)"
        color_graf = (150, 50, 50) if self.datos["graficos_bajos"] else (150, 150, 50)
        pygame.draw.rect(pantalla, color_graf, self.btn_graficos, border_radius=6)
        txt_graf = self.f_texto.render(texto_graf, True, (255, 255, 255))
        pantalla.blit(txt_graf, (self.btn_graficos.centerx - txt_graf.get_width()//2, self.btn_graficos.centery - 10))