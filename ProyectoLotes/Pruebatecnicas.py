import cv2
import numpy as np
import matplotlib.pyplot as plt

def procesar_contornos(image_path, kernel_size=3, umbral_canny=100):
    # 1. Leer imagen y convertir a escala de grises
    imagen = cv2.imread(image_path)
    if imagen is None:
        print("Error: No se pudo cargar la imagen.")
        return
    
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    




    # 2. Eliminar texto (usando apertura morfológica)
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    apertura = cv2.morphologyEx(gris, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # 3. Detectar bordes (Canny + Prewitt/Sobel opcional)
    bordes_canny = cv2.Canny(apertura, umbral_canny, umbral_canny * 2)
    
    # Opcional: Combinar con Prewitt para bordes más gruesos
    sobelx = cv2.Sobel(apertura, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(apertura, cv2.CV_64F, 0, 1, ksize=3)
    bordes_sobel = np.sqrt(sobelx**2 + sobely**2)
    bordes_sobel = np.uint8(bordes_sobel > 50) * 255  # Umbralizar
    
    bordes_combinados = cv2.bitwise_or(bordes_canny, bordes_sobel)
    
    # 4. Refinar contornos (dilatación leve)
    bordes_refinados = cv2.dilate(bordes_combinados, kernel, iterations=3)
    
    # 5. Superponer contornos en imagen original (opcional)
    contornos_color = cv2.cvtColor(bordes_refinados, cv2.COLOR_GRAY2BGR)
    contornos_color[:, :, 0:2] = 0  # Eliminar canales R y G (solo azul)
    resultado = cv2.addWeighted(imagen, 0.7, contornos_color, 0.1, 0)
    
    # 6. Mostrar resultados
    plt.figure(figsize=(18, 6))
    plt.subplot(1, 3, 1)
    plt.imshow(cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB))
    plt.title('Imagen Original')
    plt.axis('off')
    
    plt.subplot(1, 3, 2)
    plt.imshow(bordes_refinados, cmap='gray')
    plt.title('Contornos Detectados')
    plt.axis('off')
    
    plt.subplot(1, 3, 3)
    plt.imshow(cv2.cvtColor(resultado, cv2.COLOR_BGR2RGB))
    plt.title('Contornos Superpuestos (Azul)')
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()

# Uso
procesar_contornos("images.jpeg", kernel_size=1, umbral_canny=50)
