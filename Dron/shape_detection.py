import cv2
import numpy as np

"""
    Rangos de color para la segmentación de las figuras.
"""
lower_red = np.array([170,150,100])
upper_red = np.array([180,255,255])

lower_yellow = np.array([17, 100, 100])
upper_yellow = np.array([30, 255, 255])

lower_blue = np.array([90,100,100])
upper_blue = np.array([120,255,255])

lower_green = np.array([45,100,85])
upper_green = np.array([89,255,255])

def apply_mask(frame):
    
    """
        Aplica segmentación de color a un frame de entrada para detectar colores específicos.
    """

    """
        Selección de la región de interés dentro del frame.
    """
    roi = frame[120:240, 160:320]

    """
        Conversión del roi a HSV.
    """
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    """
        Definición de las máscaras para la detección de colores específicos.
    """
    mask_red = cv2.inRange(hsv, lower_red, upper_red)
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask = cv2.bitwise_or(mask_red, cv2.bitwise_or(mask_yellow, cv2.bitwise_or(mask_green, mask_blue)))
    return mask

def find_shape(frame):
    
    """
        Detecta si hay una forma presente en un frame de entrada basado en la cantidad de píxeles detectados.
    """
    mask = apply_mask(frame)
    pixel_count = cv2.countNonZero(mask)
    if pixel_count > 8000:
        return True
    return False

def shape_detection(frame):
    
    """
        Detecta y clasifica la forma presente en un frame de entrada.
    """
    roi = frame[120:240, 160:320]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask_red = cv2.inRange(hsv, lower_red, upper_red)
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask = cv2.bitwise_or(mask_red, cv2.bitwise_or(mask_yellow, cv2.bitwise_or(mask_green, mask_blue)))

    """
        Identificación de los contornos de la máscara.
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    """
        Variables para almacenar los vértices y la forma detectada.
    """
    vertex_x = np.empty(4, dtype=np.int16)
    vertex_y = np.empty(4, dtype=np.int16)
    shape = "None"
    aux = 0

    for cntr in contours:
        area = cv2.contourArea(cntr)
        if area > 6000:
            
            """
                Aproximación de un polígono al contorno de la fitura.
            """
            approx = cv2.approxPolyDP(cntr, 0.03*cv2.arcLength(cntr, True), True)

            x = approx.ravel()[0]
            y = approx.ravel()[1]
            
            """
                Clasificación de la figura respecto al número de vértices aproximados.
            """
            if len(approx) == 3:
                shape = "triangle"
            elif len(approx) == 4:
                for i in range(4):
                    vertex_x[i] = approx[i][0][0]
                    vertex_y[i] = approx[i][0][1]

                """
                    Ordena las coordenadas de los vértices.
                """
                for i in range(4):
                    for j in range(3):
                        if vertex_x[j] > vertex_x[j+1]:
                            aux = vertex_x[j+1]
                            vertex_x[j+1] = vertex_x[j]
                            vertex_x[j] = aux

                            aux = vertex_y[j+1]
                            vertex_y[j+1] = vertex_y[j]
                            vertex_y[j] = aux
                
                """
                    Ordena las coordenadas superiores e inferiores para verificar si es cuadrado o rombo.
                """
                if vertex_y[0] > vertex_y[1]:
                    aux = vertex_y[1]
                    vertex_y[1] = vertex_y[0]
                    vertex_y[0] = aux

                if vertex_y[2] > vertex_y[3]:
                    aux = vertex_y[3]
                    vertex_y[3] = vertex_y[2]
                    vertex_y[2] = aux
                    
                upper_difference = abs(vertex_y[0] - vertex_y[2])
                lower_difference = abs(vertex_y[1] - vertex_y[3])

                if upper_difference < 50 and lower_difference < 50: 
                    shape = "square"
                else: 
                    shape = "rhombus"

            elif len(approx) == 5:
                shape = "pentagon"
            elif len(approx) > 8 and len(approx) < 12:
                shape = "circle"

            cv2.drawContours(roi, [approx], 0, (0,0,0), 2)            

    return shape