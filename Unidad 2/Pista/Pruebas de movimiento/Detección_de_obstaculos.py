import pygame
import math
import sys


class Juego:
    def __init__(self):
        pygame.init()
        self.ancho, self.alto = 800, 600
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Evasión Automática de Obstáculos")

        # Colores
        self.VERDE = (50, 200, 50)
        self.AZUL = (50, 50, 200)
        self.NARANJA = (255, 165, 0)  # Color para los obstáculos
        self.BLANCO = (255, 255, 255)

        # Jugador
        self.jugador_img = pygame.Surface((50, 50), pygame.SRCALPHA)
        # El triángulo define la orientación del movimiento
        pygame.draw.polygon(self.jugador_img, self.AZUL, [(25, 0), (50, 50), (0, 50)])
        self.jugador = self.jugador_img
        self.centro = pygame.Vector2(self.ancho // 2, self.alto // 2)

        # Variables de movimiento
        self.velocidad = 0
        self.aceleracion = 0.3
        self.vel_max = 5
        self.angulo = 0  # 0 = punta hacia arriba (dirección constante inicial)

        # Controla si el jugador debe acelerar y mantener el movimiento
        self.en_movimiento = False

        self.clock = pygame.time.Clock()

        # Superficie para el camino (Fondo)
        self.superficie_camino = pygame.Surface((self.ancho, self.alto))
        self.superficie_camino.fill(self.VERDE)

        # --- AGREGAR OBSTÁCULOS ---
        # Definimos rectángulos naranjas en posiciones aleatorias o fijas
        self.obstaculos = [
            pygame.Rect(380, 200, 100, 50),
            pygame.Rect(100, 400, 80, 80),
            pygame.Rect(600, 300, 120, 40),
            pygame.Rect(300, 100, 60, 60),
            pygame.Rect(500, 500, 90, 90),
            pygame.Rect(200, 50, 50, 200)
        ]

        # Dibujarlos en la superficie de fondo para que sean parte del terreno
        for obs in self.obstaculos:
            pygame.draw.rect(self.superficie_camino, self.NARANJA, obs)

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
                    # W: Inicia el movimiento automático
                    self.en_movimiento = True
                elif event.key == pygame.K_s:
                    # S: Detiene el movimiento completamente (alto total)
                    self.velocidad = 0
                    self.en_movimiento = False

    def actualizar_movimiento(self):
        # 1. Velocidad (W/S)
        if self.en_movimiento:
            if self.velocidad < self.vel_max:
                self.velocidad += self.aceleracion
            else:
                self.velocidad = self.vel_max
        else:
            self.velocidad = 0

        # --- 2. DETECCIÓN Y EVASIÓN ---
        # Calculamos la posición del sensor (un punto delante del jugador)
        distancia_sensor = 70
        angulo_rad = math.radians(self.angulo - 90)

        sensor_x = self.centro.x + math.cos(angulo_rad) * distancia_sensor
        sensor_y = self.centro.y + math.sin(angulo_rad) * distancia_sensor

        # Verificamos qué hay en esa posición
        detectando_obstaculo = False

        # Solo verificamos si el sensor está dentro de la pantalla
        if 0 <= int(sensor_x) < self.ancho and 0 <= int(sensor_y) < self.alto:
            try:
                color_punta = self.superficie_camino.get_at((int(sensor_x), int(sensor_y)))

                # Si el sensor toca color NARANJA, activamos evasión
                if color_punta == self.NARANJA:
                    detectando_obstaculo = True
            except IndexError:
                pass  # Ignorar errores de límites por si acaso

        # Lógica de giro
        if detectando_obstaculo:
            # Gira a la derecha ABRUPTAMENTE para esquivar
            self.angulo += 20  # Aumentado de 5 a 20 para un giro brusco
        else:
            pass

        # 3. Actualizar posición física
        angulo_rad = math.radians(self.angulo - 90)
        self.centro.x += math.cos(angulo_rad) * self.velocidad
        self.centro.y += math.sin(angulo_rad) * self.velocidad

        # --- 4. DETECCIÓN DE CHOQUE (GAME OVER) ---
        # Verificar si el centro del jugador toca algún obstáculo
        for obs in self.obstaculos:
            if obs.collidepoint(self.centro):
                print("¡CHOCASTE! Fin del juego.")
                self.mostrar_mensaje("¡GAME OVER!")  # Mostrar mensaje antes de cerrar
                pygame.quit()
                sys.exit()

        # 5. Movimiento Infinito (Wrap-around)
        if self.centro.x < 0:
            self.centro.x = self.ancho
        elif self.centro.x > self.ancho:
            self.centro.x = 0

        if self.centro.y < 0:
            self.centro.y = self.alto
        elif self.centro.y > self.alto:
            self.centro.y = 0

    def dibujar(self):
        # Dibuja el fondo (con los obstáculos ya pintados)
        self.ventana.blit(self.superficie_camino, (0, 0))

        # Dibujar jugador
        jugador_rotado = pygame.transform.rotate(self.jugador_img, -self.angulo)
        rect_rotado = jugador_rotado.get_rect(center=(self.centro.x, self.centro.y))
        self.ventana.blit(jugador_rotado, rect_rotado.topleft)

        # (Opcional) Dibujar línea del sensor para ver qué está detectando (Debug)
        distancia_sensor = 60
        angulo_rad = math.radians(self.angulo - 90)
        sensor_x = self.centro.x + math.cos(angulo_rad) * distancia_sensor
        sensor_y = self.centro.y + math.sin(angulo_rad) * distancia_sensor
        pygame.draw.line(self.ventana, (255, 0, 0), self.centro, (sensor_x, sensor_y), 2)

    def mostrar_mensaje(self, texto):
        fuente = pygame.font.SysFont(None, 60)
        # Fondo negro para que se lea bien
        texto_surf = fuente.render(texto, True, (255, 0, 0))
        rect = texto_surf.get_rect(center=(self.ancho // 2, self.alto // 2))
        pygame.draw.rect(self.ventana, (0, 0, 0), rect.inflate(20, 20))
        self.ventana.blit(texto_surf, rect)
        pygame.display.flip()
        pygame.time.wait(2000)  # Esperar 2 segundos para ver el mensaje


if __name__ == "__main__":
    juego = Juego()
    juego.loop_principal()