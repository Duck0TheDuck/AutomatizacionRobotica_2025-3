import random
import numpy as np
from ProyectoIntegrador.src.settings import POBLACION_TAMANO, PROBABILIDAD_MUTACION, VARIACION_MUTACION
from modelo import crear_modelo
from ProyectoIntegrador.src.training.entities.dinosaurio_evo import DinosaurioEvo


def evolucionar_poblacion(dinos_muertos):
    """Algoritmo Genético usando pesos de modelos Keras."""
    print("--- Evolucionando (TensorFlow) ---")

    # Ordenar por fitness
    dinos_muertos.sort(key=lambda x: x.score, reverse=True)
    mejor_dino = dinos_muertos[0]
    print(f"Mejor Score: {mejor_dino.score}")

    nueva_poblacion = []

    # 1. ELITISMO: Clonar al mejor
    # (En Keras hay que crear uno nuevo y copiarle los pesos manualmente)
    mejor_modelo = crear_modelo()
    mejor_modelo.set_weights(mejor_dino.cerebro.get_weights())
    nueva_poblacion.append(DinosaurioEvo(modelo=mejor_modelo))

    # 2. REPRODUCCIÓN
    while len(nueva_poblacion) < POBLACION_TAMANO:
        padre1 = random.choice(dinos_muertos[:8])  # Top 8
        padre2 = random.choice(dinos_muertos[:8])

        # Cruzar cerebros
        pesos_hijo = cruzar_pesos(padre1.cerebro.get_weights(),
                                  padre2.cerebro.get_weights())

        # Crear dino nuevo y asignarle los pesos mutados
        modelo_hijo = crear_modelo()
        modelo_hijo.set_weights(pesos_hijo)
        nueva_poblacion.append(DinosaurioEvo(modelo=modelo_hijo))

    return nueva_poblacion, mejor_modelo


def cruzar_pesos(pesos_p1, pesos_p2):
    """
    Recibe listas de matrices de numpy (que vienen de get_weights).
    Devuelve una nueva lista con los pesos mezclados y mutados.
    """
    nuevos_pesos = []

    for w1, w2 in zip(pesos_p1, pesos_p2):
        # w1 y w2 son matrices de pesos o vectores de bias

        # 1. Cruce (Crossover Uniforme)
        mask = np.random.rand(*w1.shape) > 0.5
        hijo_w = np.where(mask, w1, w2)

        # 2. Mutación
        if random.random() < PROBABILIDAD_MUTACION:
            noise = np.random.normal(0, VARIACION_MUTACION, w1.shape)
            hijo_w = hijo_w + noise

        nuevos_pesos.append(hijo_w)

    return nuevos_pesos