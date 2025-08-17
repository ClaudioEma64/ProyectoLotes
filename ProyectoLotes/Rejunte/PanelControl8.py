# Con deteccion de linea
# agregamos Recorte de imagen

import cv2
import tkinter as tk
from tkinter import ttk
import numpy as np
import os
from tkinter import simpledialog
import threading
import matplotlib.pyplot as plt


#////////////////////////////////

# Variables globales
ref_points = []
obj_points = []
current_mode = "reference"
pixels_per_unit = 0
ref_width_real = 0
img = None
img_copy = None
tk_root = None

img_menu= None



recalibrar = False

#///////////////////////
resize_factor = 1.0  # Factor de tamaño actual

resize_step = 0.2    # Paso para aumentar/disminuir tamaño

current_img = None   # Almacena la imagen actual para 

imagen_original= None

#///////////////////////////////



#////PARA FUNCION DIBUJAR RECTANGULO///
imagen_temporal2 = None
porcion = None

dibujando = False

#///////////deteccion de lineas///



color_a_detectar = (0, 255, 0)
deteccion_linea = 100


gray = None #cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

img_temp=None

imag_temporal=None

#//////////////////////////////////////////

img_lineas= None

#++++++++++++ medicion de lados


def medir_figuras_azules( mostrar_resultados=True, guardar_resultado=False):
    """
    Detecta figuras azules en una imagen y mide sus lados.
    
    Parámetros:
    ruta_imagen (str): Ruta de la imagen a procesar
    mostrar_resultados (bool): Muestra ventanas con resultados si es True
    guardar_resultado (bool): Guarda la imagen con medidas si es True
    
    Retorna:
    dict: Diccionario con medidas de las figuras detectadas
    """
    global img_lineas
    # Convertir a HSV
    #hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    hsv = cv2.cvtColor(img_lineas, cv2.COLOR_BGR2HSV)
    # Rango de color azul en HSV (ajustable)
    azul_bajo = np.array([90, 50, 50])
    azul_alto = np.array([130, 255, 255])
    
    # Crear máscara
    mascara = cv2.inRange(hsv, azul_bajo, azul_alto)
    
    # Mejorar máscara
    kernel = np.ones((5, 5), np.uint8)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)
    
    # Encontrar contornos
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    resultados = {}
    
    # Procesar cada figura
    for i, contorno in enumerate(contornos):
        # Saltar contornos muy pequeños
        if cv2.contourArea(contorno) < 1:
            continue
            
        # Aproximar a polígono
        perimetro = cv2.arcLength(contorno, True)
        approx = cv2.approxPolyDP(contorno, 0.02 * perimetro, True)
        num_lados = len(approx)
        
        # Calcular medidas de lados
        medidas = []
        for j in range(num_lados):
            p1 = approx[j][0]
            p2 = approx[(j + 1) % num_lados][0]
            distancia = np.linalg.norm(p1 - p2)
            medidas.append(round(distancia, 2))
            
            # Dibujar en imagen
            punto_medio = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
            #cv2.putText(imagen, f"{distancia:.1f}px", punto_medio, 
            #           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            cv2.putText(img_lineas, f"{distancia:.1f}px", punto_medio, 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

            #cv2.line(imagen, tuple(p1), tuple(p2), (255, 0, 0), 2)
            cv2.line(img_lineas, tuple(p1), tuple(p2), (255, 0, 0), 2)

        # Dibujar contorno y puntos
        #cv2.drawContours(imagen, [contorno], 0, (0, 255, 0), 2)
        cv2.drawContours(img_lineas, [contorno], 0, (0, 255, 0), 2)

        for punto in approx:
            #cv2.circle(imagen, tuple(punto[0]), 5, (0, 0, 255), -1)
            cv2.circle(img_lineas, tuple(punto[0]), 5, (0, 0, 255), -1)

        # Almacenar resultados
        resultados[f"figura_{i+1}"] = {
            "num_lados": num_lados,
            "medidas_px": medidas,
            "area_px": cv2.contourArea(contorno),
            "perimetro_px": round(perimetro, 2)
        }
    
    # Mostrar resultados
    if mostrar_resultados:
        cv2.imshow('Figuras Azules Detectadas', img_lineas)
        cv2.imshow('Mascara Azul', mascara)
        cv2.waitKey(0)
        #cv2.destroyAllWindows()
    
    # Guardar resultado
    #if guardar_resultado:
        #nombre_guardado = ruta_imagen.replace('.', '_resultado.')
        #cv2.imwrite(nombre_guardado, imagen)
        #print(f"Imagen guardada como: {nombre_guardado}")
    
    return resultados




