import pygame
import math
import sys


class CircuitoAutomatico:
    def __init__(self):
        pygame.init()
        self.ancho, self.alto = 800, 600
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Robot Automatico")

        # --- COLORES ---
        self.AZUL_PISTA = (0, 100, 255)
        self.VERDE_PASTO = (34, 139, 34)
        self.ROJO = (200, 50, 50)
        self.AMARILLO = (255, 215, 0)
        self.BLANCO = (255, 255, 255)
        self.NARANJA = (255, 165, 0)
        self.ROJO_MUERTE = (255, 0, 0)

        # --- MEMORIA ---
        self.memoria_choques = []

        # --- CONFIGURACIÓN PISTA (Waypoints) ---
        self.grosor_pista = 85
        # Esta lista es la RUTA IDEAL que el robot QUIERE seguir
        self.pista_coords = [
            (280, 550), (280, 500), (280, 450), (280, 350), (280, 200), (280, 100),
            (280, 50), (350, 40), (450, 40), (550, 60), (600, 150), (550, 250),
            (450, 300), (400, 350), (450, 400), (550, 450), (600, 550), (550, 570),
            (450, 570), (350, 550), (320, 520), (300, 500), (280, 520), (280, 550)
        ]
        self.waypoint_index = 1  # Empezamos persiguiendo el punto 1

        # --- OBSTÁCULOS ---
        self.obstaculos = [
            pygame.Rect(260, 350, 25, 25),
            pygame.Rect(480, 40, 25, 25),
            pygame.Rect(450, 385, 25, 25),
            # EL OBSTÁCULO "IMPOSIBLE" (Requiere memoria para pasarlo)
            pygame.Rect(260, 20, 35, 35),
            pygame.Rect(480, 385, 25, 25)

        ]

        # Zonas
        self.inicio_rect = pygame.Rect(260, 550, 40, 40)
        self.meta_rect = pygame.Rect(300, 485, 60, 80)
        self.checkpoint_rect = pygame.Rect(0, 0, 800, 150)
        self.checkpoint_activado = False

        # --- JUGADOR ---
        self.jugador_img = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.jugador_img, self.BLANCO, [(20, 0), (40, 40), (20, 30), (0, 40)])
        self.jugador = self.jugador_img
        self.posicion_inicial = pygame.Vector2(280, 550)
        self.centro = pygame.Vector2(self.posicion_inicial)

        # Física
        self.velocidad = 0
        self.vel_max = 4
        self.angulo = 0
        self.clock = pygame.time.Clock()

        # Mapa Lógico
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
            self.cerebro()  # <--- LÓGICA PRINCIPAL
            self.actualizar_fisica()
            self.verificar_colision_hitbox()  # Muerte estricta
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

    def cerebro(self):
        """
        La toma de dicisiones que realiza el programa contiene 3 capas:
        1. Calcular dirección al Waypoint (Su Objetivo es seguir el camino y llegar a la meta)
        2. Sumar repulsión por Memoria de Choques (EL vehiculo utiliza un sistema de aprendizaje por refuerzo negaativo
        con el fin de evitar errores del pasado)
        3. Sumar evasión por Sensores (Los sensores detectan los obstaculos y el peligro cercano)
        """
        giro_final = 0
        velocidad_objetivo = self.vel_max

        # --- CAPA 1: NAVEGACIÓN POR WAYPOINTS ---
        target_x, target_y = self.pista_coords[self.waypoint_index]

        # Calcular vector hacia el objetivo
        dist_x = target_x - self.centro.x
        dist_y = target_y - self.centro.y
        distancia_wp = math.sqrt(dist_x ** 2 + dist_y ** 2)

        # Calcular ángulo deseado hacia el waypoint
        angulo_wp = math.degrees(math.atan2(-dist_y, dist_x)) - 90
        diff_wp = (angulo_wp - self.angulo + 180) % 360 - 180

        # Girar suavemente hacia el waypoint
        if diff_wp > 10:
            giro_final += 3
        elif diff_wp < -10:
            giro_final -= 3
        else:
            giro_final += diff_wp * 0.3  # Ajuste fino

        # Cambiar de waypoint si estamos cerca
        if distancia_wp < 60:
            self.waypoint_index = (self.waypoint_index + 1) % len(self.pista_coords)

        # --- CAPA 2: MEMORIA DE ERRORES  ---
        for punto_muerte in self.memoria_choques:
            distancia = self.centro.distance_to(punto_muerte)

            # Radio de miedo de 100 pixeles de la zona donde choco anteriormente
            if distancia < 100:
                # Calcular vector unitario hacia el peligro
                vec_x = punto_muerte.x - self.centro.x
                vec_y = -(punto_muerte.y - self.centro.y)  # Y invertida visualmente
                angle_to_death = math.degrees(math.atan2(vec_y, vec_x)) - 90

                # Detección de posible peligro
                diff_death = (angle_to_death - self.angulo + 180) % 360 - 180

                # Fuerza de repulsióno miedo
                fuerza = (100 - distancia) / 8

                # Detección de riesgos en un radio de 120 grados
                if abs(diff_death) < 60:
                    velocidad_objetivo = 2  # Bajar velocidad por precaución
                    # Girar hacia el lado OPUESTO del peligro
                    if diff_death > 0:  # Peligro a la derecha
                        giro_final -= fuerza  # Forzar giro Izquierda
                    else:  # Peligro a la izquierda
                        giro_final += fuerza  # Forzar giro Derecha

        # CAPA 3: SENSORES REACTIVOS  ---
        # Direccion de los sensores
        c_cen, p_cen = self.obtener_color_sensor(0, 55)
        c_izq, p_izq = self.obtener_color_sensor(30, 40)
        c_der, p_der = self.obtener_color_sensor(-30, 40)
        self.debug_sensors = [p_cen, p_izq, p_der]

        #Posibles amenazas
        es_peligro = lambda c: c == self.NARANJA or c == self.VERDE_PASTO

        if es_peligro(c_cen) or es_peligro(c_izq) or es_peligro(c_der):
            velocidad_objetivo = 0.5  # Frenar casi en seco
            # Lógica de evasión de emergencia
            if es_peligro(c_izq):
                giro_final = -7  # Giro duro Derecha (corrección: invertir lógica si es necesario)
                # Nota: En coord pantalla Y crece abajo.
                # Peligro a la Izquierda debo girar a la Derecha
                giro_final = -8
            elif es_peligro(c_der):
                giro_final = 8
            else:
                # Si es frontal puro, elegir lado preferente o azar
                giro_final = 8

        # Aplicar límites
        self.angulo += giro_final

        # Física
        if self.velocidad < velocidad_objetivo:
            self.velocidad += 0.1
        elif self.velocidad > velocidad_objetivo:
            self.velocidad -= 0.2

    def verificar_colision_hitbox(self):
        """ Detector de colisión estricto """
        offset = 14  # Radio aprox del robot
        # Puntos clave: Nariz, Cola-Izq, Cola-Der
        ang = math.radians(self.angulo + 90)
        puntos = [
            self.centro,
            self.centro + pygame.Vector2(math.cos(ang) * offset, -math.sin(ang) * offset),
        ]

        choco = False
        for p in puntos:
            if not (0 <= p.x < self.ancho and 0 <= p.y < self.alto):
                choco = True;
                break
            try:
                if self.superficie_camino.get_at((int(p.x), int(p.y))) in [self.VERDE_PASTO, self.NARANJA]:
                    choco = True;
                    break
            except:
                pass

        if choco:
            print(f"CHOQUE EN {self.centro}. APRENDIENDO...")
            self.memoria_choques.append(pygame.Vector2(self.centro))
            self.reset_jugador()

    def reset_jugador(self):
        self.centro = pygame.Vector2(self.posicion_inicial)
        self.angulo = 0
        self.velocidad = 0
        self.waypoint_index = 1  # Reiniciar ruta
        self.checkpoint_activado = False
        pygame.time.wait(500)

    def actualizar_fisica(self):
        angulo_rad = math.radians(self.angulo + 90)
        self.centro.x += math.cos(angulo_rad) * self.velocidad
        self.centro.y -= math.sin(angulo_rad) * self.velocidad

        # Checkpoint
        if self.checkpoint_rect.collidepoint(self.centro):
            if not self.checkpoint_activado: self.checkpoint_activado = True

        # Meta
        if self.checkpoint_activado and self.meta_rect.collidepoint(self.centro):
            self.mostrar_mensaje_final()

    def mostrar_mensaje_final(self):
        fuente = pygame.font.SysFont("Arial", 50, bold=True)
        txt = f"META LOGRADA (Errores: {len(self.memoria_choques)})"
        render = fuente.render(txt, True, self.BLANCO)
        rect = render.get_rect(center=(self.ancho // 2, self.alto // 2))
        pygame.draw.rect(self.ventana, (0, 0, 0), rect.inflate(20, 20))
        self.ventana.blit(render, rect)
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

    def dibujar(self):
        self.ventana.fill(self.VERDE_PASTO)

        # Pista
        ancho_linea = self.grosor_pista - 4
        ancho_borde = self.grosor_pista + 4
        radio = self.grosor_pista // 2.1
        pygame.draw.lines(self.ventana, self.BLANCO, True, self.pista_coords, ancho_borde)
        pygame.draw.lines(self.ventana, self.AZUL_PISTA, True, self.pista_coords, ancho_linea)
        for x, y in self.pista_coords:
            pygame.draw.circle(self.ventana, self.BLANCO, (x, y), radio + 0)
            pygame.draw.circle(self.ventana, self.AZUL_PISTA, (x, y), radio)

        # Obstáculos
        for obs in self.obstaculos:
            pygame.draw.rect(self.ventana, self.NARANJA, obs)
            pygame.draw.rect(self.ventana, (0, 0, 0), obs, 2)

        # Marcas de MEMORIA
        for punto in self.memoria_choques:
            px, py = int(punto.x), int(punto.y)
            pygame.draw.line(self.ventana, self.ROJO_MUERTE, (px - 10, py - 10), (px + 10, py + 10), 3)
            pygame.draw.line(self.ventana, self.ROJO_MUERTE, (px - 10, py + 10), (px + 10, py - 10), 3)

        # Waypoint Actual
        wx, wy = self.pista_coords[self.waypoint_index]
        pygame.draw.circle(self.ventana, (255, 0, 255), (wx, wy), 8, 2)

        # Zonas
        pygame.draw.rect(self.ventana, self.AMARILLO, self.inicio_rect)
        c_meta = self.ROJO if self.checkpoint_activado else (100, 0, 0)
        pygame.draw.rect(self.ventana, c_meta, self.meta_rect)

        # Jugador
        jugador_rotado = pygame.transform.rotate(self.jugador_img, self.angulo)
        rect_rotado = jugador_rotado.get_rect(center=(self.centro.x, self.centro.y))
        self.ventana.blit(jugador_rotado, rect_rotado.topleft)

        # Sensores
        if hasattr(self, 'debug_sensors'):
            pygame.draw.line(self.ventana, (255, 0, 0), self.centro, self.debug_sensors[0], 2)


if __name__ == "__main__":
    juego = CircuitoAutomatico()
    juego.loop_principal()