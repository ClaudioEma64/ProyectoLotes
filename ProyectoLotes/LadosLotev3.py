import cv2
import numpy as np
import math

# Variables globales
puntos = []  # Almacena los vértices del lote
imagen = cv2.imread("images.jpeg")  # Imagen original
imagen_temporal = imagen.copy()  # Copia para dibujar
imagen_temporal2 = imagen.copy()  # Copia para recortar
porcion=imagen.copy()

escala = 0.1  # Escala en metros/píxel (ej: 0.1 si 10px = 1m)

factor_zoom = 1  # Factor de ampliación de la imagen (1.5 = 150%)

dibujando = False


def calcular_distancia(p1, p2):
    """Calcula la distancia entre dos puntos en píxeles y metros."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    distancia_px = math.sqrt(dx**2 + dy**2)
    distancia_m = distancia_px * escala if escala else None
    return distancia_px, distancia_m



def redimensionar_imagen(imagen_original):
    """Redimensiona la imagen según el factor de zoom"""
    c = 0
    if imagen_original is None:
        return None
    ancho = int(imagen_original.shape[1] * factor_zoom)
    alto = int(imagen_original.shape[0] * factor_zoom)
    return  cv2.resize(imagen_original, (ancho, alto))
   # print("valor que envia redimencionar {c}: ", c)
    
def dibujar_puntos_y_lineas():
    """Dibuja puntos y líneas conectadas en la imagen."""
    global imagen_temporal, imagen_temporal2,porcion
#    imagen_temporal = imagen.copy()
    if imagen is None:
        return
    
    # Creamos una copia redimensionada
    imagen_redim = redimensionar_imagen(porcion)
    imagen_temporal = imagen_redim.copy()
    imagen_temporal2= imagen_temporal.copy()
    # Ajustamos las coordenadas de los puntos según el zoom
    
    puntos_redim = []
    for punto in puntos:
        try:
             # Si es una tupla/lista/numpy array con 2 elementos
            x, y = map(float, punto[:2])  # Asegura que son números
            puntos_redim.append((int(x*factor_zoom), int(y*factor_zoom)))
        except (TypeError, ValueError, IndexError):
            continue  # Ignora puntos mal formados
    # Opcional: Verificación
    if not puntos_redim:
        print("Advertencia: No se pudo procesar ningún punto")


 # Dibuja todas las líneas
    if len(puntos_redim) > 1:
        # Primero encuentra el lado más al norte
        lados = []
        for i in range(len(puntos_redim)):
            p1 = puntos_redim[i]
            p2 = puntos_redim[(i+1)%len(puntos_redim)]
            azimut = calcular_azimut(p1, p2)


   # Calculamos qué tan "norte" está este lado (0° es exactamente norte)
            norte_score = min(abs(azimut), abs(360-azimut))
            lados.append((norte_score, i, p1, p2))
        
        # Ordena los lados por su cercanía al norte
        lados.sort()
        
         # Dibuja todos los lados primero
        for _, i, p1, p2 in lados:
            cv2.line(imagen_temporal, p1, p2, (0, 255, 0), 2)


 # Resalta el lado más al norte (el primero en la lista ordenada)
        if lados:
            _, i, p1_norte, p2_norte = lados[0]
            cv2.line(imagen_temporal, p1_norte, p2_norte, (255, 0, 0), 4)  # Rojo más grueso
            # Añade texto "NORTE"
            centro_x = (p1_norte[0] + p2_norte[0]) // 2
            centro_y = (p1_norte[1] + p2_norte[1]) // 2
            cv2.putText(imagen_temporal, "NORTE", (centro_x, centro_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7*factor_zoom, (0, 0, 255), 2)



    # Dibuja líneas entre puntos
    if len(puntos_redim) > 1:
        for i in range(len(puntos_redim) - 1):
            cv2.line(imagen_temporal, puntos_redim[i], puntos_redim[i+1], (0, 255, 0), 2)
        # Cierra el polígono
        # cv2.line(imagen_temporal, puntos_redim[-1], puntos_redim[0], (0, 255, 0), 2)
        if len(puntos_redim) > 2:
            cv2.line(imagen_temporal, puntos_redim[-1], puntos_redim[0], (0, 255, 0), 2)
    # Dibuja puntos
    for punto in puntos_redim:
        cv2.circle(imagen_temporal, punto, int(5*factor_zoom), (0, 0, 255), -1)
    
    # Mide distancias
    for i in range(len(puntos_redim)):
        p1 = puntos_redim[i]
        p2 = puntos_redim[(i + 1) % len(puntos_redim)] if len(puntos_redim) > 1 else p1
        distancia_px, distancia_m = calcular_distancia(puntos[i], puntos[(i + 1) % len(puntos)] if len(puntos) > 1 else puntos[i])
#            distancia_px, distancia_m = calcular_distancia(p1, p2)
        texto = f"{distancia_px:.1f}px"
        if distancia_m:
            texto += f" ({distancia_m:.2f}m)"
        pos_texto = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
        #cv2.putText(imagen_temporal, texto, pos_texto, cv2.FONT_HERSHEY_SIMPLEX, 0.5*factor, (0, 0, 0), int(1*factor))
    
        cv2.putText(imagen_temporal, texto, pos_texto, cv2.FONT_HERSHEY_SIMPLEX, 0.5*factor_zoom, (255, 255, 255), int(2*factor_zoom))
        cv2.putText(imagen_temporal, texto, pos_texto, cv2.FONT_HERSHEY_SIMPLEX, 0.5*factor_zoom, (0, 0, 0), int(1*factor_zoom))


    cv2.imshow("Medidor de Lotes", imagen_temporal)

def click_event(event, x, y, flags, param):
    """Maneja los eventos del mouse."""
    global puntos
   # Ajustamos las coordenadas según el zoom
    x_original = int(x / factor_zoom)
    y_original = int(y / factor_zoom) 

    if event == cv2.EVENT_LBUTTONDOWN:
        puntos.append((x_original, y_original))
        dibujar_puntos_y_lineas()
    
    elif event == cv2.EVENT_RBUTTONDOWN:
        if len(puntos) > 0:
            puntos.pop()  # Elimina el último punto
            dibujar_puntos_y_lineas()





def calcular_azimut(p1, p2):
    """Calcula el ángulo respecto al norte geográfico (en grados) de una línea p1-p2"""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]  # En imágenes, el eje Y crece hacia abajo
    angulo_rad = math.atan2(dx, -dy)  # -dy porque el norte es hacia arriba en la imagen
    angulo_deg = math.degrees(angulo_rad)
    return angulo_deg % 360  # Aseguramos un valor entre 0-360





def detectar_contornos( mostrar_pasos=False):
    # Cargar la imagen
#    imagen = cv2.imread(imagen_path)
    #imagen = cv2.imread("images.jpeg")

    #if imagen is None:
      #  print("Error: No se pudo cargar la imagen")
     #   return
    

    # Convertir a escala de grises
    gris = cv2.cvtColor(imagen_temporal, cv2.COLOR_BGR2GRAY)
    
    # Aplicar desenfoque para reducir ruido
    desenfocada = cv2.GaussianBlur(gris, (5, 5), 0)
    
    # Detectar bordes con Canny
    bordes = cv2.Canny(desenfocada, 50, 150)
    
    # Encontrar contornos
    contornos, jerarquia = cv2.findContours(bordes.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Dibujar los contornos encontrados
    imagen_contornos = imagen_temporal.copy()
    cv2.drawContours(imagen_contornos, contornos, -1,(0, 255, 0), 2)

    
    # Mostrar resultado
    if mostrar_pasos:
        cv2.imshow('Imagen Original', imagen_temporal)
        cv2.imshow('Escala de Grises', gris)
        cv2.imshow('Bordes Detectados', bordes)
    
    cv2.imshow('Contornos Detectados', imagen_contornos)
    cv2.waitKey(0)
    #cv2.destroyAllWindows()
    
    # Guardar la imagen con contornos
    cv2.imwrite('imagen_con_contornos.jpg', imagen_contornos)
    print("Imagen con contornos guardada como 'imagen_con_contornos.jpg'")


def dibujar_rectangulo(event, x , y, flags, param):
    global ix, iy, fx, fy, dibujando, imagen, imagen_temporal2

    if event == cv2.EVENT_LBUTTONDOWN:
        dibujando = True
        ix, iy = x, y
        fx, fy = x, y
        imagen_temporal2 = imagen_temporal.copy()

    elif event == cv2.EVENT_MOUSEMOVE:
        if dibujando is True:
            fx, fy = x, y
        # Mostrar el rectangulo en tiempo real
            img_display = imagen_temporal2.copy()
            cv2.rectangle(img_display, (ix,iy), (fx, fy), (255, 0, 0), 2)
            cv2.imshow('Seleccion de Porcion de Imagen' , img_display)

    elif event == cv2.EVENT_LBUTTONUP:
        dibujando = False
        fx, fy = x, y
        #Dibujar el rectangular final el "2" es el grosor de la linea
        cv2.rectangle(imagen_temporal2, (ix,iy), (fx, fy), (0, 255, 0), 2)
        cv2.imshow('Seleccion de Porcion de Imagen', imagen_temporal2)

#////////////////////////// MAIN ///////////////////////////////

def main():
    global imagen, escala, factor_zoom, porcion
    
    # Cargar imagen (reemplaza con tu ruta)
    imagen = cv2.imread("images.jpeg")
    if imagen is None:
        print("Error: No se pudo cargar la imagen.")
        return
    
    # Configurar escala (ej: 0.05 significa 20px = 1m)
    #escala = float(input("Ingresa la escala (metros/píxel): ")) if input("¿Usar escala? (s/n): ").lower() == 's' else None
   # Configurar escala
    usar_escala = input("¿Usar escala? (s/n): ").lower() == 's'
    if usar_escala:
        try:
            escala = float(input("Ingresa la escala (metros/píxel): "))
        except ValueError:
            print("Valor inválido. Usando escala 1:1 (solo píxeles)")
            escala = None
    else:
        escala = None
   # Configurar zoom
    try:
        factor_zoom = float(input(f"Ingresa el factor de zoom (Imagen Recortada) (actual={factor_zoom}): ") or factor_zoom)
    except ValueError:
        print(f"Valor inválido. Usando zoom por defecto {factor_zoom}")

#    cv2.namedWindow("Medidor de Lotes")
#    cv2.setMouseCallback("Medidor de Lotes", click_event)

    cv2.namedWindow("Seleccion de Porcion de Imagen")
    cv2.setMouseCallback('Seleccion de Porcion de Imagen', dibujar_rectangulo)


    #cv2.namedWindow("Medidor de Lotes")
    #cv2.setMouseCallback("Medidor de Lotes", click_event)

    #dibujar_puntos_y_lineas()  # Mostrar imagen inicial
    
    print("Instrucciones:")
    print("- Clic izquierdo: Agregar punto")
    print("- Clic derecho: Eliminar último punto")
    print("- Presiona 'q' para salir")
    print("- Presiona 'c' para limpiar todos los puntos")
    print("- Presiona 'a' para aumentar zoom")
    print("- Presiona 'd' para disminuir zoom")
    print("- Presiona 'e' para guardar imagen con contornos")
    print("- Presiona 'g' para guardar imagen seleccionada")
    print("-**************¿¿ COMENZAMOS ?? **************")
#    print("-**************PRECIONA 's' para iniciar**************")
    
 

    while True:
        key = cv2.waitKey(1) & 0xFF
       
        if key == ord('q'):
            break
        elif key == ord('c'):
            puntos.clear()
            dibujar_puntos_y_lineas()
        elif key == ord('a'):
            factor_zoom *= 1.1
            dibujar_puntos_y_lineas()
        elif key == ord('d'):
            factor_zoom /= 1.1
            dibujar_puntos_y_lineas()
        elif key == ord('e'):
            detectar_contornos( mostrar_pasos=True)
            dibujar_puntos_y_lineas()
        elif key == ord('g'):
             
            if ix != -1 and iy != -1 and fx != -1 and fy != -1:
        #Asegurarse de que las coordenadas esten en el orden correcto
        #la funcion sorted() ordena un alista.            
                x1, x2 = sorted([ix, fx])
                y1, y2 = sorted([iy, fy])

                porcion = imagen[y1:y2, x1: x2].copy()
#                porcion = imagen_temporal[y1:y2, x1: x2]
 
                cv2.imwrite('porcion_guardada.jpg', porcion)
                print("Porcion guardada como 'porcion_guardada.jpg'")

                cv2.namedWindow("Medidor de Lotes")
    
                cv2.setMouseCallback("Medidor de Lotes", click_event)

                dibujar_puntos_y_lineas()  # Mostrar imagen inicial
                cv2.waitKey(500)  # Espera 3 segundos (3000 ms)
                
                cv2.destroyWindow("Seleccion de Porcion de Imagen")

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
