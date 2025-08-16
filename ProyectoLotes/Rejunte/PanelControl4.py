import cv2
import tkinter as tk
from tkinter import ttk
import numpy as np
import os
from tkinter import simpledialog
import threading


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
                calculate_and_display_measurements()
            
            cv2.imshow('Medicion de Objetos', img)



def calculate_and_display_measurements():
    global ref_points, obj_points, pixels_per_unit, img, img_copy, ref_width_real
    
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
    img = img_copy.copy()
    
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
        cv2.putText(display_img, f"Zoom: {resize_factor*100:.2f}%", 
                   (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.8, (0, 0, 255), 2)

        cv2.imshow('Medicion de Objetos', display_img)




def resize_image(factor):
    """Cambia el tamaño de la imagen mostrada"""
    global current_img, resize_factor
    
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
       # redraw_points()

        # Actualizar ventana
        update_display()
        # Redibujar puntos sobre la imagen redimensionada
        redraw_points()


        #cv2.imshow('Medicion de Objetos', current_img)
        #img = current_img


# Aumentar tamaño
def increase_size():

    resize_image(resize_step)


def decrease_size():
    """Disminuye el tamaño de la imagen"""
    resize_image(-resize_step)

def reset_size():
    """Restablece el tamaño original de la imagen"""
    global resize_factor,imagen_original
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
            ('Zoom +', '+', "Purple.TButton"),
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
    estadoZpos = {"Zoom+":False}
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
        elif cmd == '+':
            print("Zoom +...")
            estadoZpos["Zoom+"] = True
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
    imagen_original=img.copy()
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
    
    img_copy = img.copy()
    img_menu = np.zeros((500, 800, 3), dtype=np.uint8)
    cv2.putText(img_menu, "Bienvenido!! ", (150, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(img_menu, "Presione 'r' para continuar: ", (150, 140), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    # Configurar ventana OpenCV
    # Configurar ventana OpenCV
    cv2.namedWindow('Medicion de Objetos')
    #cv2.setMouseCallback('Medicion de Objetos', mouse_event)
    cv2.imshow('Medicion de Objetos', img_menu)
    
    print("Instrucciones:")
    print("1. Presiona 'r' para modo referencia")
    print("2. Haz clic en las 4 esquinas del objeto de referencia")
    print("3. Ingresa el tamaño real del objeto de referencia")
    print("4. Presiona 'm' para modo medición")
    print("5. Haz clic en las 4 esquinas del objeto a medir")
    print("6. Presiona 'n' para nuevo objeto")
    print("7. Presiona 'ESC' para salir")



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
                img = img_copy.copy()


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

                    # Dibujar referencia existente
                    for i in range(4):
                        cv2.line(img, ref_points[i], ref_points[(i+1) % 4], (0, 255, 0), 2)
                    cv2.imshow('Medicion de Objetos', img)
                    print("\nModo medición: Selecciona las 4 esquinas del objeto a medir")


                estadoM["medir"]= False

#////////////////////////////////////////////////////

            elif key == ord('c'):  # Calcular medidas
                calculate_and_display_measurements()

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



            elif key == ord('f'):  # Tamaño original
                reset_size()
                print("Tamaño restablecido al 100%")


                estadoReset["Reset"] = False

#/////////////////////////////////////////////////////
            if key == 27 or key == ord('q'):  # ESC o 'q'
                state["running"] = False
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cerrar todo en el orden correcto
        cv2.destroyAllWindows()
        panel.root.destroy()  # Destruir ventana Tkinter
