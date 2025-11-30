import pygame
import math
import sys


class JuegoAutonomo:
    def __init__(self):
        pygame.init()
        self.ancho, self.alto = 800, 600
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Vehículo Autónomo")

        # COLORES
        self.AZUL_PISTA = (0, 100, 255)
        self.VERDE_PASTO = (34, 139, 34)
        self.ROJO = (200, 50, 50)
        self.AMARILLO = (255, 215, 0)
        self.BLANCO = (255, 255, 255)
        self.NARANJA = (255, 165, 0)
        self.CIAN_DEBUG = (0, 255, 255)  # Color para ver el checkpoint

        # PISTA
        self.grosor_pista = 85

        self.pista_coords = [
            (280, 550), (280, 500), (280, 450), (280, 350), (280, 200), (280, 100),
            (280, 50), (350, 40), (450, 40), (550, 60), (600, 150), (550, 250),
            (450, 300), (400, 350), (450, 400), (550, 450), (600, 550), (550, 570),
            (450, 570), (350, 550), (320, 520), (300, 500), (280, 520), (280, 550)
        ]

        self.waypoint_index = 1

        # OBSTÁCULOS
        self.obstaculos = [
            pygame.Rect(260, 350, 40, 40),
            pygame.Rect(480, 40, 25, 25),
            pygame.Rect(450, 385, 35, 35),
            pygame.Rect(260, 20, 35, 35)
        ]

        # ZONAS LÓGICAS
        self.inicio_rect = pygame.Rect(260, 550, 40, 40)

        # Meta
        self.meta_rect = pygame.Rect(300, 485, 60, 80)

        # Checkpoint
        self.checkpoint_rect = pygame.Rect(0, 0, 800, 150)
        self.checkpoint_activado = False

        # JUGADOR
        self.jugador_img = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.jugador_img, self.BLANCO, [(20, 0), (40, 40), (20, 30), (0, 40)])
        self.jugador = self.jugador_img
        self.posicion_inicial = pygame.Vector2(280, 550)
        self.centro = pygame.Vector2(self.posicion_inicial)

        # Física
        self.velocidad = 0
        self.vel_max = 4
        self.vel_evasion = 1.5
        self.angulo = 0
        self.clock = pygame.time.Clock()

        # Superficie Lógica
        self.superficie_camino = pygame.Surface((self.ancho, self.alto))
        self.dibujar_mapa_logico()

    def dibujar_mapa_logico(self):
        self.superficie_camino.fill(self.VERDE_PASTO)
        pygame.draw.lines(self.superficie_camino, self.AZUL_PISTA, True, self.pista_coords, self.grosor_pista)
        radio = self.grosor_pista // 2.1
        for x, y in self.pista_coords:
            pygame.draw.circle(self.superficie_camino, self.AZUL_PISTA, (x, y), radio)
        for obs in self.obstaculos:
            pygame.draw.rect(self.superficie_camino, self.NARANJA, obs)

    def loop_principal(self):
        while True:
            self.manejar_eventos()
            self.logica_autonoma()
            self.actualizar_fisica()
            self.dibujar()
            pygame.display.flip()
            self.clock.tick(60)

    def manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def obtener_color_sensor(self, angulo_offset, distancia):
        angulo_rad = math.radians(self.angulo + 90 + angulo_offset)
        sensor_x = self.centro.x + math.cos(angulo_rad) * distancia
        sensor_y = self.centro.y - math.sin(angulo_rad) * distancia
        punto = (int(sensor_x), int(sensor_y))
        if 0 <= punto[0] < self.ancho and 0 <= punto[1] < self.alto:
            try:
                return self.superficie_camino.get_at(punto), punto
            except:
                pass
        return (0, 0, 0, 0), punto

    def logica_autonoma(self):
        color_centro, p_centro = self.obtener_color_sensor(0, 60)
        color_izq, p_izq = self.obtener_color_sensor(30, 35)
        color_der, p_der = self.obtener_color_sensor(-30, 35)
        self.debug_sensors = [p_centro, p_izq, p_der]

        giro = 0
        aceleracion_objetivo = self.vel_max

        detecta_obstaculo = (color_centro == self.NARANJA) or (color_izq == self.NARANJA) or (color_der == self.NARANJA)

        if detecta_obstaculo:
            aceleracion_objetivo = self.vel_evasion
            if color_der == self.NARANJA or color_centro == self.NARANJA:
                giro = 7
            else:
                giro = -7
        elif color_izq == self.VERDE_PASTO:
            giro = -5
        elif color_der == self.VERDE_PASTO:
            giro = 5
        else:
            target_x, target_y = self.pista_coords[self.waypoint_index]
            dist_x = target_x - self.centro.x
            dist_y = target_y - self.centro.y
            distancia = math.sqrt(dist_x ** 2 + dist_y ** 2)

            if distancia < 50:
                self.waypoint_index = (self.waypoint_index + 1) % len(self.pista_coords)

            angulo_objetivo = math.degrees(math.atan2(-dist_y, dist_x)) - 90
            diff_angulo = (angulo_objetivo - self.angulo + 180) % 360 - 180
            if diff_angulo > 5:
                giro = 3
            elif diff_angulo < -5:
                giro = -3

        self.angulo += giro
        if self.velocidad < aceleracion_objetivo:
            self.velocidad += 0.1
        elif self.velocidad > aceleracion_objetivo:
            self.velocidad -= 0.2

    def actualizar_fisica(self):
        angulo_rad = math.radians(self.angulo + 90)
        self.centro.x += math.cos(angulo_rad) * self.velocidad
        self.centro.y -= math.sin(angulo_rad) * self.velocidad

        self.centro.x = max(0, min(self.ancho, self.centro.x))
        self.centro.y = max(0, min(self.alto, self.centro.y))

        # Activación del Checkpoint
        if self.checkpoint_rect.collidepoint(self.centro):
                self.checkpoint_activado = True

        # Meta Final
        if self.checkpoint_activado and self.meta_rect.collidepoint(self.centro):
            self.mostrar_mensaje_final()

    def mostrar_mensaje_final(self):
        fuente = pygame.font.SysFont("Arial", 60, bold=True)
        render = fuente.render("NIVEL TERMINADO", True, self.BLANCO)
        fondo_txt = render.get_rect(center=(self.ancho // 2, self.alto // 2))
        pygame.draw.rect(self.ventana, (0, 0, 0), fondo_txt.inflate(20, 20))
        self.ventana.blit(render, fondo_txt)
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()

    def dibujar(self):
        self.ventana.fill(self.VERDE_PASTO)

        # Dibujar Pista
        ancho_linea = self.grosor_pista - 4
        ancho_borde = self.grosor_pista + 4
        radio = self.grosor_pista // 2.1
        pygame.draw.lines(self.ventana, self.BLANCO, True, self.pista_coords, ancho_borde)
        pygame.draw.lines(self.ventana, self.AZUL_PISTA, True, self.pista_coords, ancho_linea)
        for x, y in self.pista_coords:
            pygame.draw.circle(self.ventana, self.BLANCO, (x, y), radio + 0)
            pygame.draw.circle(self.ventana, self.AZUL_PISTA, (x, y), radio)

        # Dibujar Obstáculos
        for obs in self.obstaculos:
            pygame.draw.rect(self.ventana, self.NARANJA, obs)
            pygame.draw.rect(self.ventana, (0, 0, 0), obs, 2)

        # Dibujar Meta y Inicio
        pygame.draw.rect(self.ventana, self.AMARILLO, self.inicio_rect)

        # La meta cambia de color si ya pasaste el checkpoint
        color_meta = self.ROJO if self.checkpoint_activado else (100, 0, 0)  # Rojo oscuro si está bloqueada
        pygame.draw.rect(self.ventana, color_meta, self.meta_rect)

        # Sensores y Waypoints
        wp_x, wp_y = self.pista_coords[self.waypoint_index]
        pygame.draw.circle(self.ventana, (255, 0, 255), (wp_x, wp_y), 5)

        if hasattr(self, 'debug_sensors'):
            pygame.draw.line(self.ventana, (255, 0, 0), self.centro, self.debug_sensors[0], 2)
            pygame.draw.line(self.ventana, (0, 255, 0), self.centro, self.debug_sensors[1], 1)
            pygame.draw.line(self.ventana, (0, 255, 0), self.centro, self.debug_sensors[2], 1)

        # Jugador
        jugador_rotado = pygame.transform.rotate(self.jugador_img, self.angulo)
        rect_rotado = jugador_rotado.get_rect(center=(self.centro.x, self.centro.y))
        self.ventana.blit(jugador_rotado, rect_rotado.topleft)


if __name__ == "__main__":
    juego = JuegoAutonomo()
    juego.loop_principal()