#+++++++++++++ Dibujar linea

# Función callback para eventos del ratón
def dibujar_linea(event, x, y, flags, param):
    global dibujando, punto_inicio, imagen, imagen_original
    global img_temp
    global imag_temporal
    if event == cv2.EVENT_LBUTTONDOWN:  # Botón izquierdo presionado
        dibujando = True
        punto_inicio = (x, y)
        # Guardamos una copia de la imagen original
        #imagen_original = imagen.copy()
        imag_temporal = img_temp.copy()
        
    elif event == cv2.EVENT_MOUSEMOVE:  # Movimiento del ratón
        if dibujando:
            # Restauramos la imagen original y dibujamos línea temporal
            #imagen = imagen_original.copy()
            img_temp =imag_temporal.copy()
            #cv2.line(imagen, punto_inicio, (x, y), (0, 0, 255), 2)
            cv2.line(img_temp, punto_inicio, (x, y), (0, 255, 0), 2)

            cv2.imshow('Dibuja Lineas' , img_temp)
    elif event == cv2.EVENT_LBUTTONUP:  # Botón izquierdo liberado
        dibujando = False
        # Dibujamos la línea permanente
        #cv2.line(imagen, punto_inicio, (x, y), (0, 0, 255), 2)
        cv2.line(img_temp, punto_inicio, (x, y), (0, 255, 0), 2)






#+++++++++++++++++++++++++


def tranformadaHough(detect_linea):
    global img_temp,gray


    #imagen_redim = redimensionar_imagen(img_temp)
    #img_temp = imagen_redim.copy()
    gray = cv2.cvtColor(img_temp, cv2.COLOR_BGR2GRAY)


    # 2. Detectar bordes (Canny) el gradiente maximo de canny es 150
    edges = cv2.Canny(gray, 130, 150, apertureSize=3)


    # 3. Aplicar Transformada de Hough para líneas
    #rho=1  Resolución de distancia en píxeles (precisión para detectar líneas).#
    # Con Threshold podemos modificar la cantidad de linea
    # lo optimo es 100, si aumentamos el threhold se reducen 
    # la cantidad de linea que se detectan pero exigimos mas el 
    # al procesador. 




    lines = cv2.HoughLines(edges, 1, np.pi/180, threshold= detect_linea)

    print(f"Deteccion de linea {detect_linea}")
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
        plt.pause(2)           # Muestra por 3 segundos
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
        cv2.imshow("IMAGEN FILTRADA", resultado)
        img_lineas = resultado

    else:
        dibujando = False




#////////////////////////////////////////


def show_input_dialog(title, prompt):
    """Muestra un diálogo de entrada de Tkinter y devuelve el valor"""
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    root.attributes("-topmost", True)  # Traer al frente

    # Usar simpledialog para obtener el valor
    valor = simpledialog.askfloat(title, prompt, parent=root)

    # Destruir la ventana después de obtener el valor
    root.destroy()
    return valor

#*************EVENT************

def dibujar_rectangulo(event, x , y, flags, param):
    global ix, iy, fx, fy, dibujando, img, imagen_temporal2
    global current_img
    if event == cv2.EVENT_LBUTTONDOWN:
        dibujando = True
        ix, iy = x, y
        fx, fy = x, y
        imagen_temporal2 = current_img.copy()

    elif event == cv2.EVENT_MOUSEMOVE:
        if dibujando is True:
            fx, fy = x, y
            # Mostrar el rectangulo de Recorte color Azul en tiempo real
            img_display = imagen_temporal2.copy()
            cv2.rectangle(img_display, (ix,iy), (fx, fy), (255, 0, 0), 2)
            cv2.imshow('Seleccion de Porcion de Imagen' , img_display)


    elif event == cv2.EVENT_LBUTTONUP:
        dibujando = False
        fx, fy = x, y
        #Dibujar el rectangular final color verde, el "2" es el grosor de la li>
        cv2.rectangle(imagen_temporal2, (ix,iy), (fx, fy), (0, 255, 0), 2)
        cv2.imshow('Seleccion de Porcion de Imagen', imagen_temporal2)




