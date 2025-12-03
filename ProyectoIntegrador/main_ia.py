import pygame
import sys
import random as rand
from keras.models import load_model
from ProyectoIntegrador.src.settings import ANCHO_PANTALLA, ALTO_PANTALLA, SUELO_Y, MODEL_NAME
from ProyectoIntegrador.src.training.entities.dinosaurio_evo import DinosaurioEvo
from ProyectoIntegrador.src.entities.obstaculo import Obstaculo

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption("Dino IA - FASE DE PRUEBA")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)

    # --- 1. CARGAR EL MODELO ---
    path = './src/training/model/'
    model_name = path + f"{MODEL_NAME}.keras"
    print(f"Cargando cerebro desde: {model_name}...")

    try:
        modelo_cargado = load_model(model_name)
        print("¡ÉXITO! Modelo cargado.")
    except Exception as e:
        print(f"\n[ERROR CRÍTICO] No se pudo cargar '{model_name}'.")
        print("Asegúrate de que el entrenamiento (main.py) terminó y creó el archivo.")
        print(f"Detalle técnico: {e}")
        try:
            print("Intentando cargar backup_dino.keras...")
            modelo_cargado = load_model("backup_dino.keras")
            print("¡Backup cargado!")
        except:
            sys.exit()

    # --- 2. PREPARAR EL JUEGO ---
    dino = DinosaurioEvo(modelo=modelo_cargado)

    obstaculos = [Obstaculo(x=ANCHO_PANTALLA + 200)]
    game_speed = 10
    score = 0

    corriendo = True
    while corriendo:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                corriendo = False

        # Dibujar Fondo
        pantalla.fill((255, 255, 255))
        pygame.draw.line(pantalla, (0, 0, 0), (0, SUELO_Y), (ANCHO_PANTALLA, SUELO_Y))

        # --- LÓGICA DEL JUEGO ---
        # Generar obstáculos
        if len(obstaculos) == 0 or obstaculos[-1].rect.x < ANCHO_PANTALLA - 400:
            if rand.randint(0, 100) < 5:
                obstaculos.append(Obstaculo(x=ANCHO_PANTALLA + rand.randint(50, 300)))

        # Actualizar obstáculos
        for obs in obstaculos:
            obs.update(game_speed)
            obs.dibujar(pantalla)
            if obs.rect.right < 0:
                obstaculos.remove(obs)

        # Actualizar Dino (predicción)
        if dino.vivo:
            dino.update(obstaculos, game_speed)
            dino.dibujar(pantalla)
            score += 1

            # Detección de Colisión
            for obs in obstaculos:
                if dino.rect.colliderect(obs.rect):
                    dino.vivo = False
                    print(f"--> El dino chocó. Score final: {score}")

        else:
            print("--- Reiniciando partida de prueba ---")
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