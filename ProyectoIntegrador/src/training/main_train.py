import pygame
import sys
import random as rand
from ProyectoIntegrador.src.settings import ANCHO_PANTALLA, ALTO_PANTALLA, SUELO_Y, FPS, POBLACION_TAMANO, MODO_VISUAL, MAX_GENERACIONES, MODEL_NAME
from ProyectoIntegrador.src.training.entities.dinosaurio_evo import DinosaurioEvo
from ProyectoIntegrador.src.entities.obstaculo import Obstaculo
from genetica import evolucionar_poblacion
from modelo import guardar_modelo_keras


def main():
    path = './model/'
    model_name = path + MODEL_NAME
    if MODO_VISUAL:
        pygame.init()
        pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
        pygame.display.set_caption("Dino IA - Entrenamiento")
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 30)
    else:
        print("--- INICIANDO EN MODO 2DO PLANO (SIN VENTANA) ---")
        print("Esto entrenará mucho más rápido y consumirá menos recursos.")

    # Población inicial
    dinos = [DinosaurioEvo() for _ in range(POBLACION_TAMANO)]
    dinos_muertos = []

    obstaculos = [Obstaculo(x=ANCHO_PANTALLA + 200)]
    game_speed = 10
    generacion = 1
    mejor_modelo_global = None

    ejecutando = True
    while ejecutando:
        if MODO_VISUAL:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    ejecutando = False
                    if mejor_modelo_global:
                        guardar_modelo_keras(mejor_modelo_global, model_name)

            pantalla.fill((255, 255, 255))
            pygame.draw.line(pantalla, (0, 0, 0), (0, SUELO_Y), (ANCHO_PANTALLA, SUELO_Y))

        # --- Lógica del Juego ---
        if len(obstaculos) == 0 or obstaculos[-1].rect.x < ANCHO_PANTALLA - 400:
            if rand.randint(0, 100) < 5:
                obstaculos.append(Obstaculo(x=ANCHO_PANTALLA + rand.randint(50, 300)))

        # Mover Obstáculos
        for obs in obstaculos:
            obs.update(game_speed)
            if MODO_VISUAL: obs.dibujar(pantalla)
            if obs.rect.right < 0:
                obstaculos.remove(obs)

        # Mover Dinos
        vivos_actuales = 0
        for dino in dinos:
            if dino.vivo:
                vivos_actuales += 1
                dino.update(obstaculos, game_speed)
                if MODO_VISUAL: dino.dibujar(pantalla)

                for obs in obstaculos:
                    if dino.rect.colliderect(obs.rect):
                        dino.vivo = False
                        dinos_muertos.append(dino)

        game_speed += 0.005
        if game_speed > 30: game_speed = 30

        # --- NUEVA GENERACIÓN ---
        if vivos_actuales == 0:
            if generacion >= MAX_GENERACIONES:
                print(f"--- META ALCANZADA: {generacion} GENS ---")
                if mejor_modelo_global: guardar_modelo_keras(mejor_modelo_global, model_name)
                ejecutando = False
                break

            dinos, mejor_modelo_gen = evolucionar_poblacion(dinos_muertos)
            mejor_modelo_global = mejor_modelo_gen

            print(f"Gen: {generacion} Completada. Mejor Score: {int(dinos_muertos[0].score)}")

            dinos_muertos = []
            obstaculos = [Obstaculo(x=ANCHO_PANTALLA + 200)]
            game_speed = 10
            generacion += 1

        if MODO_VISUAL:
            txt = font.render(f"Gen: {generacion} | Vivos: {vivos_actuales} | Vel: {game_speed:.1f}", True, (0, 0, 0))
            pantalla.blit(txt, (10, 10))
            pygame.display.flip()
            clock.tick(FPS)

    if MODO_VISUAL: pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()