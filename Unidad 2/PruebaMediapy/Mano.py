import cv2
import mediapipe as mp

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=1,
                       min_detection_confidence=0.7,
                       min_tracking_confidence=0.5)

# Función para contar dedos levantados
def contar_dedos(hand_landmarks):
    dedos_levantados = 0
    dedos_tips = [8, 12, 16, 20]  # Índice, medio, anular, meñique
    dedos_pips = [6, 10, 14, 18]

    # Pulgar (comparación horizontal)
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        dedos_levantados += 1

    # Otros dedos (comparación vertical)
    for tip, pip in zip(dedos_tips, dedos_pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            dedos_levantados += 1

    return dedos_levantados

# Captura de video
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            dedos = contar_dedos(hand_landmarks)
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            cv2.putText(frame, f'Dedos levantados: {dedos}', (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Contador de dedos', frame)

   #Cerrar programa

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()