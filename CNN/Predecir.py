import os
import numpy as np
# 1. Importaciones corregidas
from tensorflow.keras.utils import load_img, img_to_array
from tensorflow.keras.models import load_model

# 2. Rutas corregidas y carga de modelo simplificada
alto, largo = 300, 300
modelo = "E4_ConvolutionalNeuronalNetwork/modelo/modelomodelo.keras"

# load_model carga la arquitectura Y los pesos.
cnn = load_model(modelo)

print("¡Modelo cargado exitosamente!")


def predict(file):
    imagen_a_predecir = load_img(file, target_size=(alto, largo), color_mode="grayscale")
    imagen_a_predecir = img_to_array(imagen_a_predecir)

    # Escala los datos de [0, 255] a [0, 1]
    imagen_a_predecir = imagen_a_predecir / 255.0

    imagen_a_predecir = np.expand_dims(imagen_a_predecir, axis=0)

    arreglo = cnn.predict(imagen_a_predecir, verbose=0)
    resultado = arreglo[0]
    respuesta = np.argmax(resultado)

    # carpetas
    match respuesta:
        case 0:
            return 'C1-Ap1Ap2'
        case 1:
            return 'C2-Clase2'
        case 2:
            return 'C3-Clase3'
        case _:
            return '----'


def get_folders_name_from(from_location):
    list_dir = os.listdir(from_location)
    folders = []
    for file in list_dir:
        temp = os.path.splitext(file)
        if temp[1] == "":
            folders.append(temp[0])
    folders.sort()


    return folders


def probar_red_neuronal():
    # 3. Ruta de prueba corregida
    base_location = "../F3-Prueba/"

    folders = get_folders_name_from(base_location)
    print(f"Probando con carpetas: {folders}")

    correct = 0
    count_predictions = 0
    for folder in folders:
        # Usamos os.path.join para unir rutas de forma segura
        folder_path = os.path.join(base_location, folder)

        try:
            # endswith acepta una tupla de extensiones
            files = [archivo for archivo in os.listdir(folder_path) if archivo.endswith((".jpg", ".jpeg", ".png"))]
        except FileNotFoundError:
            print(f"Error: No se encontró la carpeta {folder_path}")
            continue

        for file in files:
            composed_location = os.path.join(folder_path, file)
            prediction = predict(composed_location)

            # Comprueba si el nombre de la predicción está contenido en el nombre de la carpeta
            is_correct = prediction in folder
            print(f'Archivo: {file}, Predicción: {prediction}, ¿Correcto?: {is_correct}')

            count_predictions += 1
            if is_correct:
                correct += 1

    if count_predictions > 0:
        eficiencia = (correct / count_predictions * 100)
        print("---------------------------------")
        print(f"Total de predicciones: {count_predictions}")
        print(f"Correctas: {correct}")
        print(f"Eficiencia: {eficiencia:.2f}%")  # .2f para 2 decimales
    else:
        print("No se encontraron imágenes para probar.")


# Ejecutar la prueba
probar_red_neuronal()