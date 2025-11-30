import sys
import os
import json  # Procesar la salida de Vosk
import vosk
import pyaudio
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, Qt, QThread, pyqtSignal  # NUEVO: QThread y pyqtSignal

# Reconocimiento de voz
class VoiceThread(QThread):
    # Este hilo maneja la escucha del micrófono y el reconocimiento de voz

    command_received = pyqtSignal(str)  # Señal para enviar comandos a la GUI

    def __init__(self, model_path):
        super().__init__()
        self.model_path = model_path
        self.running = True

    def run(self):
        try:
            model = vosk.Model(self.model_path)
            # Lista de palabras clave para mejorar la precisión
            keywords = ["prender", "apagar", "subir", "bajar", "volumen"]
            recognizer = vosk.KaldiRecognizer(model, 16000, json.dumps(keywords))

            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=16000,
                            input=True,
                            frames_per_buffer=8192)

            print("=== Escuchando comandos de voz... ===")

            while self.running:
                data = stream.read(4096, exception_on_overflow=False)
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get('text', '').lower()

                    if text:
                        print(f"Voz reconocida: '{text}'")
                        if "prender" in text:
                            self.command_received.emit("prender")
                        elif "apagar" in text:
                            self.command_received.emit("apagar")
                        elif "subir" in text:  # Captura "subir" o "subir volumen"
                            self.command_received.emit("subir")
                        elif "bajar" in text:  # Captura "bajar" o "bajar volumen"
                            self.command_received.emit("bajar")
        except Exception as e:
            print(f"Error en el hilo de voz: {e}")
        finally:
            if 'stream' in locals() and stream.is_active():
                stream.stop_stream()
                stream.close()
            if 'p' in locals():
                p.terminate()
            print("=== Hilo de voz detenido. ===")

    def stop(self):
        """Detiene el hilo de forma segura."""
        self.running = False
        self.wait()


# Clase principal del Televisor
class Televisor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Televisor con Audio y Voz")  # Título modificado

        # Ruta segura del archivo de audio
        audio_path = os.path.abspath("Audio de WhatsApp 2025-09-30 a las 10.07.08_d619cf8f.wav")

        # Reproductor de audio
        self.player = QMediaPlayer()
        if os.path.exists(audio_path):
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(audio_path)))
            self.player.error.connect(self.handle_error)
        else:
            print("Error: El archivo de audio no se encuentra en la ruta especificada.")
            print(f"Ruta buscada: {audio_path}")

        # --- Configuración original de la GUI (imágenes, botones, slider) ---
        self.Encendido = QLabel()
        self.Encendido.setPixmap(QPixmap("Full-HD-LED-TV-PNG-Transparent-HD-Photo.png"))
        self.Encendido.setScaledContents(True)
        self.Encendido.setFixedSize(400, 300)

        self.Apagada = QLabel()
        self.Apagada.setPixmap(QPixmap("black-television-illustration-black-television-vector-free-png.png"))
        self.Apagada.setScaledContents(True)
        self.Apagada.setFixedSize(400, 300)
        self.Apagada.hide()

        self.boton_encendido = QPushButton("Enciende o apaga la tele")
        self.boton_encendido.clicked.connect(self.alternar_imagen)

        self.boton_subir_volumen = QPushButton("Subir Volumen")
        self.boton_subir_volumen.clicked.connect(self.subir_volumen)
        self.boton_bajar_volumen = QPushButton("Bajar Volumen")
        self.boton_bajar_volumen.clicked.connect(self.bajar_volumen)

        self.slider_volumen = QSlider(Qt.Horizontal)
        self.slider_volumen.setRange(0, 100)
        self.slider_volumen.setValue(50)
        self.slider_volumen.valueChanged.connect(self.cambiar_volumen)
        self.player.setVolume(50)

        # --- Layout original ---
        layout = QVBoxLayout()
        layout.addWidget(self.Encendido)
        layout.addWidget(self.Apagada)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.boton_encendido)
        button_layout.addWidget(self.boton_bajar_volumen)
        button_layout.addWidget(self.boton_subir_volumen)

        layout.addLayout(button_layout)
        layout.addWidget(self.slider_volumen)

        # --- Integración de Voz ---

        # Etiqueta para dar feedback de voz
        self.voice_status_label = QLabel("Diga 'prender', 'apagar', 'subir volumen' o 'bajar volumen'")
        self.voice_status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.voice_status_label)

        self.setLayout(layout)

        # Estado inicial: apagado
        self.Encendido.hide()
        self.Apagada.show()

        # Iniciar el hilo de voz
        model_path = "vosk-model-small-es-0.42"  # Ruta a tu modelo
        self.voice_thread = VoiceThread(model_path)
        self.voice_thread.command_received.connect(self.handle_voice_command)
        self.voice_thread.start()

    # Funcion de comandos de voz ---
    def handle_voice_command(self, command):
        """Actúa según el comando de voz recibido del hilo."""
        print(f"Comando de voz procesando: {command}")

        if command == "prender":
            if self.Apagada.isVisible():  # Solo si está apagada
                self.alternar_imagen()
                self.voice_status_label.setText("Comando: ENCENDER")
            else:
                self.voice_status_label.setText("La TV ya estaba encendida.")

        elif command == "apagar":
            if self.Encendido.isVisible():  # Solo si está encendida
                self.alternar_imagen()
                self.voice_status_label.setText("Comando: APAGAR")
            else:
                self.voice_status_label.setText("La TV ya estaba apagada.")

        elif command == "subir":
            self.subir_volumen()
            self.voice_status_label.setText(f"Volumen: {self.player.volume()}")

        elif command == "bajar":
            self.bajar_volumen()
            self.voice_status_label.setText(f"Volumen: {self.player.volume()}")

    # Funciones originales
    def handle_error(self):
        print("Error en el reproductor de audio:", self.player.errorString())

    def alternar_imagen(self):
        if self.Encendido.isVisible():
            self.Encendido.hide()
            self.Apagada.show()
            self.player.stop()
        else:
            self.Encendido.show()
            self.Apagada.hide()
            self.player.setPosition(0)
            self.player.play()

    def subir_volumen(self):
        volumen_actual = self.player.volume()
        if volumen_actual < 100:
            nuevo_volumen = min(volumen_actual + 10, 100)
            self.player.setVolume(nuevo_volumen)
            self.slider_volumen.setValue(nuevo_volumen)
            print(f"Volumen subido a: {nuevo_volumen}")

    def bajar_volumen(self):
        volumen_actual = self.player.volume()
        if volumen_actual > 0:
            nuevo_volumen = max(volumen_actual - 10, 0)
            self.player.setVolume(nuevo_volumen)
            self.slider_volumen.setValue(nuevo_volumen)
            print(f"Volumen bajado a: {nuevo_volumen}")

    def cambiar_volumen(self, valor):
        self.player.setVolume(valor)

    # Detiene los hilos
    def closeEvent(self, event):
        print("Cerrando aplicación y deteniendo hilo de voz...")
        self.voice_thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Televisor()
    ventana.show()
    sys.exit(app.exec_())