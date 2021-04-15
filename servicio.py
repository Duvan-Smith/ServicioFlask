from flask import Flask,request,jsonify,render_template
import pika
app = Flask(__name__)

@app.route('/api',methods=['POST'])
def Satisfaccion():
    Raw_data=request.json
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='muestra')
    channel.basic_publish(exchange='', routing_key='muestra',body=Raw_data['mensaje'])
    connection.close()
    return jsonify(Raw_data)

@app.route('/',methods=['GET'])
def main():
    return render_template('index.html')

@app.route('/admin',methods=['GET'])
def admin():
    return render_template('index.html')

@app.route('/Configurador',methods=['GET'])
def Configurador():
    return render_template('index.html')

@app.route('/user',methods=['GET'])
def user():
    return render_template('index.html')
    
@app.route('/personalizacion',methods=['GET'])
def personalizacion():
    return render_template('index.html')

@app.route('/demo',methods=['GET'])
def demo():
    return render_template('index.html')