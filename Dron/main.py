from flask import Flask, Response, jsonify
import cv2
import numpy as np
from djitellopy import Tello
from collections import Counter

from line_follower import line_follower
from shape_detection import shape_detection
from shape_detection import find_shape

app = Flask(__name__)
me = Tello()
me.connect()
me.streamon()

def generate_frames():

    """ 
        Genera un flujo de frames capturados desde la cámara para visualizarlos como video.
        Los bits están codificados en formato JPG para que sea foto por foto.
    """

    while True:
        frame = me.get_frame_read().frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():

    """ 
        Endpoint para conectar la actualización de frames en tiempo real con el js.
    """

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/emergency_stop')
def emergency_stop():

    """ 
        Método para parado de emergencia del dron.
    """
    
    me.emergency()
    return "Emergency stop executed"

contador_triangulo = 0
contador_cuadrado = 0
contador_pentagono = 0
contador_rombo = 0
contador_circulo = 0

@app.route('/start')
def start():
    global contador_triangulo, contador_cuadrado, contador_pentagono, contador_rombo, contador_circulo
    
    """ 
    Inicialización del dron junto con el detector de figuras y seguidor de linea.
    Dependiendo de la figura detectada, el dron realizará un movimiento específico.
    """
    # me.takeoff()
    shapes = []
    detected_shapes = 0
    while True:
        if detected_shapes or find_shape(generate_frames):
            shape = shape_detection(generate_frames)
            shapes.append(shape)
            detected_shapes += 1

            if detected_shapes == 30:
                count = Counter(shapes)
                most_common_shape = max(count, key=count.get)
                """
                Movimientos basados en la forma más comun detectada dentro de un rango de cuadros.
                """
                if most_common_shape == "triangle":
                    me.rotate_clockwise(180)
                    me.move_forward(20)
                    contador_triangulo += 1
                elif most_common_shape == "square":
                    me.land()
                    contador_cuadrado += 1
                    break
                elif most_common_shape == "pentagon":
                    me.rotate_clockwise(90)
                    me.move_forward(20)
                    contador_pentagono += 1
                elif most_common_shape == "rhombus":
                    me.rotate_clockwise(-90)
                    me.move_forward(20)
                    contador_rombo += 1
                elif most_common_shape == "circle":
                    me.move_forward(20)
                    contador_circulo += 1
                
                shapes = []
                detected_shapes = 0

                print(most_common_shape)
        else:
            """
            Si no encuentra figuras, el dron seguirá avanzando sobre la línea detectada.
            """
            forward, left_right, yaw = line_follower(generate_frames)
            # me.send_rc_control(left_right, forward, 0, yaw)

        if cv2.waitKey(1) == 27:
            # me.send_rc_control(0,0,0,0)
            # me.land()
            print("exit")
            break

    counters = {
        "triangulo": contador_triangulo,
        "cuadrado": contador_cuadrado,
        "pentagono": contador_pentagono,
        "rombo": contador_rombo,
        "circulo": contador_circulo
    }
    return jsonify(counters)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
