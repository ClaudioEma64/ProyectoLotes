import cv2
import numpy as np
import matplotlib.pyplot as plt

import time

#

#azul = (255, 0 ,0); verde = (0, 255, 0); rojo = (0, 0, 255)
dibujando = False #True si el boton esta presionado   
#modo= True #si true, rectangulo, sino linea, cambia con m
ix, iy = -1, -1

fx, fy = -1, -1

# Definir el color que quieres detectar (en formato BGR, no RGB)
color_a_detectar = (0, 255, 0)



# 1. Cargar imagen y convertir a escala de grises


#img = cv2.imread('Loteprueba.jpeg')

#img = cv2.imread('images.jpeg')

img=cv2.imread('porcion_guardada.jpg')


gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

img_temp= img.copy()

img_lineas=img.copy()



if img is None:
    print("Error: No se pudo cargar la imagen. Verifica la ruta.")
    exit()



# 2. Detectar bordes (Canny) el gradiente maximo de canny es 150
edges = cv2.Canny(gray, 100, 150, apertureSize=3)

# 3. Aplicar Transformada de Hough para líneas
#rho=1  Resolución de distancia en píxeles (precisión para detectar líneas).#
# Con Threshold podemos modificar la cantidad de linea
# lo optimo es 100, si aumentamos el threhold se reducen 
# la cantidad de linea que se detectan pero exigimos mas el 
# al procesador. 
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
        cv2.line(img_temp, (x1, y1), (x2, y2), (0, 255, 0), 1)
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
    plt.imshow(img_temp, cmap='gray')
    plt.title(f'lineas detectadas')
    plt.axis('off')

    plt.tight_layout()

    plt.show(block=False)  # Permite que el código continúe
    plt.pause(4)           # Muestra por 3 segundos
    plt.close('all')      # Cierra todas las figuras automáticamente
#Funcion llamada Por CallbackMause()
def dibujar_Area_Lote(event, x , y, flags, param):
    global ix, iy, fx, fy, dibujando, img, img_temp,img_lineas

    color_deseado = np.array([0, 255, 0])  # Verde en BGR

    # Tolerancia para cada canal (B, G, R)
    tolerancia = 30

    # Crear máscara de píxeles que coinciden con el color

    mascara = np.all(np.abs(img_temp - color_deseado) < tolerancia, axis=2)

    # Crear imagen resultante (fondo blanco)
    resultado = np.full_like(img_temp, 255)  # Blanco puro

    # Copiar solo los píxeles que coinciden con el color deseado
    resultado[mascara] = img_temp[mascara]
#    cv2.imshow('Resultado', resultado)


    if event == cv2.EVENT_LBUTTONDOWN:
        dibujando = True
        ix, iy = x, y
        fx, fy = x, y

        # Color del píxel donde se hizo clic (BGR)
        color_semilla = resultado[y, x].tolist()

        # Color de relleno (rojo en este ejemplo)
#        color_relleno = (0, 0, 255)
        
        # Definir el color de relleno (con transparencia, formato BGRA)
        color_relleno = (255, 0, 0, 0)  # Verde semitransparente (alpha=128/255)


        # Máscara para floodFill (debe ser 2 píxeles más grande que la imagen)
        # h=high w=weight
        h, w = resultado.shape[:2]
        mascara1 = np.zeros((h+2, w+2), np.uint8)

        # Rellenar el área conectada con tolerancia de color
        cv2.floodFill(
            image=resultado,
            mask=mascara1,
            seedPoint=(x, y),
            newVal=color_relleno,
            loDiff=(10, 10, 10),  # Tolerancia inferior (B, G, R)
            upDiff=(10, 10, 10)     # Tolerancia superior
        )
#       cv2.imshow("IMAGEN FILTRADA", resultado)
        img_lineas = resultado





#creo ventana con nombre image
cv2.namedWindow('Lotes')

cv2.setMouseCallback('Lotes', dibujar_Area_Lote)

print("Instrucciones:")
print("1. Seleccione un area que desea dibujar con el mouse")
print("2. Modificar el threshold para deteccion de lineas 'p'")
print("3. -")
print("4. Presione 'q' para salir")




while(1):
#    cv2.imshow("image", img_temp)
    cv2.imshow("Lotes",img_lineas )


    k = cv2.waitKey(1) & 0xFF
    if k == ord('g'):  #guardar el area del lote
         if ix != -1 and iy != -1 and fx != -1 and fy != -1:
                #Asegurarse de que las coordenadas esten en el orden correcto
                #la funcion sorted() ordena un alista. 
                x1, x2 = sorted([ix, fx])
                y1, y2 = sorted([iy, fy])

    elif  k == ord('r'): #Restuarar imagen original
        img_temp = img.copy()
        ix, iy = -1, -1
        fx, fy = -1, -1 
        print("Imagen restaurada - puede hacer una nueva seleccion")
    elif  k == ord('p'): #Aumento la deteccion de lineas

        deteccion_lineas=10
    elif  k == ord('q'): #salir
        break

cv2.destroyAllWindows()
