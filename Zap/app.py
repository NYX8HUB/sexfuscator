# app.py
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
import time
import requests

app = Flask(__name__)
app.secret_key = 'idk1919919192929393388393938'  # Chave secreta para o Flask (pode ser qualquer string)

# Função para carregar os usuários a partir do arquivo JSON
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return {}

# Função para carregar mensagens
def load_messages():
    if os.path.exists('messages.json'):
        with open('messages.json', 'r') as f:
            return json.load(f)
    return {}

# Função para salvar mensagens no arquivo JSON
def save_messages(messages):
    with open('messages.json', 'w') as f:
        json.dump(messages, f)

# Função para verificar se o usuário está logado
def is_logged_in():
    return 'user_id' in session

# Página inicial (login)
@app.route('/')
def index():
    return render_template('index.html')

# Login de usuário
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    users = load_users()

    if username in users:
        if users[username]['password'] == password:
            session['user_id'] = users[username]['id']  # Armazenando o id do usuário na sessão
            return redirect(url_for('chat'))
        else:
            return 'Senha incorreta.'
    else:
        return 'Nome de usuário não encontrado.'

# Página de chat
@app.route('/chat')
def chat():
    if not is_logged_in():
        return redirect(url_for('index'))

    users = load_users()
    messages = load_messages()
    user_messages = messages.get(session['user_id'], [])
    return render_template('chat.html', user=users[session['user_id']], messages=user_messages)

# Enviar mensagem
@app.route('/send_message', methods=['POST'])
def send_message():
    if not is_logged_in():
        return redirect(url_for('index'))

    message = request.form['message']
    recipient_id = request.form['recipient_id']
    sender_id = session['user_id']

    # Carregar mensagens
    messages = load_messages()

    if sender_id not in messages:
        messages[sender_id] = []
    if recipient_id not in messages:
        messages[recipient_id] = []

    # Salvar mensagem
    timestamp = time.time()
    messages[sender_id].append({'message': message, 'timestamp': timestamp, 'recipient_id': recipient_id})
    messages[recipient_id].append({'message': message, 'timestamp': timestamp, 'recipient_id': sender_id})

    save_messages(messages)
    return redirect(url_for('chat'))

# Buscar gifs do Tenor
@app.route('/search_gif', methods=['GET'])
def search_gif():
    if not is_logged_in():
        return redirect(url_for('index'))

    query = request.args.get('query')
    api_key = 'AIzaSyCE_tvuPdRnC9CKXS6_Btq6ViE4pplFp3c'  # A chave de API fornecida
    url = f"https://tenor.googleapis.com/v2/search?q={query}&key={api_key}&client_key=my_test_app&limit=8"
    response = requests.get(url).json()

    if response['results']:
        return jsonify(response['results'][0]['media'][0]['gif']['url'])
    return jsonify({'error': 'No GIF found'})

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove o ID do usuário da sessão
    return redirect(url_for('index'))

# Sistema de registro de usuário
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    users = load_users()

    if username not in users:
        user_id = str(len(users) + 1)
        users[username] = {'id': user_id, 'username': username, 'password': password}
        with open('users.json', 'w') as f:
            json.dump(users, f)
        return redirect(url_for('index'))

    return 'Username already exists'

if __name__ == '__main__':
    app.run(debug=True)
