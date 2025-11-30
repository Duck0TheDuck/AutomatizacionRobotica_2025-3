import pygame
import math
import sys

class Juego:
    def __init__(self):
        pygame.init()
        self.ancho, self.alto = 800, 600
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Conducción Libre")

        # Colores
        self.VERDE = (50, 200, 50)
        self.AZUL = (50, 50, 200)
        self.BLANCO = (255, 255, 255)

        # Jugador
        self.jugador_img = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.polygon(self.jugador_img, self.AZUL, [(25, 0), (50, 50), (0, 50)])
        self.jugador = self.jugador_img
        self.centro = pygame.Vector2(self.ancho // 2, self.alto // 2)

        # Variables de movimiento
        self.velocidad = 0
        self.aceleracion = 0.3
        self.vel_max = 5
        self.angulo = 0  # 0 = punta hacia arriba
        self.velocidad_giro = 4 # Velocidad de rotación manual

        self.en_movimiento = False
        self.clock = pygame.time.Clock()

        # Superficie para el camino (Fondo limpio)
        self.superficie_camino = pygame.Surface((self.ancho, self.alto))
        self.superficie_camino.fill(self.VERDE)

    def loop_principal(self):
        while True:
            self.manejar_eventos()
            self.actualizar_movimiento()
            self.dibujar()
            pygame.display.flip()
            self.clock.tick(60)

    def manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.en_movimiento = True
                elif event.key == pygame.K_s:
                    self.velocidad = 0
                    self.en_movimiento = False

    def actualizar_movimiento(self):
        # 1. Control de Velocidad (W/S)
        if self.en_movimiento:
            if self.velocidad < self.vel_max:
                self.velocidad += self.aceleracion
            else:
                self.velocidad = self.vel_max
        else:
            self.velocidad = 0

        # 2. Control de Dirección Manual (A/D)
        # Usamos get_pressed para que el giro sea fluido al mantener la tecla
        teclas = pygame.key.get_pressed()
        if self.velocidad != 0: # Solo giramos si nos movemos
            if teclas[pygame.K_a]:
                self.angulo += self.velocidad_giro
            if teclas[pygame.K_d]:
                self.angulo -= self.velocidad_giro

        # 3. Actualizar posición física
        angulo_rad = math.radians(self.angulo - 90)
        self.centro.x += math.cos(angulo_rad) * self.velocidad
        self.centro.y += math.sin(angulo_rad) * self.velocidad

        # 4. Movimiento Infinito (Wrap-around / Pantalla infinita)
        if self.centro.x < 0:
            self.centro.x = self.ancho
        elif self.centro.x > self.ancho:
            self.centro.x = 0

        if self.centro.y < 0:
            self.centro.y = self.alto
        elif self.centro.y > self.alto:
            self.centro.y = 0

    def dibujar(self):
        # Dibuja el fondo verde limpio
        self.ventana.blit(self.superficie_camino, (0, 0))

        # Dibujar jugador rotado
        jugador_rotado = pygame.transform.rotate(self.jugador_img, self.angulo)
        rect_rotado = jugador_rotado.get_rect(center=(self.centro.x, self.centro.y))
        self.ventana.blit(jugador_rotado, rect_rotado.topleft)

if __name__ == "__main__":
    juego = Juego()
    juego.loop_principal()