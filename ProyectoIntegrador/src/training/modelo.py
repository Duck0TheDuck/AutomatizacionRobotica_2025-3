import os
import tensorflow as tf
from keras import Sequential
from keras.layers import Dense
from keras.models import load_model
from ProyectoIntegrador.src.settings import INPUT_NODES, HIDDEN_NODES, OUTPUT_NODES

# Desactivar logs molestos de TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


def crear_modelo():
    """Crea una Red Neuronal MLP usando Keras."""
    model = Sequential([
        # Capa Oculta (Dense) con activación ReLU
        Dense(HIDDEN_NODES, input_shape=(INPUT_NODES,), activation='relu'),

        # Capa de Salida (Dense) con activación Sigmoide (0 a 1)
        Dense(OUTPUT_NODES, activation='sigmoid')
    ])

    model.compile(loss='mse', optimizer='adam')
    return model


def predecir_accion(model, inputs):
    """Realiza la inferencia (predicción) de forma eficiente."""
    # Convertir inputs a Tensor (Forma: 1x6)
    input_tensor = tf.convert_to_tensor([inputs], dtype=tf.float32)

    # Usamos model(input) en lugar de model.predict() porque es más rápido dentro de bucles
    prediccion = model(input_tensor, training=False)

    # Devolver el valor numérico (ej. 0.85)
    return prediccion.numpy()[0][0]


def guardar_modelo_keras(model, nombre_base="dino_modelo"):
    """Guarda el modelo en los formatos .keras y .weights.h5"""
    try:
        # Guardar modelo completo
        model.save(f"{nombre_base}.keras")
        # Guardar solo los pesos (lo que pediste del H5)
        model.save_weights(f"{nombre_base}.weights.h5")
        print(f"--> Guardado: {nombre_base}.keras y {nombre_base}.weights.h5")
    except Exception as e:
        print(f"Error guardando modelo: {e}")


def cargar_modelo_keras(ruta_modelo):
    """Carga un modelo .keras existente"""
    return load_model(ruta_modelo)