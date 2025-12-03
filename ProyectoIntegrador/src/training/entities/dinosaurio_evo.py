from ProyectoIntegrador.src.settings import SUELO_Y, UMBRAL_SALTO
from ProyectoIntegrador.src.entities.dinosaurio import Dinosaurio
from ProyectoIntegrador.src.training.modelo import crear_modelo, predecir_accion

class DinosaurioEvo(Dinosaurio):
    def __init__(self, modelo=None):
        super().__init__()
        self.cerebro = modelo if modelo is not None else crear_modelo()

    def update(self, obstaculos=None, vel_mundo=None):
        super().update()
        self.pensar(obstaculos, vel_mundo)

    def pensar(self, obstaculos, vel_mundo):
        obs_siguiente = None
        for obs in obstaculos:
            if obs.rect.right > self.rect.left:
                obs_siguiente = obs
                break

        if obs_siguiente:
            # Las 6 variables para la Red Neuronal
            inputs = [
                (SUELO_Y - self.y) / 100.0,  # x1
                (obs_siguiente.rect.x - self.rect.right) / 800.0,  # x2
                obs_siguiente.rect.width / 100.0,  # x3
                obs_siguiente.rect.height / 100.0,  # x4
                self.vel_y / 20.0,  # x5
                vel_mundo / 20.0  # x6
            ]

            # Usar Keras para decidir
            decision = predecir_accion(self.cerebro, inputs)

            if decision >= UMBRAL_SALTO and not self.saltando:
                self.saltar()