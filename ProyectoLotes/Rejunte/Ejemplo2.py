import cv2
import numpy as np
import tkinter as tk
from tkinter import simpledialog

# Variables globales
ref_points = []
obj_points = []
current_mode = "reference"
pixels_per_unit = 0
ref_width_real = 1
img_original = None  # Almacena la imagen original sin modificaciones
current_img = None   # Almacena la imagen actual para mostrar
resize_factor = 1.0  # Factor de tamaño actual
resize_step = 0.2    # Paso para aumentar/disminuir tamaño

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

def resize_image(factor):
    """Cambia el tamaño de la imagen mostrada"""
    global current_img, resize_factor
    
    # Actualizar factor de tamaño con límites
    new_factor = resize_factor + factor
    if 0.3 <= new_factor <= 3.0:
        resize_factor = new_factor
    
    # Aplicar redimensionamiento
    if img_original is not None:
        h, w = img_original.shape[:2]
        new_w = int(w * resize_factor)
        new_h = int(h * resize_factor)
        
        # Redimensionar con interpolación de alta calidad
        current_img = cv2.resize(img_original, (new_w, new_h), 
                                interpolation=cv2.INTER_CUBIC)
        
        # Redibujar puntos sobre la imagen redimensionada
        redraw_points()
        
        # Actualizar ventana
        update_display()

def increase_size():
    """Aumenta el tamaño de la imagen"""
    resize_image(resize_step)

def decrease_size():
    """Disminuye el tamaño de la imagen"""
    resize_image(-resize_step)

def reset_size():
    """Restablece el tamaño original de la imagen"""
    global resize_factor
    resize_factor = 1.0
    current_img = img_original.copy()
    redraw_points()
    update_display()

