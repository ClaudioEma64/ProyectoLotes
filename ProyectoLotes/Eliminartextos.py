import cv2
import numpy as np
import pytesseract
from pytesseract import Output

def eliminar_texto(imagen_path, output_path):
    # Cargar la imagen
    imagen = cv2.imread(imagen_path)
    if imagen is None:
        print("Error al cargar la imagen")
        return
    
    # Convertir a escala de grises
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    desenfocada = cv2.GaussianBlur(gris, (5, 5), 0)
    
    # Aplicar umbral adaptativo para detectar texto (ajusta los parámetros según tu imagen)
    #thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
     #                            cv2.THRESH_BINARY_INV, 11, 2)
#    deteccion de bordes ()canny
    bordes = cv2.Canny(desenfocada,50, 150)
#   dilatar los bodes para cerrar contornos
    kernel= np.ones((3, 3), np.uint8)
    bordes_dilatados = cv2.dilate(bordes, kernel, iterations = 1)


    # Encontrar contornos (zonas de texto)
    contornos, _ = cv2.findContours(bordes_dilatados, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Crear una máscara para las zonas de texto
    mascara = np.zeros_like(gris)
    cv2.drawContours(mascara, contornos, -1, 255, thickness=cv2.FILLED)
    
    # Aplicar inpainting para rellenar las zonas de texto
    resultado = cv2.bitwise_and(imagen, imagen, mask=mascara)
    
    # Guardar el resultado
    cv2.imwrite(output_path, resultado)
    print(f"Imagen procesada guardada en: {output_path}")
    cv2.imshow("planos sin texto", resultado)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
# Uso:
eliminar_texto("images.jpeg", "plano_sin_texto.jpg")
