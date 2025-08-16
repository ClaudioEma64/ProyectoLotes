import cv2
import numpy as np
import matplotlib.pyplot as plt



# 1. Cargar imagen y convertir a escala de grises
img = cv2.imread('images.jpeg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


# 2. Detectar bordes (Canny) el gradiente maximo de canny es 150
edges = cv2.Canny(gray, 130, 150, apertureSize=3)

# 3. Aplicar Transformada de Hough para líneas
#rho=1  Resolución de distancia en píxeles (precisión para detectar líneas).#
lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)

# 4. Dibujar las líneas detectadas
if lines is not None:
    for rho, theta in lines[:, 0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 255), 1)

# 5. Mostrar resultados
   
    plt.figure(figsize=(18, 6))
    
    plt.subplot(1,3, 1)
    plt.imshow(cv2.cvtColor(gray, cv2.COLOR_BGR2RGB))
    plt.title('Imagen Original')
    plt.axis('off')
    
    plt.subplot(1, 3, 2)
    plt.imshow(edges, cmap='gray')
    plt.title(f'Canny')
    plt.axis('off')
   

    plt.subplot(1, 3, 3)
    plt.imshow(img, cmap='gray')
    plt.title(f'lineas detectadas')
    plt.axis('off')
   
    plt.tight_layout()
    plt.show()
