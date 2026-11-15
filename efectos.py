import math, random, pygame

class Particulas:
    def __init__(self):
        self.lista = []

    def emitir(self, x, y, colores, cantidad=10, vel=3.0, vida=30, tam=5, gravedad=0.0):
        if len(self.lista) > 1000: return
        for _ in range(cantidad):
            ang = random.uniform(0, math.tau)
            v = random.uniform(0.3, 1.0) * vel
            duracion = random.randint(max(1, int(vida * 0.6)), vida)
            self.lista.append({
                "x": x, "y": y, "vx": math.cos(ang) * v, "vy": math.sin(ang) * v,
                "vida": duracion, "max": duracion, "tam": tam, "g": gravedad,
                "color": random.choice(colores),
            })

    def emitir_estela_fuego(self, x, y):
        if len(self.lista) > 1000: return
        for _ in range(2):
            self.lista.append({
                "x": x + random.randint(-8, 8), 
                "y": y + random.randint(-8, 8),
                "vx": random.uniform(-1.5, 1.5), 
                "vy": random.uniform(-2.0, 0.5),
                "vida": 12, "max": 12,
                "tam": 8, "g": -0.05,
                "color": random.choice([(255, 100, 0), (255, 200, 0), (200, 30, 0)]),
            })

    def emitir_aura_fuego(self, x, y):
        """Partículas de brasas que suben por el cuerpo."""
        if len(self.lista) > 1000: return
        self.lista.append({
            "x": x + random.randint(-20, 20), 
            "y": y + random.randint(-10, 30),
            "vx": random.uniform(-0.5, 0.5), 
            "vy": random.uniform(-1.0, -2.0),
            "vida": random.randint(15, 30), "max": 30,
            "tam": random.randint(2, 4), "g": -0.02,
            "color": random.choice([(255, 80, 0), (255, 150, 0), (200, 20, 20)]),
        })

    def emitir_polvo(self, x, y, cantidad=3):
        for _ in range(cantidad):
            self.lista.append({
                "x": x + random.randint(-10, 10), "y": y,
                "vx": random.uniform(-1, 1), "vy": random.uniform(-0.5, -1.5),
                "vida": 15, "max": 15,
                "tam": 3, "g": 0.05, "color": (200, 190, 170),
            })

    def actualizar(self):
        for p in self.lista:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += p["g"]
            p["vida"] -= 1
        self.lista = [p for p in self.lista if p["vida"] > 0]

    def dibujar(self, pantalla, cam_x):
        for p in self.lista:
            r = max(1, int(p["tam"] * (p["vida"] / p["max"])))
            pygame.draw.circle(pantalla, p["color"], (int(p["x"] - cam_x), int(p["y"])), r)