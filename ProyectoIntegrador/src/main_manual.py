import pygame
import sys
import random as rand
from settings import ANCHO_PANTALLA, ALTO_PANTALLA, SUELO_Y
from ProyectoIntegrador.src.entities.dinosaurio import Dinosaurio
from ProyectoIntegrador.src.entities.obstaculo import Obstaculo

def main():
    # Inicializar Pygame (Forzamos visualización aquí)
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption("Dino Chrome Manual")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)

    dino = Dinosaurio()
    obstaculos = [Obstaculo(x=ANCHO_PANTALLA + 200)]
    game_speed = 10
    score = 0

    corriendo = True
    while corriendo:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                corriendo = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    dino.saltar()

        # Dibujar Fondo
        pantalla.fill((255, 255, 255))
        pygame.draw.line(pantalla, (0, 0, 0), (0, SUELO_Y), (ANCHO_PANTALLA, SUELO_Y))

        # --- LÓGICA DEL JUEGO---
        # Generar obstáculos
        if len(obstaculos) == 0 or obstaculos[-1].rect.x < ANCHO_PANTALLA - 400:
            if rand.randint(0, 100) < 5:
                obstaculos.append(Obstaculo(x= ANCHO_PANTALLA + rand.randint(50, 300)))

        # Actualizar obstáculos
        for obs in obstaculos:
            obs.update(game_speed)
            obs.dibujar(pantalla)
            if obs.rect.right < 0:
                obstaculos.remove(obs)

        if dino.vivo:
            dino.update( )
            dino.dibujar(pantalla)
            score += 1

            # Detección de Colisión
            for obs in obstaculos:
                if dino.rect.colliderect(obs.rect):
                    dino.vivo = False
                    print(f"--> El dino chocó. Score final: {score}")
        else:
            print("--- Reiniciando partida ---")
            dino.vivo = True
            dino.rect.y = SUELO_Y - dino.alto
            dino.y = SUELO_Y
            dino.vel_y = 0
            dino.saltando = False

            obstaculos = [Obstaculo(x=ANCHO_PANTALLA + 200)]
            game_speed = 10
            score = 0

        game_speed += 0.005
        if game_speed > 30: game_speed = 30

        txt = font.render(f"Score: {score} | Vel: {game_speed:.1f}", True, (0, 0, 0))
        pantalla.blit(txt, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()