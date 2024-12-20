import os
import time
import json
import random
from flask import Flask, request, jsonify, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configurações
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'apk', 'jpg', 'jpeg', 'gif', 'txt', 'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Função para gerar um ID numérico aleatório de 15 dígitos
def generate_random_id():
    return ''.join(random.choices('0123456789', k=15))

# Função para verificar se a extensão do arquivo é permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Função para carregar os usuários
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return {}

# Função para salvar os usuários
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)

# Função para carregar os arquivos
def load_files():
    if os.path.exists('files.json'):
        with open('files.json', 'r') as f:
            return json.load(f)
    return {}

# Função para salvar os arquivos
def save_files(files):
    with open('files.json', 'w') as f:
        json.dump(files, f)

# Rota para registro de usuários
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    users = load_users()

    if username not in users:
        user_id = generate_random_id()  # Gerando um ID aleatório de 15 dígitos
        users[username] = {'id': user_id, 'username': username, 'password': password}
        save_users(users)
        return redirect(url_for('index'))

    return 'Username already exists'

# Rota para fazer upload de arquivos
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Salvar no JSON com tempo de envio
        uploaded_files = load_files()
        file_id = generate_random_id()  # Gerar ID aleatório de 15 dígitos para o arquivo
        uploaded_files[file_id] = {
            'filename': filename,
            'filepath': filepath,
            'upload_time': time.time(),
            'size': os.path.getsize(filepath)  # Adicionando o tamanho do arquivo em bytes
        }
        save_files(uploaded_files)

        return jsonify({'file_id': file_id, 'filename': filename, 'size': os.path.getsize(filepath)}), 200
    return 'File type not allowed', 400

# Rota para download de arquivos
@app.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    uploaded_files = load_files()
    file = uploaded_files.get(file_id)

    if file:
        # Enviar o arquivo ao usuário
        return send_from_directory(app.config['UPLOAD_FOLDER'], file['filename'], as_attachment=True)
    return 'File not found', 404

# Função para verificar e excluir arquivos expirados (mais de 7 dias)
def delete_expired_files():
    uploaded_files = load_files()
    current_time = time.time()

    # Filtra os arquivos que estão expirados
    files_to_delete = [file_id for file_id, file in uploaded_files.items() if current_time - file['upload_time'] > 604800]  # 604800 segundos = 7 dias

    for file_id in files_to_delete:
        file = uploaded_files[file_id]
        # Deleta o arquivo físico
        if os.path.exists(file['filepath']):
            os.remove(file['filepath'])

        # Deleta a entrada do arquivo no JSON
        del uploaded_files[file_id]

    # Salva as alterações no JSON
    save_files(uploaded_files)

# Rodar a função de exclusão ao iniciar o servidor (ou de forma periódica)
delete_expired_files()  # Chamada direta, mas você pode usar um agendador como APScheduler ou Celery para rodar periodicamente

# Página inicial (login)
@app.route('/')
def index():
    return 'Welcome to the Chat App'

if __name__ == "__main__":
    app.run(debug=True)
