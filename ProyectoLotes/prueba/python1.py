import cv2
import numpy as np
import pytesseract
from pytesseract import Output

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'



def eliminar_texto(imagen_path, output_path="plano_sin_texto.jpg"):
    # 1. Cargar imagen
    img = cv2.imread(imagen_path)
    if img is None:
        print("Error: No se pudo cargar la imagen.")
        return

    # 2. Detección de texto con pytesseract
    datos_texto = pytesseract.image_to_data(img, output_type=Output.DICT)
    
    # 3. Crear una máscara para eliminar texto
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    
    for i in range(len(datos_texto["text"])):
        # Si la confianza es alta (> 60), consideramos que es texto
        if int(datos_texto["conf"][i]) > 60:
            x, y, w, h = datos_texto["left"][i], datos_texto["top"][i], datos_texto["width"][i], datos_texto["height"][i]
            cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)  # Rellenar área de texto
    
    # 4. Aplicar inpaint para eliminar el texto
    resultado = cv2.inpaint(img, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

    # 5. Guardar y mostrar resultado
    cv2.imwrite(output_path, resultado)
    cv2.imshow("Plano sin Texto", resultado)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print(f"Resultado guardado como '{output_path}'")

# Instalar pytesseract y Tesseract-OCR antes de ejecutar:
# pip install pytesseract opencv-python
# Descargar Tesseract-OCR: https://github.com/UB-Mannheim/tesseract/wiki
ruta_imagen = input("Ingresa el nombre de la imagen (ej: 'images.jpeg'): ")
eliminar_texto(ruta_imagen)
