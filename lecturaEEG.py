import time
import pika, sys, os
import joblib
import numpy as np
import pandas as pd
from firebase import firebase
import json
import mne

model = joblib.load(r'C:\Users\Duvan\OneDrive\Documentos\TraingEEG\Results\results\RandoFores\model\Ex1.pkl')
variables_usabilidad_Anterior=None
variables_usabilidad_Comparar=None
satisfaccion=[]
firebaseV=None

def Predition(data):
    return model.predict(data)

# def filters(raw,lowfrec,highpass):
#     raw_highpass = raw.filter(l_freq=lowfrec, h_freq=highpass)
#     freqs = (60)
#     raw_notch_fit = raw_highpass.notch_filter(freqs=freqs, method='spectrum_fit', filter_length='12s')
#     return raw_notch_fit

#leer mensaje
def Medir_Satisfaccion(sample):
    #Extraer de la lectura un array con la forma(shape) requerido por el modelo entrenado
    #el valor debe ser el porcentaje
    #Deben estar los filtros=crear funcion
    return Predition(sample)[0]
def Guardar_datos(variables_usabilidad,medida_de_satisfaccion):
    global firebaseV
    data=np.array(medida_de_satisfaccion)
    satisfaccionG=np.average(data)#se tiene el promedio
    print()
    variables_usabilidad=variables_usabilidad.decode("utf-8")
    print(variables_usabilidad)
    print()

    new_user = variables_usabilidad[variables_usabilidad.find('"uid":"'):variables_usabilidad.find('","color"')]
    new_user=new_user[7:]

    save_color = variables_usabilidad[variables_usabilidad.find('"color":"'):variables_usabilidad.find('","posicionLetra":"')]
    save_color=save_color[9:]

    save_pletra = variables_usabilidad[variables_usabilidad.find('","posicionLetra":"'):variables_usabilidad.find('","letra":{"nombre":"')]
    save_pletra=save_pletra[19:]

    save_titulo = variables_usabilidad[variables_usabilidad.find(',"titulo":"'):variables_usabilidad.find('","subtitulo":"')]
    save_titulo=save_titulo[11:]

    aux_letra=save_pletra+'","letra":'
    print(aux_letra,len(aux_letra))
    aux_letra2=',"titulo":"'+save_titulo

    save_letra = variables_usabilidad[variables_usabilidad.find(aux_letra):variables_usabilidad.rfind(aux_letra2)]
    save_letra=save_letra[len(aux_letra):]
    print(save_letra)

    

    save_subtitulo = variables_usabilidad[variables_usabilidad.find('","subtitulo":"'):variables_usabilidad.find('","parrafos":')]
    save_subtitulo=save_subtitulo[15:]

    save_parrafos = variables_usabilidad[variables_usabilidad.find('","parrafos":'):variables_usabilidad.find(',"imagen":"')]
    save_parrafos=save_parrafos[13:]

    aux_imagen=save_parrafos+',"imagen":"'
    save_imagen = variables_usabilidad[variables_usabilidad.rfind(aux_imagen):variables_usabilidad.find('","contenidos":{')]
    save_imagen=save_imagen[13:]
    print()

    save_contenidos = variables_usabilidad[variables_usabilidad.find('","contenidos":'):variables_usabilidad.rfind('}')]
    save_contenidos=save_contenidos[15:]
    print()

    firebaseV = firebase.FirebaseApplication("https://pagina-personalizable-default-rtdb.firebaseio.com/", None)

    componenteUser={
        "user":new_user,
        "eeg":medida_de_satisfaccion,
        "promedio":satisfaccionG,
        "color":save_color,
        "posicionLetra":save_pletra,
        "letra":save_letra,
        "titulo":save_titulo,
        "subtitulo":save_subtitulo,
        "parrafos":save_parrafos,
        "imagen":save_imagen,
        "contenidos":save_contenidos,
        # "componente":variables_usabilidad,
    }

    new_componente = '/componenteUser/'+new_user
    print()
    result=firebaseV.post(new_componente,componenteUser)
    print("post",result)
    print()
    #http://ozgur.github.io/python-firebase/

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
    global variables_usabilidad_Comparar
    global satisfaccion

    variables_usabilidad=Leer_mensaje()

    # sample=filters(sample,1,40)

    if(variables_usabilidad!=None and variables_usabilidad_Anterior==None):
        satisfaccion.append(Medir_Satisfaccion(sample)) #clasifica sample con el modelo entrenado

    elif(variables_usabilidad!=variables_usabilidad_Anterior and variables_usabilidad_Anterior!=None):
        satisfaccion.append(Medir_Satisfaccion(sample)) #clasifica sample con el modelo entrenado

    if(variables_usabilidad!=None):
        variables_usabilidad_Comparar=variables_usabilidad_Anterior
        variables_usabilidad_Anterior=variables_usabilidad
            
    if(variables_usabilidad_Comparar!=None and variables_usabilidad!=None and variables_usabilidad_Comparar!=variables_usabilidad_Anterior):
        Guardar_datos(variables_usabilidad_Comparar,satisfaccion) # guarda los datos en firebase
        satisfaccion=[]
        if("FinTomaMuestraUsuario" in variables_usabilidad.decode("utf-8")):
            print("Entro en FinTomaMuestraUsuario")
            variables_usabilidad=None
            variables_usabilidad_Anterior=None
            variables_usabilidad_Comparar=None
            satisfaccion=[]
    else:
        print("Sample:",sample)

#simulación de board 
class CBoard:
    def start_stream(self,_print_raw):
        iteraciones=150
        frecuencia=1 #simular la frecuencia
        data = pd.read_csv(r"C:\Users\Duvan\OneDrive\Documentos\TraingEEG\DataSetConstruido\User1SerCsvMaOne.csv",)
        data = np.array(data, dtype="float")
        for d in data:
            time.sleep(frecuencia)
            d2=np.delete(d, 10)#Esta linea se eliminara al trabajar con los datos reales
            sample=np.array([d2])
            _print_raw(sample)

board = CBoard()
board.start_stream(print_raw)