def mouse_event(event, x, y, flags, param):
    global ref_points, obj_points, current_mode, img, img_copy
    
    # Modo de referencia
    if current_mode == "reference":
        if event == cv2.EVENT_LBUTTONDOWN and len(ref_points) < 4:
            ref_points.append((x, y))
            cv2.circle(img, (x, y), 5, (0, 255, 0), -1)

            if len(ref_points) > 1:
                cv2.line(img, ref_points[-2], ref_points[-1], (0, 200, 0), 2)

            if len(ref_points) == 4:
                cv2.line(img, ref_points[0], ref_points[3], (0, 200, 0), 2)

            cv2.imshow('Medicion de Objetos', img)
    
    # Modo de medición
    elif current_mode == "measure":
        if event == cv2.EVENT_LBUTTONDOWN and len(obj_points) < 4:
            obj_points.append((x, y))
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)

            if len(obj_points) > 1:
                cv2.line(img, obj_points[-2], obj_points[-1], (0, 100, 255), 2)

            if len(obj_points) == 4:
                cv2.line(img, obj_points[0], obj_points[3], (0, 100, 255), 2)
                calculate_and_display_measurements() #calcula teniendo encuenta los pixeles para sacar el tamaño de los objetos

            cv2.imshow('Medicion de Objetos', img) # se visualiza como une los puntos con lineas


