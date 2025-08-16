import cv2
import numpy as np
import matplotlib.pyplot as plt

def filtrar_contornos_1cm(image_path, escala_px_cm=38, ancho_linea_1cm=5, mostrar_intermedios=False):
    """
    Parámetros:
    - image_path: Ruta de la imagen.
    - escala_px_cm: Píxeles que representan 1 cm en la imagen (ajustar según resolución).
    - ancho_linea_1cm: Grosor en píxeles de una línea de 1 cm.
    - mostrar_intermedios: Mostrar imágenes intermedias para diagnóstico.
    """


    # 1. Cargar imagen y convertir a escala de grises
    img = cv2.imread(image_path)
    if img is None:
        print("Error: No se pudo cargar la imagen.")
        return
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Binarización adaptativa (para manejar variaciones de iluminación)
    kernel = np.ones((13, 13), np.uint8)

    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY_INV, 3, 2)
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel,iterations=3)
    if mostrar_intermedios:
        plt.imshow(binary, cmap='gray')
        plt.title("Binarización Adaptativa")
        plt.show()
    
    # 3. Apertura morfológica para eliminar texto y ruido
    kernel_size = max(3, int(ancho_linea_1cm * 0.6))  # Tamaño del kernel basado en el ancho de línea
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
    """
    if mostrar_intermedios:
        plt.imshow(cleaned, cmap='gray')
        plt.title("Después de Apertura (Texto Eliminado)")
        plt.show()
    """
    # 4. Detección de contornos y filtrado por longitud (1 cm)
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_length_cm = 1  # Longitud mínima en cm
    min_length_px = escala_px_cm * min_length_cm  # Convertir a píxeles
    
    mask = np.zeros_like(gray)
    for cnt in contours:
        length = cv2.arcLength(cnt, closed=False)
        if length >= min_length_px:
            cv2.drawContours(mask, [cnt], -1, 255, thickness=ancho_linea_1cm)

    # 5. Cierre morfológico para unir segmentos rotos
    kernel_refine = np.ones((ancho_linea_1cm // 2, ancho_linea_1cm // 2), np.uint8)
    final_contours = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_refine)
    """ 
    if mostrar_intermedios:
        plt.imshow(final_contours, cmap='gray')
        plt.title("Contornos Filtrados y Refinados")
        plt.show()
    """
    # 6. Superponer contornos en la imagen original (opcional)
    result = cv2.bitwise_and(img, img, mask=final_contours)
    
    # 7. Visualización
    plt.figure(figsize=(18, 6))
    
    plt.subplot(1, 3, 1)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title('Imagen Original')
    plt.axis('off')
    
    plt.subplot(1, 3, 2)
    plt.imshow(final_contours, cmap='gray')
    plt.title(f'Contornos de {min_length_cm} cm (Máscara)')
    plt.axis('off')
    
    plt.subplot(1, 3, 3)
    plt.imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    plt.title('Resultado Final')
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()

# Ejemplo de uso:
filtrar_contornos_1cm(
    image_path="images.jpeg",
    escala_px_cm=19,      # Ajustar según la resolución de tu imagen 1cm 38pix
    ancho_linea_1cm=1,    # Grosor de línea típico 5 en píxeles
    mostrar_intermedios=True  # Para diagnóstico
)
