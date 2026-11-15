# inventario.py
from items import ITEMS, es_stackeable, es_consumible

SLOTS_COLS = 6
SLOTS_FILAS = 6
SLOTS_TOTAL = SLOTS_COLS * SLOTS_FILAS


class Inventario:
    def __init__(self, datos):
        self.datos = datos
        # slots: lista de None o {"id": str, "cantidad": int}
        self.slots = [None] * SLOTS_TOTAL
        self._cargar()

    # ---------- Persistencia ----------
    def _cargar(self):
        guardado = self.datos.get("inventario", None)
        if isinstance(guardado, list) and len(guardado) == SLOTS_TOTAL:
            for i, s in enumerate(guardado):
                if s and "id" in s and "cantidad" in s:
                    self.slots[i] = {"id": s["id"],
                                     "cantidad": max(1, int(s["cantidad"]))}

    def guardar_en_datos(self):
        self.datos["inventario"] = [
            ({"id": s["id"], "cantidad": s["cantidad"]} if s else None)
            for s in self.slots
        ]

    # ---------- Agregar ----------
    def agregar(self, item_id, cantidad=1):
        """Intenta añadir. Devuelve la cantidad que NO pudo guardar."""
        if item_id not in ITEMS:
            return cantidad
        if es_stackeable(item_id):
            # Primero llenar stacks existentes
            for s in self.slots:
                if s and s["id"] == item_id:
                    s["cantidad"] += cantidad
                    self.guardar_en_datos()
                    return 0
            # Si no hay stack, buscar slot vacío
            for i, s in enumerate(self.slots):
                if s is None:
                    self.slots[i] = {"id": item_id, "cantidad": cantidad}
                    self.guardar_en_datos()
                    return 0
            return cantidad  # inventario lleno
        else:
            # No stackeable: un ítem por slot
            sobrante = cantidad
            for i, s in enumerate(self.slots):
                if s is None and sobrante > 0:
                    self.slots[i] = {"id": item_id, "cantidad": 1}
                    sobrante -= 1
            if sobrante != cantidad:
                self.guardar_en_datos()
            return sobrante

    # ---------- Mover ----------
    def mover(self, desde, hasta):
        """Mueve o intercambia entre slots. Con stacking si aplica."""
        if desde == hasta:
            return
        a = self.slots[desde]
        b = self.slots[hasta]
        if a is None:
            return
        # Si el destino tiene el mismo ítem stackeable, apilar
        if b and b["id"] == a["id"] and es_stackeable(a["id"]):
            b["cantidad"] += a["cantidad"]
            self.slots[desde] = None
        else:
            self.slots[desde] = b
            self.slots[hasta] = a
        self.guardar_en_datos()

    # ---------- Quitar ----------
    def quitar(self, slot_idx, cantidad=1):
        s = self.slots[slot_idx]
        if not s:
            return 0
        quitado = min(cantidad, s["cantidad"])
        s["cantidad"] -= quitado
        if s["cantidad"] <= 0:
            self.slots[slot_idx] = None
        self.guardar_en_datos()
        return quitado

    # ---------- Usar ----------
    def usar(self, slot_idx, jugador):
        """Devuelve True si el ítem fue consumido."""
        s = self.slots[slot_idx]
        if not s:
            return False
        item_id = s["id"]
        if not es_consumible(item_id):
            return False
        ok = jugador.usar_item(item_id)
        if ok:
            self.quitar(slot_idx, 1)
        return ok

    # ---------- Contar ----------
    def contar(self, item_id):
        return sum(s["cantidad"] for s in self.slots if s and s["id"] == item_id)