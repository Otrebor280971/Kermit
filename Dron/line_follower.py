import numpy as np
import cv2

def map_x(x, a=-50, b=50):

    """
        Mapea un valor de coordenada X desde el rango original de la imagen (de -240 a 240)
        a un nuevo rango especificado por los parámetros 'a' y 'b'.

        Args:
            x (int): Coordenada X a mapear.
            a (int, optional): Límite inferior del nuevo rango. Por defecto es -50.
            b (int, optional): Límite superior del nuevo rango. Por defecto es 50.
    """
    return int(a + (x + 240) * (b - a) / 480)

def map_angle(angle, a=-40, b=40):

    """
        Mapea un ángulo desde el rango original (de -90 a 90 grados)
        a un nuevo rango especificado por los parámetros 'a' y 'b'.

        Args:
            angle (float): Ángulo a mapear.
            a (int, optional): Límite inferior del nuevo rango. Por defecto es -40.
            b (int, optional): Límite superior del nuevo rango. Por defecto es 40.
    """
    return int(a + (angle + 90) * (b - a) / 180)

def calculate_angle(cx, cy):

    """
        Calcula el ángulo entre la línea que conecta el centro de la imagen con el punto (cx, cy)
        y la vertical.

        Args:
            cx (int): Coordenada X del punto.
            cy (int): Coordenada Y del punto.
    """
    angle = np.arctan2(cx, cy)
    return np.degrees(angle)

def line_follower(frame):

    """
        Procesa un frame para seguir una línea basada en el color detectado.

        Convierte el frame a espacio de color HSV y crea una máscara para el color de la línea.
        Encuentra los contornos de la máscara y calcula los comandos para mover el dron.
    """

    """
        Rango de colores para linea HSV
    """
    lower = np.array([0,0,203])
    upper = np.array([180,45,255])

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    """
        Genera una máscara para la detección de linea.
    """
    mask = cv2.inRange(hsv, lower, upper)

    """
        Encontrar contornos en la máscara.
    """
    contours, _ =cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    forward = 0
    left_rigth = 0
    yaw = 0

    if contours:

        """
            Identificar el contorno más grande.
        """
        biggest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(biggest)
        cx = (x + w)//2
        cy = (y + h)//2

        """
            Calcular la diferencia en el eje X respecto al centro de la imagen.
        """
        x_difference = cx - 240

        """
            Identificar la región de interés para contabilizar pixeles.
        """
        central_roi = mask[:, 160:320]
        pixel_count = cv2.countNonZero(central_roi)

        """
            Comandos de control en base de la detección.
        """
        if pixel_count > 10000: 
            forward = 30

        left_rigth = map_x(x_difference)
        angle = calculate_angle(x_difference, cy)
        yaw = map_angle(angle)

        cv2.drawContours(frame, contours, -1, (255,0,0), 5)
        cv2.circle(frame, (cx, cy), 10, (255,0,0), cv2.FILLED)

    cv2.imshow("Mask", mask)
    return forward, left_rigth, yaw