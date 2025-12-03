from ProyectoIntegrador.src.settings import ANCHO_OBS, ALTO_OBS, SUELO_Y
import random as rand
import pygame as pg

class Obstaculo:
    def __init__(self, ancho=ANCHO_OBS, alto=ALTO_OBS, x=0):
        self.ancho = rand.randint(ancho[0], ancho[1]) # tupla (mínimo, máximo)
        self.alto = rand.randint(alto[0], alto[1]) # tupla (mínimo, máximo)
        self.rect = pg.Rect(x, SUELO_Y - self.alto, self.ancho, self.alto)

    def update(self, velocidad):
        self.rect.x -= velocidad

    def dibujar(self, screen):
        pg.draw.rect(screen, (0, 0, 0), self.rect)