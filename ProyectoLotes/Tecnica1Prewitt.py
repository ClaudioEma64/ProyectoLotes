import numpy as np
import cv2
import matplotlib.pyplot as plt

def prewitt_edge_detection(image_path, threshold=30):
    # 1. Leer la imagen en escala de grises
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    if image is None:
        print("Error: No se pudo cargar la imagen.")
        return
    
    # 2. Aplicar el operador Prewitt
    kernel_x = np.array([[-1, 0, 1],
                         [-1, 0, 1],
                         [-1, 0, 1]])
    
    kernel_y = np.array([[-1, -1, -1],
                         [ 0,  0,  0],
                         [ 1,  1,  1]])
    
    # Aplicar convolución para detectar bordes horizontales y verticales
    edges_x = cv2.filter2D(image, cv2.CV_64F, kernel_x)
    edges_y = cv2.filter2D(image, cv2.CV_64F, kernel_y)
    
    # Combinar los bordes (magnitud del gradiente)
    edges = np.sqrt(edges_x**2 + edges_y**2)
    edges = np.uint8(edges)
    
    # Aplicar umbral para resaltar bordes fuertes
    _, edges_thresh = cv2.threshold(edges, threshold, 255, cv2.THRESH_BINARY)
    
    # 3. Mostrar resultados
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.imshow(image, cmap='gray')
    plt.title('Imagen Original')
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    plt.imshow(edges_thresh, cmap='gray')
    plt.title('Bordes Detectados (Prewitt)')
    plt.axis('off')
    
    plt.show()

# Ejemplo de uso
image_path = 'images.jpeg'  # Cambia por tu ruta de imagen
prewitt_edge_detection(image_path, threshold=50)
