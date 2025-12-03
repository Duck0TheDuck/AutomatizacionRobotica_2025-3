from ProyectoIntegrador.src.settings import SUELO_Y, ANCHO_DINO, ALTO_DINO, COLOR_DINO
import pygame as pg

class Dinosaurio:
    def __init__(self, alto=ALTO_DINO, ancho=ANCHO_DINO, color=COLOR_DINO):
        self.x = 50
        self.y = SUELO_Y
        self.alto = alto
        self.ancho = ancho
        self.color = color
        self.vel_y = 0
        self.saltando = False
        self.vivo = True
        self.score = 0
        self.rect = pg.Rect(self.x, self.y - self.alto, self.ancho, self.alto)

    def update(self):
        if not self.vivo: return

        # Física
        self.vel_y += 0.8
        self.y += self.vel_y
        if self.y >= SUELO_Y:
            self.y = SUELO_Y
            self.vel_y = 0
            self.saltando = False
        self.rect.y = self.y - self.alto

        self.score += 1

    def saltar(self):
        if not   self.saltando:
            self.vel_y = -15
            self.saltando = True

    def dibujar(self, screen):
        if self.vivo:
            pg.draw.rect(screen, self.color, self.rect)