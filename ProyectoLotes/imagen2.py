import cv2
import numpy as np

# 1. Leer la imagen en modo blanco y negro (escala de grises)
imagen = cv2.imread('images.jpeg', cv2.IMREAD_GRAYSCALE)
if imagen is None:
    print("Error: No se pudo cargar la imagen.")
    exit()

# 2. Definir el valor de umbral (ej: 128)
umbral = 128

# 3. Crear una nueva imagen para almacenar los resultados
#Devuelve una tupla con la estructura (altura, ancho)para imágenes en escala de grises (1 canal).
altura, ancho = imagen.shape

#Crea una matriz negra del mismo tamaño que la imagen original. dtype=np.uint8: Tipo de dato sin signo de 8 bits (0 a 255).
#np es de la numpy no opencv
imagen_umbralizada = np.zeros((altura, ancho), dtype=np.uint8)

# 4. Aplicar umbral manualmente usando bucles for anidados
#    Recorre cada píxel de la imagen original.
#    Asigna 255 (blanco) si el píxel supera el umbral, o 0 (negro) si no.

for i in range(altura):
    for j in range(ancho):
        if imagen[i, j] > umbral:
            imagen_umbralizada[i, j] = 255  # Blanco
        else:
            imagen_umbralizada[i, j] = 0    # Negro

# 5. Guardar la imagen resultante
cv2.imwrite('imagen_umbralizada2.jpg', imagen_umbralizada)
print("Imagen Generadaaa...")
