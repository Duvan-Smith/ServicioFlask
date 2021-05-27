import time
import pika, sys, os
import joblib
import numpy as np
import pandas as pd
from firebase import firebase
import json
import mne
import scipy
from scipy import stats
from scipy.signal import filtfilt
from scipy import signal

model = joblib.load(r'C:\Users\Asus\Documents\GitHub\Tesis\ServicioFlask\Recursos\Ex1.pkl')
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

# leer mensaje
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
    new_usuario=data['usuario']
    save_color=data['color']
    save_pletra=data['posicionLetra']
    save_letra=data['letra']
    save_titulo=data['titulo']
    save_subtitulo=data['subtitulo']
    save_parrafos=data['parrafos']
    save_imagen=data['imagen']
    save_contenidos=data['contenidos']
    save_fechaYHora=data['fechaYHora']

    firebaseV = firebase.FirebaseApplication("https://pagina-personalizable-default-rtdb.firebaseio.com/", None)

    componenteUser={
        "usuario":new_usuario,
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
        "fechaYHora":save_fechaYHora,
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

    #Se ponen los mismos filtros utilizados para el entrenamiento del algoritmo
    sample = bandpass(1, 40, sample)
    sample = notch_filter(60, sample)

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
        data = pd.read_csv(r"C:\Users\Asus\Documents\GitHub\Tesis\ServicioFlask\Recursos\User1SerCsvMaOne.csv",)
        data = np.array(data, dtype="float")
        for d in data:
            time.sleep(frecuencia)
            sample=np.delete(d, 10)#Esta linea se eliminara al trabajar con los datos reales
            sample=np.array([sample])
            sample=np.array(sample)
            _print_raw(sample)

board = CBoard()
board.start_stream(print_raw)