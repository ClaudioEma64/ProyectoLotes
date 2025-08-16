import cv2
import numpy as np

def detectar_contornos(imagen_path, mostrar_pasos=False):
    # Cargar la imagen
    imagen = cv2.imread(imagen_path)
    if imagen is None:
        print("Error: No se pudo cargar la imagen")
        return
    
    # Convertir a escala de grises
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    
    # Aplicar desenfoque para reducir ruido
    desenfocada = cv2.GaussianBlur(gris, (5, 5), 0)
    
    # Detectar bordes con Canny
    bordes = cv2.Canny(desenfocada, 50, 150)
    
    # Encontrar contornos
    contornos, jerarquia = cv2.findContours(bordes.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Dibujar los contornos encontrados
    imagen_contornos = imagen.copy()
    cv2.drawContours(imagen_contornos, contornos, -1, (0, 255, 0), 2)
    
    # Mostrar resultados
    if mostrar_pasos:
        cv2.imshow('Imagen Original', imagen)
        cv2.imshow('Escala de Grises', gris)
        cv2.imshow('Bordes Detectados', bordes)
    
    cv2.imshow('Contornos Detectados', imagen_contornos)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # Guardar la imagen con contornos
    cv2.imwrite('imagen_con_contornos.jpg', imagen_contornos)
    print("Imagen con contornos guardada como 'imagen_con_contornos.jpg'")

# Uso del programa
ruta_imagen = input("Introduce la ruta de la imagen: ")
detectar_contornos(ruta_imagen, mostrar_pasos=True)
