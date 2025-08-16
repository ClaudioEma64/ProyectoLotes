import cv2
import numpy as np

# Variables globales
contornos = []
imagen_original = None
imagen_trabajo = None
contorno_seleccionado = None

def seleccionar_contorno(event, x, y, flags, param):
    global contorno_seleccionado, imagen_trabajo
    
    if event == cv2.EVENT_LBUTTONDOWN:
        for cnt in contornos:
            # Verifica si el clic está cerca del contorno (5px de margen)
            distancia = cv2.pointPolygonTest(cnt, (x, y), True)
            if abs(distancia) < 5:  # Si está cerca del borde
                contorno_seleccionado = cnt
                # Dibujar el contorno seleccionado
                imagen_trabajo = imagen_original.copy()
                cv2.drawContours(imagen_trabajo, [cnt], -1, (0, 0, 255), 3)
                area = cv2.contourArea(cnt)
                cv2.putText(imagen_trabajo, f"Area: {area:.2f} px^2", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                print(f"Area seleccionada: {area:.2f} px^2")
                break

def main():
    global contornos, imagen_original, imagen_trabajo
    
    # 1. Cargar imagen y detectar contornos (como en tu código original)
    ruta = input("Introduce la ruta de la imagen: ")
    imagen_original = cv2.imread(ruta)
    if imagen_original is None:
        print("Error al cargar la imagen")
        return
    
    gris = cv2.cvtColor(imagen_original, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gris, (5, 5), 0)
    bordes = cv2.Canny(blur, 50, 150)
    contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 2. Mostrar contornos detectados (en verde)
    imagen_trabajo = imagen_original.copy()
    cv2.drawContours(imagen_trabajo, contornos, -1, (0, 255, 0), 2)
    
    # 3. Configurar ventana interactiva
    cv2.namedWindow("Selecciona el Contorno")
    cv2.setMouseCallback("Selecciona el Contorno", seleccionar_contorno)
    
    print("\nInstrucciones:")
    print("- Haz clic cerca del borde del contorno que deseas seleccionar")
    print("- Presiona 'q' para salir")
    
    while True:
        cv2.imshow("Selecciona el Contorno", imagen_trabajo)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

