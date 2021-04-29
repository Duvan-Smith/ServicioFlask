import time
import pika, sys, os
import joblib
import numpy as np
import pandas as pd
from firebase import firebase
from pyOpenBCI import OpenBCICyton

model = joblib.load(r'C:\Users\Duvan\OneDrive\Documentos\TraingEEG\Results\results\RandoFores\model\Ex1.pkl')
variables_usabilidad_Anterior=None
variables_usabilidad_Comparar=None
satisfaccion=[]
s2=[]

def Predition(data):
    return model.predict(data)

#leer mensaje
def Medir_Satisfaccion(sample):
    #Extraer de la lectura un array con la forma(shape) requerido por el modelo entrenado
    #el valor debe ser el porcentaje
    #Deben estar los filtros=crear funcion
    return Predition(sample)[0]
def Guardar_datos(variables_usabilidad,medida_de_satisfaccion):
    data=np.array(medida_de_satisfaccion)
    satisfaccionG=np.average(data)#se tiene el promedio
    print()
    print("variables_usabilidad:",variables_usabilidad)
    print("medida_de_satisfaccion:",medida_de_satisfaccion)
    print("promedio:",satisfaccionG)
    # firebase = firebase.FirebaseApplication('https://console.firebase.google.com/project/pagina-personalizable', None)
    # new_user = 'Ozgur Vatansever'

    # result = firebase.post('/users', new_user, {'print': 'pretty'}, {'X_FANCY_HEADER': 'VERY FANCY'})
    # print(result)
    # medida_de_satisfaccion=sacar el promedio
    # sumar y con lend da el promedio - 
    #Se guarda el promedio y las bariables lend y filter==1,filter==0 y eso se guarda
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
    sample=sample.channels_data
    global variables_usabilidad_Anterior
    global variables_usabilidad_Comparar
    global satisfaccion

    variables_usabilidad=Leer_mensaje()

    if(variables_usabilidad!=None and variables_usabilidad_Anterior==None):
        satisfaccion.append(Medir_Satisfaccion(sample)) #clasifica sample con el modelo entrenado
    elif(variables_usabilidad!=variables_usabilidad_Anterior and variables_usabilidad_Anterior!=None):
        satisfaccion.append(Medir_Satisfaccion(sample)) #clasifica sample con el modelo entrenado

    if(variables_usabilidad!=None):
            variables_usabilidad_Comparar=variables_usabilidad_Anterior
            variables_usabilidad_Anterior=variables_usabilidad
            
    if(variables_usabilidad_Comparar!=None and variables_usabilidad!=None and variables_usabilidad_Comparar!=variables_usabilidad_Anterior):
        Guardar_datos(variables_usabilidad_Anterior,satisfaccion) # guarda los datos en firebase
        satisfaccion=[]
    else:
        print("No se guarda")

#simulación de board 
# class CBoard:
#     def start_stream(self,_print_raw):
#         iteraciones=150
#         frecuencia=1 #simular la frecuencia
#         data = pd.read_csv(r"C:\Users\Duvan\OneDrive\Documentos\TraingEEG\DataSetConstruido\User1SerCsvMaOne.csv",)
#         data = np.array(data, dtype="float")
#         for d in data:
#             time.sleep(frecuencia)
#             d2=np.delete(d, 10)#Esta linea se eliminara al trabajar con los datos reales
#             sample=np.array([d2])
#             _print_raw(sample)
        # for sample in range(iteraciones):
        #     time.sleep(frecuencia)
        #     _print_raw(sample)


#la info de la documentación es así
#board = OpenBCICyton(port='COM5', daisy=False)

# board = CBoard()
# board.start_stream(print_raw)
# def print_raw(sample):
#     print(sample.channels_data)

# board = OpenBCICyton(port='COM5', daisy=True) #Para windows, verificar port
board = OpenBCICyton(daisy=True) # Probar

board.start_stream(print_raw)