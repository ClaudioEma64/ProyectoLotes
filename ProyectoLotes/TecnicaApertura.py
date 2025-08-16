import cv2
import numpy as np
import matplotlib.pyplot as plt

def aplicar_apertura(image_path, kernel_size=3, mostrar_original=True):
    # 1. Leer la imagen en escala de grises
    imagen = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    if imagen is None:
        print("Error: No se pudo cargar la imagen.")
        return
    
    # 2. Definir el kernel (estructurante) para la operación morfológica
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    
    # 3. Aplicar apertura (erosión seguida de dilatación)
    imagen_erosionada = cv2.erode(imagen, kernel, iterations=1)
    imagen_apertura = cv2.dilate(imagen_erosionada, kernel, iterations=1)
    
    # 4. Mostrar resultados
    plt.figure(figsize=(12, 6))
    
    if mostrar_original:
        plt.subplot(1, 2, 1)
        plt.imshow(imagen, cmap='gray')
        plt.title('Imagen Original')
        plt.axis('off')
    
        plt.subplot(1, 2, 2)
        plt.imshow(imagen_apertura, cmap='gray')
        plt.title(f'Apertura (Kernel {kernel_size}x{kernel_size})')
        plt.axis('off')
    else:
        plt.imshow(imagen_apertura, cmap='gray')
        plt.title(f'Apertura (Kernel {kernel_size}x{kernel_size})')
        plt.axis('off')
    
    plt.show()

# Ejemplo de uso
image_path = 'images.jpeg'  # Cambia por tu ruta de imagen
aplicar_apertura(image_path, kernel_size=5, mostrar_original=True)