def update_display():
    """Actualiza la ventana con la imagen actual"""
    if current_img is not None:
        # Mostrar información de tamaño
        display_img = current_img.copy()
        cv2.putText(display_img, f"Tamaño: {resize_factor*100:.0f}%", 
                   (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.8, (0, 0, 255), 2)
        
        cv2.imshow('Medicion de Objetos', display_img)

def redraw_points():
    """Redibuja todos los puntos sobre la imagen actual"""
    global current_img
    global img_original
    global ref_width_real
    if current_img is None or img_original is None:
        return
    
    # Crear una copia fresca de la imagen redimensionada
    temp_img = current_img.copy()
    
    # Escala para convertir coordenadas originales a coordenadas redimensionadas
    scale_x = current_img.shape[1] / img_original.shape[1]
    scale_y = current_img.shape[0] / img_original.shape[0]
    
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
    
    current_img = temp_img

def mouse_event(event, x, y, flags, param):
    global ref_points, obj_points, current_mode
    global img_original
    # Escala para convertir coordenadas redimensionadas a coordenadas originales
    if img_original is not None and current_img is not None:
        scale_x = img_original.shape[1] / current_img.shape[1]
        scale_y = img_original.shape[0] / current_img.shape[0]
        orig_x = int(x * scale_x)
        orig_y = int(y * scale_y)
    else:
        orig_x, orig_y = x, y
    
    # Modo de referencia
    if current_mode == "reference":
        if event == cv2.EVENT_LBUTTONDOWN and len(ref_points) < 4:
            ref_points.append((orig_x, orig_y))
            redraw_points()
            update_display()
    
    # Modo de medición
    elif current_mode == "measure":
        if event == cv2.EVENT_LBUTTONDOWN and len(obj_points) < 4:
            obj_points.append((orig_x, orig_y))
            redraw_points()
            update_display()

def calculate_and_display_measurements():
    """Calcula y muestra las mediciones en consola"""
    global ref_points, obj_points, pixels_per_unit, ref_width_real
    
    if len(ref_points) < 4 or len(obj_points) < 4:
        print("Error: Selecciona ambos objetos completamente")
        return
    
    # Calcular dimensiones en píxeles
    ref_width_px = np.linalg.norm(np.array(ref_points[0]) - np.array(ref_points[1]))
    obj_width_px = np.linalg.norm(np.array(obj_points[0]) - np.array(obj_points[1]))
    obj_height_px = np.linalg.norm(np.array(obj_points[0]) - np.array(obj_points[3]))
    
    # Calcular relación píxeles/unidad
    pixels_per_unit = ref_width_px / ref_width_real
    
    # Calcular dimensiones reales
    obj_width_real = obj_width_px / pixels_per_unit
    obj_height_real = obj_height_px / pixels_per_unit
    
    # Resultados en consola
    print("\n" + "="*50)
    print(f"Mediciones del objeto:")
    print(f"  Ancho: {obj_width_real:.2f} unidades")
    print(f"  Alto: {obj_height_real:.2f} unidades")
    print(f"  Relacion de escala: 1 unidad = {1/pixels_per_unit:.2f} pixeles")
    print("="*50 + "\n")

def main():
    global ref_points, obj_points, current_mode, img_original, current_img, resize_factor
    global ref_width_real
    # Cargar imagen
    img = cv2.imread('lote.jpeg')
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
        cv2.putText(img, "Teclas: '+' Agrandar, '-' Achicar, '0' Tamaño Original", (50, 510), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Guardar copias de la imagen
    img_original = img.copy()
    current_img = img.copy()
    
    # Configurar ventana OpenCV
    cv2.namedWindow('Medicion de Objetos')
    cv2.setMouseCallback('Medicion de Objetos', mouse_event)
    cv2.imshow('Medicion de Objetos', current_img)
    
    print("Instrucciones:")
    print("1. Presiona 'r' para modo referencia")
    print("2. Haz clic en las 4 esquinas del objeto de referencia")
    print("3. Ingresa el tamaño real del objeto de referencia")
    print("4. Presiona 'm' para modo medición")
    print("5. Haz clic en las 4 esquinas del objeto a medir")
    print("6. Teclas de tamaño: '+' Agrandar, '-' Achicar, '0' Tamaño Original")
    print("7. Presiona 'c' para calcular mediciones")
    print("8. Presiona 'n' para nuevo objeto")
    print("9. Presiona 'ESC' para salir")
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('r'):  # Modo referencia
            cv2.destroyWindow("Medicion de Objetos")
            current_mode = "reference"
            ref_points = []
            reset_size()
            print("\nModo referencia: Selecciona las 4 esquinas del objeto de referencia")
            
            # Solicitar tamaño real con Tkinter
            ref_value = show_input_dialog(
                "Tamaño de Referencia",
                "Ingresa el ancho real del objeto de referencia (en CM):"
            )
            # Solicitar Largo real con Tkinter
            ref_LARGO = show_input_dialog(
                "Tamaño de Referencia",
                "Ingresa el LARGO REAL del objeto de referencia (en CM):"
            )
            current_img = img_original
            cv2.setMouseCallback('Medicion de Objetos', mouse_event)
            cv2.imshow('Medicion de Objetos',current_img)

            
            if ref_value is not None:
                ref_width_real = ref_value
                print(f"Tamaño de referencia establecido: {ref_width_real} unidades")
            else:
                print("Entrada cancelada. Usando valor anterior")
        
        elif key == ord('m'):  # Modo medición
            if len(ref_points) < 4:
                print("Error: Primero debes seleccionar un objeto de referencia completo")
            else:
                current_mode = "measure"
                obj_points = []
                redraw_points()
                update_display()
                print("\nModo medición: Selecciona las 4 esquinas del objeto a medir")
        
        elif key == ord('c'):  # Calcular medidas
            calculate_and_display_measurements()
        
        elif key == ord('n'):  # Nuevo objeto
            if current_mode == "measure":
                obj_points = []
                redraw_points()
                update_display()
                print("\nPreparado para medir un nuevo objeto")
        
        elif key == ord('+'):  # Aumentar tamaño
            increase_size()
            print(f"Tamaño aumentado a {resize_factor*100:.0f}%")
        
        elif key == ord('-'):  # Disminuir tamaño
            decrease_size()
            print(f"Tamaño reducido a {resize_factor*100:.0f}%")
        
        elif key == ord('0'):  # Tamaño original
            reset_size()
            print("Tamaño restablecido al 100%")
        
        elif key == 27:  # Tecla ESC
            break
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
