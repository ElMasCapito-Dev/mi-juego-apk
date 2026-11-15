import pygame, math, random
from config import ANCHO, ALTO

class PantallaCarga:
    def __init__(self, pantalla, texto="Anime Multiverse"):
        self.pantalla = pantalla
        self.texto = texto
        self.t = 0
        self.progreso = 0.0
        self.terminado = False
        
        # Partículas de fondo
        self.particulas = []
        for _ in range(100):
            self.particulas.append({
                "x": random.randint(0, ANCHO),
                "y": random.randint(0, ALTO),
                "vel": random.uniform(0.5, 2.0),
                "tam": random.uniform(1, 3),
                "color": random.choice([(255, 200, 100), (200, 150, 255), (100, 200, 255)]),
                "angulo": random.uniform(0, math.tau)
            })
            
        pygame.font.init()
        # CAMBIO AQUÍ: Usamos Font(None, ...) en lugar de SysFont
        self.f_titulo = pygame.font.Font(None, 60)
        self.f_sub = pygame.font.Font(None, 24)
        
    def actualizar(self):
        self.t += 1
        if self.t < 180: # 3 segundos de carga
            self.progreso = self.t / 180.0
        else:
            self.progreso = 1.0
            self.terminado = True
            
        for p in self.particulas:
            p["y"] -= p["vel"]
            p["angulo"] += 0.05
            if p["y"] < 0:
                p["y"] = ALTO
                p["x"] = random.randint(0, ANCHO)

    def dibujar(self):
        # Fondo oscuro con degradado
        for y in range(ALTO):
            color = (int(10 + 20 * (y/ALTO)), int(5 + 10 * (y/ALTO)), int(20 + 30 * (y/ALTO)))
            pygame.draw.line(self.pantalla, color, (0, y), (ANCHO, y))
            
        # Partículas flotantes
        for p in self.particulas:
            r = p["tam"] + math.sin(p["angulo"]) * 0.5
            surf = pygame.Surface((int(r*4), int(r*4)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*p["color"], 150), (int(r*2), int(r*2)), int(r*2))
            pygame.draw.circle(surf, (255, 255, 255, 200), (int(r*2), int(r*2)), int(r))
            self.pantalla.blit(surf, (p["x"] - r*2, p["y"] - r*2))
            
        # Círculo mágico central
        cx, cy = ANCHO // 2, ALTO // 2 - 30
        radio = 80 + math.sin(self.t / 20) * 5
        
        # Halo de fondo
        halo = pygame.Surface((radio*4, radio*4), pygame.SRCALPHA)
        pygame.draw.circle(halo, (100, 200, 255, 30), (radio*2, radio*2), radio*1.5)
        pygame.draw.circle(halo, (255, 100, 255, 20), (radio*2, radio*2), radio*1.2)
        self.pantalla.blit(halo, (cx - radio*2, cy - radio*2))
        
        # Anillos giratorios
        for i in range(3):
            ang_rot = self.t * (0.02 + i * 0.01)
            pygame.draw.circle(self.pantalla, (100, 200, 255), (cx, cy), radio + i*15, 2)
            
            # Runas / puntos en el anillo
            for j in range(8):
                ang = ang_rot + j * (math.tau / 8)
                px = cx + math.cos(ang) * (radio + i*15)
                py = cy + math.sin(ang) * (radio + i*15)
                pygame.draw.circle(self.pantalla, (255, 255, 255), (int(px), int(py)), 3)
                
        # Nombre del juego (con resplandor)
        pulso = 1.0 + math.sin(self.t / 10) * 0.05
        txt_surf = self.f_titulo.render(self.texto, True, (255, 240, 200))
        # Efecto de brillo
        for offset in [(2,2), (-2,-2), (2,-2), (-2,2)]:
            brillo = self.f_titulo.render(self.texto, True, (255, 150, 50))
            brillo.set_alpha(100)
            self.pantalla.blit(brillo, (cx - txt_surf.get_width()//2 + offset[0], cy - radio - 100 + offset[1]))
        
        self.pantalla.blit(txt_surf, (cx - txt_surf.get_width()//2, cy - radio - 100))
        
        # Subtítulo
        sub = self.f_sub.render("Cargando el Multiverso...", True, (150, 200, 255))
        self.pantalla.blit(sub, (cx - sub.get_width()//2, cy + radio + 40))
        
        # Barra de carga
        barra_w = 400
        barra_h = 20
        bx = cx - barra_w // 2
        by = ALTO - 80
        
        # Fondo de la barra
        pygame.draw.rect(self.pantalla, (30, 30, 50), (bx, by, barra_w, barra_h), border_radius=10)
        pygame.draw.rect(self.pantalla, (100, 150, 200), (bx, by, barra_w, barra_h), 2, border_radius=10)
        
        # Progreso
        progreso_w = int(barra_w * self.progreso)
        if progreso_w > 0:
            color_barra = (100, 255, 150) if self.progreso >= 1.0 else (100, 200, 255)
            pygame.draw.rect(self.pantalla, color_barra, (bx, by, progreso_w, barra_h), border_radius=10)
            # Brillo interior
            pygame.draw.rect(self.pantalla, (255, 255, 255, 100), (bx, by, progreso_w, barra_h//2), border_radius=10)
            
        # Porcentaje
        porc = self.f_sub.render(f"{int(self.progreso * 100)}%", True, (255, 255, 255))
        self.pantalla.blit(porc, (cx - porc.get_width()//2, by - 30))