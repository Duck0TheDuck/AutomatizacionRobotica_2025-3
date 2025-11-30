import pygame
import math
import sys
import cv2
import mediapipe as mp
import numpy as np

class Juego:
    def __init__(self):
        # --- INICIALIZACIÓN PYGAME ---
        pygame.init()
        self.ancho, self.alto = 800, 600
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Circuito Controlado por Mano - Índice para Retroceder")

        # --- CONFIGURACIÓN MEDIAPIPE Y CÁMARA ---
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(static_image_mode=False,
                                         max_num_hands=1,
                                         min_detection_confidence=0.7,
                                         min_tracking_confidence=0.5)
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(1)

        # --- COLORES ---
        self.AZUL_PISTA = (0, 100, 255)
        self.VERDE_PASTO = (34, 139, 34)
        self.ROJO = (200, 50, 50)
        self.AMARILLO = (255, 215, 0)
        self.BLANCO = (255, 255, 255)

        # --- CONFIGURACIÓN DE LA PISTA ---
        self.grosor_pista = 85
        self.pista_coords = [
            (280, 550), (280, 500), (280, 450), (280, 350), (280, 200),
            (280, 100), (280, 50), (350, 40), (450, 40), (550, 60),
            (600, 150), (550, 250), (450, 300), (400, 350), (450, 400),
            (550, 450), (600, 550), (550, 570), (450, 570), (350, 550),
            (320, 520), (300, 500), (280, 520), (280, 550)
        ]

        # --- POSICIONES ---
        self.inicio_rect = pygame.Rect(260, 550, 40, 40)
        self.meta_rect = pygame.Rect(300, 485, 60, 80)
        self.checkpoint_rect = pygame.Rect(300, 50, 200, 100)
        self.checkpoint_activado = False

        # --- JUGADOR ---
        self.jugador_img = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.jugador_img, self.BLANCO, [(20, 0), (40, 40), (20, 30), (0, 40)])
        self.jugador = self.jugador_img
        self.posicion_inicial = pygame.Vector2(280, 550)
        self.centro = pygame.Vector2(self.posicion_inicial)

        # Variables de movimiento
        self.velocidad = 0
        self.aceleracion = 0.2
        self.vel_max = 6
        self.frenado = 0.1
        self.velocidad_giro = 4
        self.angulo = 0

        self.teclas_presionadas = {"w": False, "s": False, "a": False, "d": False}
        self.clock = pygame.time.Clock()

        # Superficie para colisiones
        self.superficie_camino = pygame.Surface((self.ancho, self.alto))
        self.superficie_camino.fill(self.VERDE_PASTO)
        pygame.draw.lines(self.superficie_camino, self.AZUL_PISTA, True, self.pista_coords, self.grosor_pista)

        self.gesto_actual = "Esperando..."

    def detectar_gesto(self, hand_landmarks):
        # Dedos: [Pulgar, Índice, Medio, Anular, Meñique]
        dedos = []
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]

        # Pulgar
        if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:
            dedos.append(1)
        else:
            dedos.append(0)

        # Otros 4 dedos
        for tip, pip in zip(tips, pips):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                dedos.append(1)
            else:
                dedos.append(0)

        self.teclas_presionadas = {"w": False, "s": False, "a": False, "d": False}
        total_dedos = sum(dedos)

        # --- LÓGICA DE GESTOS ACTUALIZADA ---

        # GESTO: PALMA (Alto Total)
        if total_dedos >= 4:
            self.gesto_actual = "PALMA: ALTO TOTAL"
            self.velocidad = 0
            return

        # GESTO: PULGAR (Avanzar / W)
        if dedos[0] == 1 and total_dedos <= 2:
            self.gesto_actual = "PULGAR: AVANZAR"
            self.teclas_presionadas["w"] = True

        # GESTO: ÍNDICE (Retroceder / S) --- NUEVA FUNCIÓN ---
        # Levantamos Índice (dedos[1]) y aseguramos que el Pulgar esté cerrado (dedos[0]==0)
        elif dedos[2] == 1 and dedos[0] == 0 and total_dedos <= 2:
            self.gesto_actual = "INDICE: RETROCEDER"
            self.teclas_presionadas["s"] = True

        # GESTO: MEDIO (Derecha / D) --- NUEVA ASIGNACIÓN PARA DERECHA ---
        # Usamos el dedo medio (dedos[2]) para girar a la derecha
        elif dedos[1] == 1 and total_dedos <= 2:
            self.gesto_actual = "MEDIO: DERECHA"
            self.teclas_presionadas["d"] = True

        # GESTO: MEÑIQUE (Izquierda / A)
        elif dedos[4] == 1 and total_dedos <= 2:
            self.gesto_actual = "MEÑIQUE: IZQUIERDA"
            self.teclas_presionadas["a"] = True

        else:
            self.gesto_actual = "Neutro"

    def procesar_camara(self):
        if self.cap is None or not self.cap.isOpened():
            return None

        success, frame = self.cap.read()
        if not success:
            return None

        # Espejo Horizontal
        frame = cv2.flip(frame, 1)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                self.detectar_gesto(hand_landmarks)
        else:
            self.teclas_presionadas = {"w": False, "s": False, "a": False, "d": False}
            self.gesto_actual = "Sin manos"

        # Conversión a Pygame Horizontal (Correcta)
        try:
            frame_peque = cv2.resize(frame, (210, 160))
            frame_rgb = cv2.cvtColor(frame_peque, cv2.COLOR_BGR2RGB)
            frame_transposed = np.transpose(frame_rgb, (1, 0, 2))
            frame_surface = pygame.surfarray.make_surface(frame_transposed)
            return frame_surface
        except Exception as e:
            return None

    def loop_principal(self):
        while True:
            frame_camara = self.procesar_camara()
            self.manejar_eventos()
            self.actualizar_movimiento()
            self.dibujar(frame_camara)
            pygame.display.flip()
            self.clock.tick(60)

    def manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.cap: self.cap.release()
                pygame.quit()
                sys.exit()

    def actualizar_movimiento(self):
        # Control W/S
        if self.teclas_presionadas["w"]:
            self.velocidad += self.aceleracion
        elif self.teclas_presionadas["s"]:  # Ahora activado con el Índice
            self.velocidad -= self.aceleracion
        else:
            if self.velocidad > 0:
                self.velocidad -= self.frenado
            elif self.velocidad < 0:
                self.velocidad += self.frenado
            if abs(self.velocidad) < self.frenado: self.velocidad = 0

        self.velocidad = max(-self.vel_max / 2, min(self.vel_max, self.velocidad))

        # Control A/D
        if self.velocidad != 0:
            direccion = 1 if self.velocidad > 0 else -1
            if self.teclas_presionadas["d"]: self.angulo -= self.velocidad_giro * direccion
            if self.teclas_presionadas["a"]: self.angulo += self.velocidad_giro * direccion

        angulo_rad = math.radians(self.angulo + 90)
        self.centro.x += math.cos(angulo_rad) * self.velocidad
        self.centro.y -= math.sin(angulo_rad) * self.velocidad

        self.centro.x = max(0, min(self.ancho, self.centro.x))
        self.centro.y = max(0, min(self.alto, self.centro.y))

        if not self.esta_en_camino():
            self.mostrar_mensaje("¡Fuera de pista!")
            self.reset_jugador()

        if self.checkpoint_rect.collidepoint(self.centro):
            self.checkpoint_activado = True

        if self.meta_rect.collidepoint(self.centro):
            if self.checkpoint_activado:
                self.mostrar_mensaje("¡VUELTA COMPLETADA!")
                self.reset_jugador()

    def esta_en_camino(self):
        try:
            color_pixel = self.superficie_camino.get_at((int(self.centro.x), int(self.centro.y)))
            return color_pixel[:3] == self.AZUL_PISTA
        except IndexError:
            return False

    def reset_jugador(self):
        self.centro.x, self.centro.y = self.posicion_inicial.x, self.posicion_inicial.y
        self.angulo = 0
        self.velocidad = 0
        self.checkpoint_activado = False
        self.teclas_presionadas = {k: False for k in self.teclas_presionadas}

    def dibujar(self, frame_camara):
        self.ventana.fill(self.VERDE_PASTO)

        # PISTA
        ancho_linea = self.grosor_pista - 4
        ancho_borde = self.grosor_pista + 4
        radio = self.grosor_pista // 2.1

        pygame.draw.lines(self.ventana, self.BLANCO, True, self.pista_coords, ancho_borde)
        pygame.draw.lines(self.ventana, self.AZUL_PISTA, True, self.pista_coords, ancho_linea)

        for x, y in self.pista_coords:
            pygame.draw.circle(self.ventana, self.BLANCO, (x, y), radio + 0)
            pygame.draw.circle(self.ventana, self.AZUL_PISTA, (x, y), radio)

        pygame.draw.rect(self.ventana, self.AMARILLO, self.inicio_rect)
        color_meta = self.ROJO if self.checkpoint_activado else (150, 50, 50)
        pygame.draw.rect(self.ventana, color_meta, self.meta_rect)

        # JUGADOR
        jugador_rotado = pygame.transform.rotate(self.jugador_img, self.angulo)
        rect_rotado = jugador_rotado.get_rect(center=(self.centro.x, self.centro.y))
        self.ventana.blit(jugador_rotado, rect_rotado.topleft)

        # CÁMARA
        pygame.draw.rect(self.ventana, (0, 0, 0), (10, 10, 210, 160))
        if frame_camara:
            self.ventana.blit(frame_camara, (15, 15))

        fuente = pygame.font.SysFont("Arial", 20, bold=True)
        texto = fuente.render(f"Gesto: {self.gesto_actual}", True, self.BLANCO)
        pygame.draw.rect(self.ventana, (0, 0, 0), (10, 180, 200, 30))
        self.ventana.blit(texto, (15, 185))

    def mostrar_mensaje(self, texto):
        fuente = pygame.font.SysFont("Arial", 50, bold=True)
        render = fuente.render(texto, True, self.BLANCO)
        fondo_txt = render.get_rect(center=(self.ancho // 2, self.alto // 2))
        pygame.draw.rect(self.ventana, (0, 0, 0), fondo_txt.inflate(20, 20))
        self.ventana.blit(render, fondo_txt)
        pygame.display.flip()
        pygame.time.wait(1500)


if __name__ == "__main__":
    juego = Juego()
    juego.loop_principal()