import time
import pika, sys, os
import joblib
import numpy as np
import pandas as pd
from firebase import firebase
from pyOpenBCI import OpenBCICyton
import json
import mne
import scipy
from scipy import stats
from scipy.signal import filtfilt
from scipy import signal

model = joblib.load(r'C:\Users\Duvan\OneDrive\Documentos\TraingEEG\Results\results\RandoFores\model\Ex1.pkl')
variables_usabilidad_Anterior=None
variables_usabilidad_Comparar=None
satisfaccion=[]
firebaseV=None

def Predition(data):
    return model.predict(data)

def notch_filter(val, data, fs=250):
    notch_freq_Hz = np.array([float(val)])
    for freq_Hz in np.nditer(notch_freq_Hz):
        bp_stop_Hz = freq_Hz + 3.0 * np.array([-1, 1])
        b, a = signal.butter(3, bp_stop_Hz / (fs / 2.0), 'bandstop')
        fin = data = signal.lfilter(b, a, data)
    return fin

# Bandpass filter
def bandpass(start, stop, data, fs = 250):
    bp_Hz = np.array([start, stop])
    b, a = signal.butter(5, bp_Hz / (fs / 2.0), btype='bandpass')
    return signal.lfilter(b, a, data, axis=0)

#leer mensaje
def Medir_Satisfaccion(sample):
    return Predition(sample)[0]

def Guardar_datos(variables_usabilidad,medida_de_satisfaccion):
    global firebaseV

    data=np.array(medida_de_satisfaccion)
    satisfaccionG=np.average(data)#se tiene el promedio

    print()
    data = json.loads(variables_usabilidad)
    print("json1:",data)
    print("color:",data['color'])
    print("letra:",data['letra'])
    print()
    
    new_user=data['uid']
    save_color=data['color']
    save_pletra=data['posicionLetra']
    save_letra=data['letra']
    save_titulo=data['titulo']
    save_subtitulo=data['subtitulo']
    save_parrafos=data['parrafos']
    save_imagen=data['imagen']
    save_contenidos=data['contenidos']

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

def print_raw(sample):
    sample=sample.channels_data
    sample=sample[0:10]
    sample=np.array([sample])
    global variables_usabilidad_Anterior
    global variables_usabilidad_Comparar
    global satisfaccion

    variables_usabilidad=Leer_mensaje()

    #Se ponen los mismos filtros utilizados para el entrenamiento del algoritmo
    sample = bandpass(1, 40, sample)
    sample = notch_filter(60, sample)

    if(variables_usabilidad!=None and variables_usabilidad_Anterior==None):
        satisfaccion.append(Medir_Satisfaccion(sample))

    elif(variables_usabilidad!=variables_usabilidad_Anterior and variables_usabilidad_Anterior!=None):
        satisfaccion.append(Medir_Satisfaccion(sample))

    if(variables_usabilidad!=None):
        variables_usabilidad_Comparar=variables_usabilidad_Anterior
        variables_usabilidad_Anterior=variables_usabilidad
            
    if(variables_usabilidad_Comparar!=None and variables_usabilidad!=None and variables_usabilidad_Comparar!=variables_usabilidad_Anterior):
        Guardar_datos(variables_usabilidad_Comparar,satisfaccion)
        satisfaccion=[]
        if("FinTomaMuestraUsuario" in variables_usabilidad.decode("utf-8")):
            print("Entro en FinTomaMuestraUsuario")
            variables_usabilidad=None
            variables_usabilidad_Anterior=None
            variables_usabilidad_Comparar=None
            satisfaccion=[]
    else:
        print("Sample:",sample)
        
board = OpenBCICyton(daisy=True)

board.start_stream(print_raw)
