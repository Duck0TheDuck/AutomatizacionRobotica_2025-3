import pygame
import math
import sys


class Juego:
    def __init__(self):
        pygame.init()
        self.ancho, self.alto = 800, 600
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Movimiento siguiendo la punta")

        # Colores
        self.VERDE = (50, 200, 50)
        self.ROJO = (200, 50, 50)
        self.AZUL = (50, 50, 200)
        self.BLANCO = (255, 255, 255)
        self.AMARILLO = (255, 255, 0)

        # Inicio y meta
        self.inicio_rect = pygame.Rect(50, 500, 50, 40)
        self.meta_rect = pygame.Rect(600, 50, 150, 80)

        # Jugador
        self.jugador_img = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.polygon(self.jugador_img, self.AZUL, [(25, 0), (50, 50), (0, 50)])
        self.jugador = self.jugador_img
        self.centro = pygame.Vector2(100, 520)  # centro lógico del jugador

        # Variables de movimiento
        self.velocidad = 0
        self.aceleracion = 0.3
        self.vel_max = 5
        self.frenado = 0.1
        self.velocidad_giro = 3
        self.angulo = 0  # 0 = punta hacia arriba
        self.en_movimiento = False

        self.teclas_presionadas = {"w": False, "s": False, "a": False, "d": False}
        self.clock = pygame.time.Clock()

        # Superficie para el camino
        self.superficie_camino = pygame.Surface((self.ancho, self.alto))
        self.superficie_camino.fill(self.BLANCO)
        pygame.draw.line(self.superficie_camino, self.VERDE,
                         self.inicio_rect.center, self.meta_rect.center, 100)

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
                    self.teclas_presionadas["w"] = True
                    self.en_movimiento = True
                elif event.key == pygame.K_s:
                    self.teclas_presionadas["s"] = True
                    self.en_movimiento = True
                elif event.key == pygame.K_a:
                    self.teclas_presionadas["a"] = True
                elif event.key == pygame.K_d:
                    self.teclas_presionadas["d"] = True
                elif event.key == pygame.K_SPACE:
                    self.stop()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.teclas_presionadas["w"] = False
                elif event.key == pygame.K_s:
                    self.teclas_presionadas["s"] = False
                elif event.key == pygame.K_a:
                    self.teclas_presionadas["a"] = False
                elif event.key == pygame.K_d:
                    self.teclas_presionadas["d"] = False

    def actualizar_movimiento(self):
        if not self.en_movimiento:
            return

        # Acelerar y frenar como un vehículo
        if self.teclas_presionadas["w"]:
            self.velocidad += self.aceleracion
        elif self.teclas_presionadas["s"]:
            self.velocidad -= self.aceleracion
        else:
            if self.velocidad > 0:
                self.velocidad -= self.frenado
            elif self.velocidad < 0:
                self.velocidad += self.frenado

        self.velocidad = max(-self.vel_max / 2, min(self.vel_max, self.velocidad))

        if self.velocidad != 0:
            if self.teclas_presionadas["d"]:
                self.angulo += self.velocidad_giro * (self.velocidad / self.vel_max)
            if self.teclas_presionadas["a"]:
                self.angulo -= self.velocidad_giro * (self.velocidad / self.vel_max)

        angulo_rad = math.radians(self.angulo - 90)
        self.centro.x += math.cos(angulo_rad) * self.velocidad
        self.centro.y += math.sin(angulo_rad) * self.velocidad

        # Mantener dentro de pantalla
        self.centro.x = max(0, min(self.ancho, self.centro.x))
        self.centro.y = max(0, min(self.alto, self.centro.y))

        # Verificar si está dentro del camino
        if not self.esta_en_camino():
            self.mostrar_mensaje("¡Saliste del camino!")
            self.reset_jugador()

        # Verificar si llegó a la meta
        if pygame.Rect(self.meta_rect).collidepoint(self.centro):
            self.mostrar_mensaje("Tocaste un objeto rojo")
            self.reset_jugador()

    def esta_en_camino(self):
        # Devuelve True si el jugador está sobre el camino verde
        if 0 <= int(self.centro.x) < self.ancho and 0 <= int(self.centro.y) < self.alto:
            color_pixel = self.superficie_camino.get_at((int(self.centro.x), int(self.centro.y)))
            return color_pixel == self.VERDE
        return False

    def reset_jugador(self):
        self.centro = pygame.Vector2(100, 520)
        self.angulo = 0
        self.velocidad = 0
        self.stop()

    def dibujar(self):
        self.ventana.blit(self.superficie_camino, (0, 0))

        # Dibujar inicio y meta
        pygame.draw.rect(self.ventana, self.AZUL, self.inicio_rect)
        pygame.draw.rect(self.ventana, self.ROJO, self.meta_rect)

        # Rotar jugador
        jugador_rotado = pygame.transform.rotate(self.jugador_img, -self.angulo)
        rect_rotado = jugador_rotado.get_rect(center=(self.centro.x, self.centro.y))
        self.ventana.blit(jugador_rotado, rect_rotado.topleft)

    def stop(self):
        self.en_movimiento = False
        for k in self.teclas_presionadas:
            self.teclas_presionadas[k] = False

    def mostrar_mensaje(self, texto):
        fuente = pygame.font.SysFont(None, 60)
        render = fuente.render(texto, True, self.ROJO)
        rect = render.get_rect(center=(self.ancho // 2, self.alto // 2))
        self.ventana.blit(render, rect)
        pygame.display.flip()
        pygame.time.wait(1500)


if __name__ == "__main__":
    juego = Juego()
    juego.loop_principal()
