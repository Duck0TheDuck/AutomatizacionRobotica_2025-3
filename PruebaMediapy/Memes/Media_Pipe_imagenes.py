import cv2
import mediapipe as mp
import math
import os
import numpy as np

# --- CONFIGURACIÓN DE MEDIAPIPE ---
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.7,
                       min_tracking_confidence=0.5)

def cargar_imagen_segura(nombre_archivo, texto_alt, color_alt):
    # Obtener directorio
    directorio_script = os.path.dirname(os.path.abspath(__file__))

    # Subir un nivel a la carpeta padre
    directorio_padre = os.path.dirname(directorio_script)

    # Entrar a la carpeta de imágenes
    ruta_final = os.path.join(directorio_padre, "Memes_repositorio", nombre_archivo)

    img = cv2.imread(ruta_final)

    if img is not None:
        print(f"Imagen cargada: {ruta_final}")
        return img
    else:
        # Crear imagen de respaldo si falla
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        img[:] = color_alt
        return img


# --- CARGA DE IMÁGENES ---

img_indice = cargar_imagen_segura("OIP.jpeg", "SENALANDO", (255, 0, 0))
img_menton = cargar_imagen_segura("Gato con mano en el menton.jpg", "PENSANDO", (0, 255, 255))
img_pelea = cargar_imagen_segura("Gato peleador.jpeg", "PELEA!!!", (0, 0, 255))

# --- NUEVAS IMÁGENES AGREGADAS ---
img_silencio = cargar_imagen_segura("Changuito silencio.jpg", "SHHH", (100, 100, 100))
img_traka = cargar_imagen_segura("Perrito traka.jpg", "TRAKA", (203, 192, 255)) # Color lila

print("-------------------------")

#Superpone las imagenes sobre la imagen de video
def superponer_imagen(frame, imagen_overlay, pos=(10, 50), tamaño=(200, 200)):
    try:
        overlay = cv2.resize(imagen_overlay, tamaño)
        h, w, _ = overlay.shape
        rows, cols, _ = frame.shape
        x, y = pos
        if y + h > rows or x + w > cols: return frame
        frame[y:y + h, x:x + w] = overlay
    except Exception:
        pass
    return frame

#Mide la distnacia de los puntos para la imagen del gatito peleador
def calcular_distancia(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


def contar_dedos_lista(hand_landmarks):
    dedos = []
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]

    # Pulgar
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        dedos.append(1)
    else:
        dedos.append(0)

    # Otros dedos
    for tip, pip in zip(tips, pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            dedos.append(1)
        else:
            dedos.append(0)
    return dedos


# Bucle Main
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    meme_a_mostrar = None
    texto_estado = ""

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # DETECTAR Arresto
        if len(results.multi_hand_landmarks) == 2:
            p1 = results.multi_hand_landmarks[0].landmark[0]
            p2 = results.multi_hand_landmarks[1].landmark[0]
            dist = calcular_distancia(p1, p2)

            if dist < 0.25:
                meme_a_mostrar = img_pelea
                texto_estado = "Arrestado"
            else:
                texto_estado = "Manos separadas"

        # GESTOS DE UNA MANO
        elif len(results.multi_hand_landmarks) >= 1:
            lm = results.multi_hand_landmarks[0]
            dedos = contar_dedos_lista(lm) # [Pulgar, Indice, Medio, Anular, Meñique]

            # TRAKA
            if dedos == [1, 0, 0, 0, 1]:
                meme_a_mostrar = img_traka
                texto_estado = "TRAKA !!!"

            # 2. SILENCIO
            elif dedos == [0, 1, 1, 0, 0] or dedos == [1, 1, 1, 0, 0]:
                meme_a_mostrar = img_silencio
                texto_estado = "SHHH..."

            # 3. DE HECHO
            elif dedos[1] == 1 and sum(dedos[2:]) == 0:
                meme_a_mostrar = img_indice
                texto_estado = "Actually"

            # 4. Pensando
            elif sum(dedos) == 0 or dedos == [1, 1, 0, 0, 0]:
                meme_a_mostrar = img_menton
                texto_estado = "MMMM"

    if meme_a_mostrar is not None:
        frame = superponer_imagen(frame, meme_a_mostrar, pos=(10, 10))

    if texto_estado:
        cv2.putText(frame, texto_estado, (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Detector de Gestos', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()