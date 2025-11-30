import cv2  # opencv

cam = cv2.VideoCapture(0)  # videocámara
contFotos = 0  # contador inicial de fotos

face_classifier = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def face_detect_box(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray_image, 1.1, 5, minSize=(40, 40))
    faces_frames = []
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 4)
        aux = image.copy()
        faces_frames.append(aux[y:y+h, x:x+w])
    return faces, faces_frames

while True:
    result, image = cam.read()
    if result:
        faces_detected, img_faces = face_detect_box(image)
        cv2.imshow("Camara_Principal", image)

        res = cv2.waitKey(1)

        if res == ord("q"):
            cam.release()
            cv2.destroyWindow("Camara_Principal")
            break

        elif res == ord(" "):  # al presionar espacio
            fotosTomadas = 0
            while fotosTomadas < 500:
                ret, image = cam.read()
                if not ret:
                    print("Error al capturar imagen.")
                    break

                faces_detected, img_faces = face_detect_box(image)
                cv2.imshow("Camara_Principal", image)

                if len(img_faces) == 0:
                    cv2.imwrite("foto_" + str(contFotos) + ".png", image)
                    contFotos += 1
                    fotosTomadas += 1
                else:
                    for img in img_faces:
                        imagen_cara = cv2.resize(img, (400, 400), interpolation=cv2.INTER_CUBIC)
                        cv2.imwrite("foto_" + str(contFotos) + ".png", imagen_cara)
                        contFotos += 1
                        fotosTomadas += 1
                        if fotosTomadas >= 300:
                            break

                cv2.waitKey(50)  # espera entre capturas

    else:
        print("No image detected. Please! try again")
        break