#***********  FIN EVENT  ***********
def calculate_and_display_measurements():
    global ref_points, obj_points, pixels_per_unit, img, img_copy, ref_width_real
    
    global porcion

    # Calcular dimensiones en píxeles
    ref_width_px = np.linalg.norm(np.array(ref_points[0]) - np.array(ref_points[1]))
    obj_width_px = np.linalg.norm(np.array(obj_points[0]) - np.array(obj_points[1]))
    
    # Calcular relación píxeles/unidad
    pixels_per_unit = ref_width_px / ref_width_real
    
    # Calcular dimensiones reales
    obj_width_real = obj_width_px / pixels_per_unit
    obj_height_px = np.linalg.norm(np.array(obj_points[0]) - np.array(obj_points[3]))
    obj_height_real = obj_height_px / pixels_per_unit
    
    # Mostrar resultados
    #img = img_copy.copy()
    #img =porcion
    
    # Dibujar referencia
    for i in range(4):
        cv2.line(img, ref_points[i], ref_points[(i+1) % 4], (0, 255, 0), 2)
    cv2.putText(img, f"Referencia: {ref_width_real:.2f} centimetros", 
               (ref_points[0][0] - 20, ref_points[0][1] - 20),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Dibujar objeto
    for i in range(4):
        cv2.line(img, obj_points[i], obj_points[(i+1) % 4], (0, 0, 255), 2)
    
    # Mostrar medidas
    center_x = sum([p[0] for p in obj_points]) // 4
    center_y = sum([p[1] for p in obj_points]) // 4
    
    cv2.putText(img, f"Ancho: {obj_width_real:.2f} centimetros", 
               (center_x - 100, center_y - 20),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(img, f"Alto: {obj_height_real:.2f} centimetros", 
               (center_x - 100, center_y + 20),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    cv2.imshow('Medicion de Objetos', img)
    
    # Resultados en consola
    print("\n" + "="*50)
    print(f"Mediciones del objeto:")
    print(f"  Ancho: {obj_width_real:.2f} centimetros")
    print(f"  Alto: {obj_height_real:.2f} centimetros")
    print("="*50 + "\n")

    img=porcion

#/////////////////////////////////////


def redraw_points():
    """Redibuja todos los puntos sobre la imagen actual"""
    global current_img
    global img
    global ref_width_real
    if current_img is None or img is None:
        return
    
    # Crear una copia fresca de la imagen redimensionada
    temp_img = current_img.copy()
    
    # Escala para convertir coordenadas originales a coordenadas redimensionadas
    scale_x = current_img.shape[1] / img.shape[1]
    scale_y = current_img.shape[0] / img.shape[0]
    
    # Dibujar puntos de referencia
    if ref_points : #VERIFICA QUE LA LISTA de tupla NO ESTE VACIA
        scaled_ref_points = [] #NUEVA LISTA
        for point in ref_points:  
#        for point in range(4):
            scaled_x = int(point[0] * scale_x)
            scaled_y = int(point[1] * scale_y)
            scaled_ref_points.append((scaled_x, scaled_y))
            cv2.circle(temp_img, (scaled_x, scaled_y), 7, (0, 255, 0), -1)

        # Dibujar líneas entre puntos
#        for i in range(len(scaled_ref_points)):
        if len(ref_points) == 4:
             for i in range(4):

                start = scaled_ref_points[i]
                end = scaled_ref_points[(i + 1) % len(scaled_ref_points)]
            #end = scaled_ref_points[(i+1) % 4]
                cv2.line(temp_img, start, end, (0, 200, 0), 2)
            #cv2.line(temp_img, scaled_ref_points[i], scaled_ref_points[(i+1) % 4], (0, 255, 0), 2)


        # Mostrar tamaño de referencia
        if ref_width_real > 0:
            cv2.putText(temp_img, f"Referencia: {ref_width_real:.2f} cm", 
                       (int(scaled_ref_points[0][0] - 20 * scale_x), 
                        int(scaled_ref_points[0][1] - 20 * scale_y)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7 * resize_factor, (0, 255, 0), 2)





  # Dibujar puntos de objeto
    if obj_points:
        scaled_obj_points = []
        for point in obj_points:
            scaled_x = int(point[0] * scale_x)
            scaled_y = int(point[1] * scale_y)
            scaled_obj_points.append((scaled_x, scaled_y))
            cv2.circle(temp_img, (scaled_x, scaled_y), 7, (0, 0, 255), -1)

        # Dibujar líneas entre puntos
        if len(obj_points) == 4:

            #for i in range(len(scaled_obj_points)):
             for i in range(4):
                start = scaled_obj_points[i]
                end = scaled_obj_points[(i + 1) % len(scaled_obj_points)]
                cv2.line(temp_img, start, end, (0, 100, 255), 2)

        # Calcular medidas si tenemos referencia
        if ref_points and len(ref_points) >= 4 and len(obj_points) >= 4:
            # Calcular dimensiones en píxeles
            ref_width_px = np.linalg.norm(np.array(ref_points[0]) - np.array(ref_points[1]))
            obj_width_px = np.linalg.norm(np.array(obj_points[0]) - np.array(obj_points[1]))
            obj_height_px = np.linalg.norm(np.array(obj_points[0]) - np.array(obj_points[3]))

            # Calcular dimensiones reales
            if ref_width_px > 0:
                pixels_per_unit = ref_width_px / ref_width_real
                obj_width_real = obj_width_px / pixels_per_unit
                obj_height_real = obj_height_px / pixels_per_unit

                # Calcular centro
                center_x = sum([p[0] for p in obj_points]) // 4
                center_y = sum([p[1] for p in obj_points]) // 4
                scaled_center_x = int(center_x * scale_x)
                scaled_center_y = int(center_y * scale_y)

                # Mostrar medidas
                cv2.putText(temp_img, f"Ancho: {obj_width_real:.2f} cm", 
                           (scaled_center_x - int(100 * scale_x), 
                            scaled_center_y - int(20 * scale_y)),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7 * resize_factor, (0, 0, 255), 2)
                cv2.putText(temp_img, f"Alto: {obj_height_real:.2f} cm", 
                           (scaled_center_x - int(100 * scale_x), 
                            scaled_center_y + int(20 * scale_y)),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7 * resize_factor, (0, 0, 255), 2)
    
    img = temp_img
    

def update_display():
    global current_img

    """Actualiza la ventana con la imagen actual"""
    if current_img is not None:
        # Mostrar información de tamaño
        display_img = current_img.copy()
        img = current_img.copy()
        #cv2.putText(display_img, f"Zoom: {resize_factor*100:.2f}%", 
        #           (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 
        #           0.8, (0, 0, 255), 2)

        #cv2.imshow('Medicion de Objetos', display_img)
        cv2.putText(img, f"Zoom: {resize_factor*100:.2f}%", 
                   (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.8, (0, 0, 255), 2)

        cv2.imshow('Medicion de Objetos', img)




def resize_image(factor):
    """Cambia el tamaño de la imagen mostrada"""
    global current_img, resize_factor
    global img
    # Actualizar factor de tamaño con límites
    new_factor = resize_factor + factor
    if 0.3 <= new_factor <= 3.0:
        resize_factor = new_factor
    
    # Aplicar redimensionamiento
    if img is not None:
        h, w = img.shape[:2]
        new_w = int(w * resize_factor)
        new_h = int(h * resize_factor)

        # Redimensionar con interpolación de alta calidad
        current_img = cv2.resize(img, (new_w, new_h),
                                interpolation=cv2.INTER_CUBIC)

        # Redibujar puntos sobre la imagen redimensionada
        redraw_points()

        # Actualizar ventana
        update_display()
        # Redibujar puntos sobre la imagen redimensionada
        #redraw_points()


        #cv2.imshow('Medicion de Objetos', current_img)
        img = current_img


# Aumentar tamaño
def increase_size():

    resize_image(resize_step)


def decrease_size():
    """Disminuye el tamaño de la imagen"""
    resize_image(-resize_step)

def reset_size():
    """Restablece el tamaño original de la imagen"""
    global resize_factor,imagen_original
    global current_img, img
    
    resize_factor = 1.0
    current_img = imagen_original
    img = imagen_original

    #redraw_points()
    update_display()
    redraw_points()

#///////////////////////////////



class MinimalControlPanel:
    def __init__(self, command_handler):
        self.command_handler = command_handler
        self.root = tk.Tk()
        self.root.title("Menu Principal")
        self.root.geometry("250x550")
        self.root.configure(bg="#2c3e50")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        
        # Configurar estilos para ttk
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar colores para los botones
        self.style.configure('Blue.TButton', background="#3498db", foreground="white")
        self.style.configure('Green.TButton', background="#2ecc71", foreground="white")
        self.style.configure('Yellow.TButton', background="#f1c40f", foreground="white")
        self.style.configure('Red.TButton', background="#e74c3c", foreground="white")
        self.style.configure('Purple.TButton', background="#9b59b6", foreground="white")
        self.style.configure('Orange.TButton', background="#f39c12", foreground="white")
        self.style.configure('Red.TButton', background="#e74c3c", foreground="Black")

        # Crear controles
        self.create_controls()
        
        # Posición inicial
        self.root.geometry("+20+20")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_controls(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        commands = [
            ('Recalibrar', 'r', "Blue.TButton"),
            ('Tomar Medida', 'm', "Green.TButton"),
            ('Guardar', 's', "Yellow.TButton"),
            ('Salir', 'q', "Red.TButton"),
            ('Actualizar', 't', "Purple.TButton"),
            ('Zoom -', '-', "Orange.TButton"),
            ('Reset imag', 'f', "Red.TButton")


        ]
        
        for text, cmd, style_name in commands:
            btn = ttk.Button(
                main_frame,
                text=text,
                command=lambda c=cmd: self.send_command(c),
                style=style_name,
                width=15
            )
            btn.pack(fill=tk.X, pady=8, ipady=5)
            
            key_label = tk.Label(
                main_frame, 
                text=f"Tecla: '{cmd}'", 
                bg="#2c3e50",
                fg="#bdc3c7",
                font=('Arial', 8)
            )
            key_label.pack()
        
    def send_command(self, command):
        self.command_handler(command)
        print(f"Comando enviado: {command}")
        
    def on_close(self):
        """Maneja el cierre de la ventana"""
        self.command_handler('q')
        self.root.destroy()
        
    def update_gui(self):
        """Actualiza la GUI sin bloquear"""
        self.root.update()

# Solución para el error de Wayland
os.environ['GDK_BACKEND'] = 'x11'
os.environ['QT_QPA_PLATFORM'] = 'xcb'

# Ejemplo de uso con OpenCV
if __name__ == "__main__":
    # Usamos un diccionario para mantener el estado mutable
    state = {"running": True}
    estadoR= {"recalibrar": False }
    estadoM = {"medir": False }
    estadoA = {"Actualizar":False}
    estadoZneg= {"Zoom-":False}
    estadoReset= {"Reset":False}



#    global ref_points, obj_points, current_mode, img, img_cpy, ref_width_real
    #recalibrar = False

    def handle_command(cmd):
        if cmd == 'r':
            print("Recalibrando sistema..")
            #recalibrar = True
            estadoR["recalibrar"] = True
        elif cmd == 'm':
            print("Tomando medida...")
            estadoM["medir"] = True
        elif cmd == 's':
            print("Guardando datos...")
        elif cmd == 'q':
            print("Saliendo...")
            state["running"] = False
        elif cmd == 't':
            print("Actualizando...")
            estadoA["Actualizar"] = True
        elif cmd == '-':
            print("Zoom -...")
            estadoZneg["Zoom-"] = True
        elif cmd == 'f':
            print("Reseteando Imag...")
            estadoReset["Reset"] = True

    
    # Crear ventana OpenCV
#    window_name = "Sistema de Visión"
#    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
#    cv2.resizeWindow(window_name, 800, 600)
#//////////////////////////    
#    global ref_points, obj_points, current_mode, img, img_cpy, ref_width_real

    #Cargar Imagen
    img=cv2.imread('lote.jpeg')
    #imagen_original=img.copy()
    if img is None:
        # Crear imagen de demo
        img = np.zeros((500, 800, 3), dtype=np.uint8)
        cv2.putText(img, "DEMO: Objeto de referencia (verde)", (100, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.putText(img, "DEMO: Objeto a medir (rojo)", (100, 300), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.rectangle(img, (150, 120), (300, 220), (0, 255, 0), 2)
        cv2.rectangle(img, (150, 320), (400, 420), (0, 0, 255), 2)
        cv2.putText(img, "Presiona 'r' para establecer referencia", (50, 450), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(img, "Presiona 'm' para comenzar medicion", (50, 480), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    #variable para Recorte de imagen
    porcion= img.copy()
    imagen_temporal2 = img.copy()
    current_img = img.copy()


    #****************

    img_copy = img.copy()

    imagen_original = img
 
    #************ deteccion de linea*********

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
 

   #************ Imagen Menu ***************
    img_menu = np.zeros((200, 800, 3), dtype=np.uint8)
    cv2.putText(img_menu, "Bienvenido!! ", (300, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(img_menu, "Presione 'r' para continuar: ", (150, 140), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    #*************************************

    # Configurar ventana OpenCV
    cv2.namedWindow('Medicion de Objetos')
    #cv2.setMouseCallback('Medicion de Objetos', mouse_event)
    cv2.imshow('Medicion de Objetos', img_menu)
    
    """ABRE VENTANA "Seleccion de Porcion"""

    cv2.namedWindow("Seleccion de Porcion de Imagen")
    cv2.imshow('Seleccion de Porcion de Imagen', imagen_temporal2)
    cv2.setMouseCallback('Seleccion de Porcion de Imagen', dibujar_rectangulo)

    
    print("Instrucciones:")

    print("- Presiona 'g' para guardar RECORTE de la imagen")
    print("1. Presiona 'r' para MODO referencia")
    print("2. Haz clic en las 4 esquinas del objeto de referencia")
    print("3. Ingresa el tamaño real del objeto de referencia")
    print("4. Presiona 'm' para modo medición")
    print("5. Haz clic en las 4 esquinas del objeto a medir")
    print("6. Presiona 'n' para nuevo objeto")
    print("7. Presiona 'ESC' para salir")
    print("8. Presiona '+' ZOOM aumenta")
    print("9. Presiona '-' ZOOM dismininuye")
    print("Pasos para que ande:")

    print("10. Presiona 'p' aummenta cantidad de lineas")
    
    print("11. Presiona 'z' Agregamos linea")
    print("12. Presiona 't' ACTUALIZAR imagenes")
    print(" Seleccionamo area que queremos determinar su contorno")

    print("Dentro de la ventana AREA")
    print("13. Presiona 'c' para calcular los lados")


#//////////////////////////////////////////////
    # Iniciar panel de control (en el mismo hilo principal)
    panel = MinimalControlPanel(handle_command)
    
    # Bucle principal combinado
    try:
        while state["running"]:
            # Actualizar GUI de Tkinter
            panel.update_gui()
            
            # Manejar teclas
            key = cv2.waitKey(1)
            
            if ((key == ord('r')) or (estadoR["recalibrar"])) :  # Modo referencia
                cv2.destroyWindow("Medicion de Objetos")

                current_mode = "reference"
                ref_points = []
                #img = img_copy.copy()


                #cv2.imshow('Medicion de Objetos', img)
                #print("\nModo referencia: Selecciona las 4 esquinas del objeto de referencia")

                # Solicitar tamaño real con Tkinter
                ref_width_real = show_input_dialog(
                "Tamaño de Referencia",
                "Ingresa el ancho real del objeto de referencia (en centimetros):"
                )



                # Si el usuario cancela, usar valor por defecto
                if ref_width_real is None:
                    print("Entrada cancelada. Usando valor por defecto 1.0")
                    ref_width_real = 1.0
                else:
                    print(f"Tamaño de referencia establecido: {ref_width_real} centimetros")
                
                cv2.namedWindow('Medicion de Objetos')
                cv2.setMouseCallback('Medicion de Objetos', mouse_event)
                cv2.imshow('Medicion de Objetos', img)
                print("\nModo referencia: Selecciona las 4 esquinas del objeto de referencia")


                estadoR["recalibrar"] = False
            elif ((key == ord('m')) or (estadoM["medir"])):  # Modo medición
               
                if len(ref_points) < 4:
                    print("Error: Primero debes seleccionar un objeto de referencia completo")
                else:
                    current_mode = "measure"
                    obj_points = []
                    #img = img_copy.copy()
                    #img= porcion
                   
                    # Dibujar referencia existente
                    for i in range(4):
                        cv2.line(img, ref_points[i], ref_points[(i+1) % 4], (0, 255, 0), 2)
                   
                    cv2.imshow('Medicion de Objetos', img)

                    print("\nModo medición: Selecciona las 4 esquinas del objeto a medir")

                estadoM["medir"]= False

#////////////////////////////////////////////////////

            elif key == ord('c'):  # Calcular medidas
                #calculate_and_display_measurements()
                
                 # Procesar imagen
                resultados = medir_figuras_azules(mostrar_resultados=True,
    guardar_resultado=False)
    
                # Mostrar resultados en consola
                print("\nResultados de medición:")
                for figura, datos in resultados.items():
                    print(f"\n{figura.upper()}:")
                    print(f" - Lados: {datos['num_lados']}")
                    print(f" - Área: {datos['area_px']} px²")
                    print(f" - Perímetro: {datos['perimetro_px']} px")
                    for i, lado in enumerate(datos['medidas_px'], 1):
                        print(f" - Lado {i}: {lado} px")



            elif key == ord('n'):  # Nuevo objeto
                if current_mode == "measure":
                    obj_points = []
                    redraw_points()
                    update_display()
                    print("\nPreparado para medir un nuevo objeto")

            elif key == ord('+'):  # Aumentar tamaño
               
                #cv2.destroyWindow("Medicion de Objetos")
                #cv2.namedWindow('Medicion de Objetos')
                #cv2.setMouseCallback('Medicion de Objetos', mouse_event)
                #cv2.imshow('Medicion de Objetos', img)


                increase_size()
                print(f"Tamaño aumentado a {resize_factor*100:.0f}%")

                estadoZpos["Zoom+"] = False

            elif key == ord('-'):  # Disminuir tamaño
                decrease_size()
                print(f"Tamaño reducido a {resize_factor*100:.0f}%")

                estadoZneg["Zoom-"] = False




#///////////////////////////////////////////////////////////////7///
#///////////////////ERROR (No resetea la imagen)/////////////
          
            elif key == ord('f'):  # Tamaño original
                

                #cv2.destroyWindow('Medicion de Objetos')
                #cv2.imshow('Seleccion de Porcion de Imagen', img)

                deteccion_linea = 100

                resize_factor = 1.0
                current_img = imagen_original
                img = imagen_original

                cv2.imshow('Medicion de Objetos', img)

                cv2.namedWindow("Seleccion de Porcion de Imagen")
                cv2.imshow('Seleccion de Porcion de Imagen', img)
                cv2.setMouseCallback('Seleccion de Porcion de Imagen', dibujar_rectangulo)

                
                #cv2.namedWindow('Medicion de Objetos')
                #cv2.setMouseCallback('Medicion de Objetos', mouse_event)
                #cv2.imshow('Medicion de Objetos', img)


                print("Tamaño restablecido al 100%")

                porcion = img[y1:y2, x1: x2].copy()




                estadoReset["Reset"] = False

#/////////////////////////////////////////////////////


            #********* Recorte de imagen****************
            elif key == ord('g'):
                if ix != -1 and iy != -1 and fx != -1 and fy != -1:
                    #Asegurarse de que las coordenadas esten en el orden correcto
                    #la funcion sorted() ordena un alista. 
                    x1, x2 = sorted([ix, fx])
                    y1, y2 = sorted([iy, fy])

                    porcion = img[y1:y2, x1: x2].copy()

                    cv2.imwrite('porcion_guardada.jpg', porcion)
                    print("Porcion guardada como 'porcion_guardada.jpg'")
                    #ABRE VENTANA MEDIDOR LOTES
                    #cv2.namedWindow("Medidor de Lotes")
                    #cv2.setMouseCallback("Medidor de Lotes", mouse_event)

                    #dibujar_puntos_y_lineas()  # Mostrar imagen inicial
                    #cv2.waitKey(500)  # Espera 3 segundos (3000 ms)

                    cv2.destroyWindow("Seleccion de Porcion de Imagen")

                    img =porcion
                    current_img= porcion
                    img_temp = porcion
             #*********************Fin Recorte************
            # Transformacion
            elif  key == ord('p'):

                deteccion_linea= deteccion_linea - 5
                tranformadaHough(deteccion_linea)
                cv2.destroyWindow("Area")

                cv2.namedWindow("Area")
                cv2.setMouseCallback('Area', dibujar_Area_Lote)
                cv2.imshow("Area", img_temp)

            elif  key == ord('k'):

                deteccion_linea = deteccion_linea + 10
                tranformadaHough(deteccion_linea)

                cv2.destroyWindow("Area")

                cv2.namedWindow("Area")

                cv2.setMouseCallback('Area', dibujar_Area_Lote)

                cv2.imshow("Area", img_temp)

            elif  key == ord('z'):
            
                cv2.namedWindow('Dibuja Lineas')
                #cv2.imshow('Dibuja Lineas', img_temp)

                cv2.setMouseCallback('Dibuja Lineas', dibujar_linea)
                cv2.imshow('Dibuja Lineas', img_temp)
            #************************************************* 

            elif ( (key == ord('t'))  or (estadoA["Actualizar"])): #uso para Actualizar pantallas

                cv2.destroyWindow('Dibuja Lineas')
                cv2.namedWindow('Dibuja Lineas')
                #cv2.imshow('Dibuja Lineas', img_temp)

                cv2.setMouseCallback('Dibuja Lineas', dibujar_linea)
                cv2.imshow('Dibuja Lineas', img_temp)


                cv2.destroyWindow("Area")

                cv2.namedWindow("Area")

                cv2.setMouseCallback('Area', dibujar_Area_Lote)

                cv2.imshow("Area", img_temp)

                estadoA["Actualizar"] = False


            #*************************************************
            if key == 27 or key == ord('q'):  # ESC o 'q'
                state["running"] = False
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cerrar todo en el orden correcto
        cv2.destroyAllWindows()
        panel.root.destroy()  # Destruir ventana Tkinter

