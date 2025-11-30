import pygame
import sys


class Juego:
    def __init__(self):
        pygame.init()
        self.ancho, self.alto = 800, 600
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Pista Angular Azul - Vuelta Completa")

        # Bandera para controlar el bucle principal
        self.running = True

        # --- COLORES ---
        self.AZUL_PISTA = (0, 100, 255)  # Carretera
        self.VERDE_PASTO = (34, 139, 34)  # Fondo
        self.ROJO = (200, 50, 50)  # Meta
        self.AMARILLO = (255, 215, 0)  # Inicio
        self.BLANCO = (255, 255, 255)

        # --- CONFIGURACIÓN DE LA PISTA ---
        self.grosor_pista = 85

        # Coordenadas mejoradas
        self.pista_coords = [
            (280, 550),  # Inicio/Meta Cerca (Punto 1)
            (280, 500),  # Subida recta
            (280, 450),
            (280, 350),
            (280, 200),
            (280, 100),
            (280, 50),  # Inicio de curva superior izquierda (Punto 7)
            (350, 40),
            (450, 40),  # Parte superior central
            (550, 60),
            (600, 150),  # Curva superior derecha
            (550, 250),
            (450, 300),
            (400, 350),
            (450, 400),
            (550, 450),  # Curva inferior derecha
            (600, 550),
            (550, 570),
            (450, 570),
            (350, 550),  # Curva inferior central
            (320, 520),
            (300, 500),
            (280, 520),  # Cierre cerca del inicio/meta
            (280, 550)  # Cierra la forma
        ]

        # --- POSICIONES (Se mantienen para el dibujo) ---
        self.inicio_rect = pygame.Rect(260, 550, 40, 40)
        self.meta_rect = pygame.Rect(300, 485, 60, 80)

        # El checkpoint se mantiene solo para que la lógica de la meta en 'dibujar' no falle,
        # aunque nunca se activará.
        self.checkpoint_activado = False

        self.clock = pygame.time.Clock()

    def loop_principal(self):
        # El bucle ahora depende de self.running
        while self.running:
            self.manejar_eventos()
            self.dibujar()
            pygame.display.flip()
            self.clock.tick(60)

    def manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False  # Cierra al hacer clic en la X
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.running = False  # Cierra al presionar Espacio

    # Se eliminaron las funciones: actualizar_movimiento, esta_en_camino, reset_jugador, mostrar_mensaje.

    def dibujar(self):
        self.ventana.fill(self.VERDE_PASTO)

        # --- Lógica de Dibujo de Pista ---
        ancho_linea = self.grosor_pista - 4
        ancho_borde = self.grosor_pista + 4
        radio = self.grosor_pista // 2

        # 1. Bordes
        pygame.draw.lines(self.ventana, self.BLANCO, True, self.pista_coords, ancho_borde)

        # 2. Pista
        pygame.draw.lines(self.ventana, self.AZUL_PISTA, True, self.pista_coords, ancho_linea)

        # 3. Suavizar las Esquinas (Círculos)
        for x, y in self.pista_coords:
            # Círculos blancos (borde)
            pygame.draw.circle(self.ventana, self.BLANCO, (x, y), radio + 0)
            # Círculos azules (pista)
            pygame.draw.circle(self.ventana, self.AZUL_PISTA, (x, y), radio)

        # 4. Dibujar Inicio y Meta
        pygame.draw.rect(self.ventana, self.AMARILLO, self.inicio_rect)
        color_meta = self.ROJO if self.checkpoint_activado else (150, 50, 50)
        pygame.draw.rect(self.ventana, color_meta, self.meta_rect)

        # Se eliminó la lógica de dibujo del Jugador.


if __name__ == "__main__":
    juego = Juego()
    juego.loop_principal()