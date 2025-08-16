import cv2
import numpy as np
import matplotlib.pyplot as plt

def ajustar_escala_grises(imagen, alpha=1.0, beta=0):
    """Ajusta contraste (alpha) y brillo (beta) en escala de grises."""
    return cv2.convertScaleAbs(imagen, alpha=alpha, beta=beta)

def aplicar_morfologia(image_path, kernel_size=3, alpha=1.0, beta=0):
    # 1. Leer imagen y convertir a escala de grises
    imagen = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if imagen is None:
        print("Error: No se pudo cargar la imagen.")
        return

   
    altura,ancho = imagen.shape
    # 2. Ajustar escala de grises
    imagen_ajustada = ajustar_escala_grises(imagen, alpha=alpha, beta=beta)
    
   
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    
    imagen_opened= cv2.morphologyEx(imagen_ajustada,cv2.MORPH_OPEN,kernel)
    

    plt.imshow(imagen_opened, cmap='gray')
    plt.title("eliminacion de ruido1")
    plt.show()
#hough

   
#Crea una matriz negra del mismo tamaño que la imagen original. dtype=np.uint8: Tipo de dato sin signo de 8 bits (0 a 255).
#np es de la numpy no opencv
    imagen_umbralizada = np.zeros((altura, ancho), dtype=np.uint8)
    umbral=240
# 4. Aplicar umbral manualmente usando bucles for anidados
#    Recorre cada píxel de la imagen original.
#    Asigna 255 (blanco) si el píxel supera el umbral, o 0 (negro) si no.

    for i in range(altura):
        for j in range(ancho):
            if imagen_ajustada[i, j] > umbral:
                imagen_umbralizada[i, j] = 255  # Blanco
            else:
                imagen_umbralizada[i, j] = 0    # Negro

    plt.imshow(imagen_umbralizada, cmap='gray')
    plt.title("Umbralizada")
    plt.show()

#en prueba aca para abajo


    kernel2 = np.ones((3, 3), np.uint8)


    imagen_opened2= cv2.morphologyEx(imagen_umbralizada,cv2.MORPH_OPEN,kernel2)
    

    plt.imshow(imagen_opened2, cmap='gray')
    plt.title("eliminacion de ruido2")
    plt.show()


    #3. Definir kernel (estructurante)
    #    Define un kernel (matriz) de tamaño 5x5 píxeles lleno de 1s.
    #  Este kernel determinará el área de influencia para las operaciones morfológicas.
   
    
    # 4. Aplicar dilatación (antes de la apertura)
    imagen_dilatada = cv2.erode(imagen_ajustada, kernel, iterations=1)
    
    # 5. Aplicar apertura (erosión + dilatación)
    imagen_erosionada = cv2.erode(imagen_ajustada, kernel, iterations=1)
    imagen_apertura = cv2.dilate(imagen_erosionada, kernel, iterations=1)
    
    # 6. Mostrar resultados
    plt.figure(figsize=(18, 6))
    
    plt.subplot(1, 6, 1)
    plt.imshow(imagen, cmap='gray')
    plt.title('Original')
    plt.axis('off')
    
    plt.subplot(1, 6, 2)
    plt.imshow(imagen_ajustada, cmap='gray')
    plt.title(f'Ajuste Grises\n(alpha={alpha}, beta={beta})')
    plt.axis('off')
    
 
    plt.subplot(1, 6, 3)
    plt.imshow(imagen_umbralizada, cmap='gray')
    plt.title(f'Imagen eliminacion de ruido\n')
    plt.axis('off')
    
    plt.subplot(1, 6, 4)
    plt.imshow(imagen_opened, cmap='gray')
    plt.title(f'Imagen Umbralizada\n')
    plt.axis('off')


    plt.subplot(1, 6, 5)
    plt.imshow(imagen_dilatada, cmap='gray')
    plt.title(f'Dilatación\n(Kernel {kernel_size}x{kernel_size})')
    plt.axis('off')
    
    plt.subplot(1, 6, 6)
    plt.imshow(imagen_apertura, cmap='gray')
    plt.title(f'Apertura\n(Kernel {kernel_size}x{kernel_size})')
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()

# Ejemplo de uso
image_path = 'images.jpeg'
aplicar_morfologia(image_path, kernel_size=3, alpha=1.0, beta=40)

