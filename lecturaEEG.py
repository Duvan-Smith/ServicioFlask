import time
import pika, sys, os
import joblib
import numpy as np
import pandas as pd

model = joblib.load(r'C:\Users\Duvan\OneDrive\Documentos\TraingEEG\Results\results\RandoFores\model\Ex1.pkl')
variables_usabilidad_Anterior=None
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
    print("promedio:",satisfaccionG)
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
    global variables_usabilidad_Anterior
    global satisfaccion
    global s2
    variables_usabilidad=Leer_mensaje()
    print("No se guarda")
    if(variables_usabilidad!=None and variables_usabilidad_Anterior==None):
        s1=satisfaccion.append(Medir_Satisfaccion(sample)) #clasifica sample con el modelo entrenado
        s2.append(s1)
        print("if1")
        for s in satisfaccion:
            print("rts:",s)
        for s in s2:
            print("rts2:",s)
        print()
    elif(variables_usabilidad!=variables_usabilidad_Anterior and variables_usabilidad_Anterior!=None):
        s3=satisfaccion.append(Medir_Satisfaccion(sample)) #clasifica sample con el modelo entrenado
        s2.append(s3)
        print("elif1")
        for s in satisfaccion:
            print("rts3:",s)
        for s in s2:
            print("rts4:",s)
        print()

    if(variables_usabilidad!=None):
        variables_usabilidad_Anterior=variables_usabilidad
        # satisfaccion=[]
        # print("variables_usabilidad",variables_usabilidad)
        # print("variables_usabilidad_Anterior",variables_usabilidad_Anterior)
        print("if3",variables_usabilidad_Anterior)
        print()

    if((variables_usabilidad!=variables_usabilidad_Anterior) and (variables_usabilidad_Anterior!=None)):
        print("Se guarda ->",sample)
        Guardar_datos(variables_usabilidad_Anterior,satisfaccion) # guarda los datos en firebase
        satisfaccion=[]
        

#simulación de board 
class CBoard:
    def start_stream(self,_print_raw):
        iteraciones=150
        frecuencia=0.325 #simular la frecuencia
        data = pd.read_csv(r"C:\Users\Duvan\OneDrive\Documentos\TraingEEG\DataSetConstruido\User1SerCsvMaOne.csv",)
        data = np.array(data, dtype="float")
        for d in data:
            time.sleep(frecuencia)
            d2=np.delete(d, 10)#Esta linea se eliminara al trabajar con los datos reales
            sample=np.array([d2])
            _print_raw(sample)
        # for sample in range(iteraciones):
        #     time.sleep(frecuencia)
        #     _print_raw(sample)


#la info de la documentación es así
#board = OpenBCICyton(port='COM5', daisy=False)
board = CBoard()
board.start_stream(print_raw)