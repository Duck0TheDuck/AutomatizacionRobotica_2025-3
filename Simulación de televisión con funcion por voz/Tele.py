from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, Qt
import sys
import os

class Televisor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Televisor con Audio")

        # Ruta segura del archivo de audio
        audio_path = os.path.abspath("Audio de WhatsApp 2025-09-30 a las 10.07.08_d619cf8f.wav")

        # Reproductor de audio
        self.player = QMediaPlayer()
        if os.path.exists(audio_path):
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(audio_path)))
            # Conectar la señal de error para depuración
            self.player.error.connect(self.handle_error)
        else:
            print("Error: El archivo de audio no se encuentra en la ruta especificada.")
            print(f"Ruta buscada: {audio_path}")

        # Imagen encendida
        self.Encendido = QLabel()
        self.Encendido.setPixmap(QPixmap("Full-HD-LED-TV-PNG-Transparent-HD-Photo.png"))
        self.Encendido.setScaledContents(True)
        self.Encendido.setFixedSize(400, 300)

        # Imagen apagada
        self.Apagada = QLabel()
        self.Apagada.setPixmap(QPixmap("black-television-illustration-black-television-vector-free-png.png"))
        self.Apagada.setScaledContents(True)
        self.Apagada.setFixedSize(400, 300)
        self.Apagada.hide()

        # Botón para alternar
        self.boton_encendido = QPushButton("Enciende o apaga la tele")
        self.boton_encendido.clicked.connect(self.alternar_imagen)

        # Botones de volumen
        self.boton_subir_volumen = QPushButton("Subir Volumen")
        self.boton_subir_volumen.clicked.connect(self.subir_volumen)
        self.boton_bajar_volumen = QPushButton("Bajar Volumen")
        self.boton_bajar_volumen.clicked.connect(self.bajar_volumen)

        # Slider de volumen
        self.slider_volumen = QSlider(Qt.Horizontal)
        self.slider_volumen.setRange(0, 100)
        self.slider_volumen.setValue(50)
        self.slider_volumen.valueChanged.connect(self.cambiar_volumen)
        self.player.setVolume(50)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.Encendido)
        layout.addWidget(self.Apagada)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.boton_encendido)
        button_layout.addWidget(self.boton_bajar_volumen)
        button_layout.addWidget(self.boton_subir_volumen)

        layout.addLayout(button_layout)
        layout.addWidget(self.slider_volumen)
        self.setLayout(layout)

        # Estado inicial: apagado
        self.Encendido.hide()
        self.Apagada.show()

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
            # Asegurarse de que el audio se reproduce desde el principio
            self.player.setPosition(0)
            self.player.play()

    def subir_volumen(self):
        volumen_actual = self.player.volume()
        if volumen_actual < 100:
            self.player.setVolume(volumen_actual + 10)
            self.slider_volumen.setValue(volumen_actual + 10)

    def bajar_volumen(self):
        volumen_actual = self.player.volume()
        if volumen_actual > 0:
            self.player.setVolume(volumen_actual - 10)
            self.slider_volumen.setValue(volumen_actual - 10)

    def cambiar_volumen(self, valor):
        self.player.setVolume(valor)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Televisor()
    ventana.show()
    sys.exit(app.exec_())