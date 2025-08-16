import cv2
import numpy as np
import matplotlib.pyplot as plt



# 1. Cargar imagen y convertir a escala de grises
img = cv2.imread('images.jpeg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 2. Detectar bordes (Canny)
edges = cv2.Canny(gray, 50, 150, apertureSize=3)

# 3. Aplicar Transformada de Hough para líneas
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
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

# 5. Mostrar resultados
    plt.imshow(img, cmap='gray')
    plt.title("Después de Apertura (Texto Eliminado)")
    plt.show()

