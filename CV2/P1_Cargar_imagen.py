from keras.src.utils import load_img, img_to_array

Largo, alto = 150, 150
#Largo alto = 600, 600

file = "cover3.jpg"
img = load_img(file,target_size=(Largo,alto))

print(img.size)
print(img.mode)

imagen_en_array = img_to_array(img)
print(imagen_en_array.shape)

archivo = open(("./array_imagen_en_datos.csv", "w"))

for i in imagen_en_array:
    for j in i:
        archivo.write(str(j[0])+",")
        archivo.write("n")
archivo.flush()
archivo.close()

img.show





