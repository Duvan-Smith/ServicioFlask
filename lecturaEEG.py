import time
import pika, sys, os

#leer mensaje
def Medir_Satisfaccion(sample):
    #Extraer de la lectura un array con la forma(shape) requerido por el modelo entrenado
    #el valor debe ser el porcentaje
    return 0.84
def Guardar_datos(variables_usabilidad,medida_de_satisfaccion):
    #una librería en firebase
    #http://ozgur.github.io/python-firebase/
    pass
    #cuardar en firebase los datos obtenidos
def Leer_mensaje():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='muestra')
    method_frame, header_frame, body = channel.basic_get(queue='muestra')
    if method_frame: #recibó mensaje
        channel.basic_ack(method_frame.delivery_tag) #marca mensaje como leido
        return body #retorna el mensaje
    return None


#simulación de print_raw
def print_raw(sample):
    print("Leyendo señal EEG ->",sample)
    variables_usabilidad=Leer_mensaje()
    if(variables_usabilidad!=None):
        print(variables_usabilidad) # imprime mensaje
        satisfaccion=Medir_Satisfaccion(sample) #clasifica sample con el modelo entrenado
        Guardar_datos(variables_usabilidad,satisfaccion) # guarda los datos en firebase

#simulación de board 
class CBoard:
    def start_stream(self,_print_raw):
        iteraciones=100
        frecuencia=0.250 #simular la frecuencia
        for sample in range(iteraciones):
            time.sleep(frecuencia)
            _print_raw(sample)


#la info de la documentación es así
#board = OpenBCICyton(port='COM5', daisy=False)
board = CBoard()
board.start_stream(print_raw)