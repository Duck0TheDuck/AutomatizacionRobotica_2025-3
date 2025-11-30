import os
#from tensorflow.keras .... o .... from tensorflow.python.keras ...
#from keras.preprocessing.image import ImageDataGenerator  # preprocesamiento de imagenes
from keras import optimizers # algoritmos para entrenar
from keras.models import Sequential # para crear redes neuronales secuenciales
from keras.layers import Dropout, Flatten, Dense, Activation #
from keras.layers import Convolution2D, MaxPooling2D # capaz de la red neuronal
from tensorflow.keras import backend as K
from keras.src.legacy.preprocessing.image import ImageDataGenerator

K.clear_session()
def train():
    data_entrenamiento = "../F1-Entrenamiento"
    data_validacion = "../F2-Validación"

    #Parametros
    epocas = 5
    alto, largo = 300, 300 #dimensiones de las imagenes. Para redimenzionar
    batch_size = 5 #numero de imagenes que se mandara a procesar por cada paso
    pasos = 35  # 100imagenes / batch => max pasos
    pasos_validacion = 15 # 50imagenes /batcg => max pasos validacion

    #To make sure that you have "at least steps_per_epoch * epochs batches", set the steps_per_epoch to
    #steps_per_epoch = len(X_train)//batch_size
    #validation_steps = len(X_test)//batch_size # if you have validation data
    ############

    kernel1 = (3, 3)
    kernel2 = (2, 2)
    kernel3 = (3, 3)

    tot_kernels1 = 48  #8 ....
    tot_kernels2 = 64
    tot_kernels3 = 128

    stride = (2, 2) #para MaxPooling

    clases = 3 #total de clases a clasificar

    lr = 0.0005 #learning rate  # 0.1 ---- 0.01   0.001  0.002



    #preprocesamiento de imagenes  --> aumento de datos...

    entrenamiento_datagen = ImageDataGenerator(
        rescale=1./255, # cada px va de 0 a 255, con esto se pasara al rango de 0 a 1, para procesar mas facil
        shear_range=0.3, #inclinacion
        zoom_range= 0.3,
        vertical_flip=True,
        horizontal_flip=True #inversion horizontal
    )

    validacion_datagen = ImageDataGenerator(
        rescale=1./255
    )

    imagen_entrenamiento = entrenamiento_datagen.flow_from_directory(
        data_entrenamiento,
        target_size= (alto, largo),
        batch_size=batch_size,
        class_mode='categorical',
        color_mode="grayscale"
    )

    imagen_validacion = validacion_datagen.flow_from_directory(
        data_validacion,
        target_size=(alto, largo),
        batch_size=batch_size,
        class_mode='categorical',
        color_mode="grayscale"
    )

    #red convolucional

    cnn = Sequential()

    ##capa 1
    cnn.add(Convolution2D(tot_kernels1, kernel1, padding='same', input_shape=(alto, largo, 1), activation='relu'))
    ##capa 2
    cnn.add(MaxPooling2D(pool_size=stride))
    ##capa 3
    cnn.add(Convolution2D(tot_kernels2, kernel2, padding='same', activation='relu'))
    ##capa 4
    cnn.add(MaxPooling2D(pool_size=stride))
    ##capa 5
    cnn.add(Convolution2D(tot_kernels3, kernel3, padding='same', activation='relu'))
    ##capa 6
    cnn.add(MaxPooling2D(pool_size=stride))



    cnn.add(Flatten()) # aplana la informacion

    ##capa 7
    cnn.add(Dense(256, activation='relu')) #

    # 0.2 - 0.6
    cnn.add(Dropout(0.2)) #porcentaje de neuronas apagadas en cada paso (0.5 = 50%)
    # permite aprender caminos alternos para clasificar.. evita sobreentrenamiento

    #capa 8 - salida
    cnn.add(Dense(clases, activation='softmax'))

    cnn.compile(loss='categorical_crossentropy', optimizer=optimizers.Adam(learning_rate=lr), metrics=['accuracy'])
    #cnn.compile(loss='binary_crossentropy', optimizer=optimizers.Adam(learning_rate=lr), metrics=['accuracy'])
    #loss -> funcion de perdida

    #entrena el modelo de la red neuronal
    cnn.fit(imagen_entrenamiento,
            epochs=epocas,
            validation_data=imagen_validacion)

    dir = "../modelo/E4_ConvolutionalNeuronalNetwork/modelo"
    os.makedirs(dir, exist_ok=True)


    cnn.save(dir + 'modelo.keras') #estructura
    cnn.save_weights(dir + 'pesos.weights.h5') #pesos en las capas
if __name__== '__main__':
    train()