import cv2
import numpy as np

# Variables globales
dibujando = False
ix, iy = -1, -1
img = None
img_temp = None

def dibujar_Area_Lote(event, x, y, flags, param):
    global ix, iy, dibujando, img, img_temp
    
    if event == cv2.EVENT_LBUTTONDOWN:
        ix, iy = x, y
        dibujando = True
        
        # Color del píxel donde se hizo clic (BGR)
        color_semilla = img_temp[y, x].tolist()
        
        # Color de relleno (verde en este ejemplo)
        color_relleno = (0, 255, 0)
        
        # Máscara para floodFill (debe ser 2 píxeles más grande que la imagen)
        # h=high w=weight
        h, w = img_temp.shape[:2]
        mascara = np.zeros((h+2, w+2), np.uint8)
        
        # Rellenar el área conectada con tolerancia de color
        cv2.floodFill(
            image=img_temp,
            mask=mascara,
            seedPoint=(x, y),
            newVal=color_relleno,
            loDiff=(10, 10, 10),  # Tolerancia inferior (B, G, R)
            upDiff=(10, 10, 10)     # Tolerancia superior
        )
        
        cv2.imshow("Imagen", img_temp)

# Cargar imagen
img = cv2.imread("images.jpeg")
img_temp = img.copy()

cv2.namedWindow("Imagen")
cv2.setMouseCallback("Imagen", dibujar_Area_Lote)

print("Instrucciones:")
print("Precionar 'q' para salir")


while True:
    cv2.imshow("Imagen", img_temp)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # Tecla ESC para salir
        break

cv2.destroyAllWindows()
