from flask import Flask, render_template, request, redirect
from flask.helpers import url_for
from werkzeug.utils import send_from_directory
import os
from app import gerar_legenda

app = Flask(__name__)

app.config['LEGENDAS-PASTA'] = 'legendas/'

@app.route('/')
def main():
   return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if request.method == 'POST':
        video = request.files['video']
        try:
            en = request.form['en']
        except:
            en = 'off'
        try:
            pt = request.form['pt']
        except:
            pt = 'off'
            
        video.save(f'videos/{video.filename}')

        idiomas = []

        if 'on' in en:
            idiomas.append('en')
        if 'on' in pt:
            idiomas.append('pt')
       
        legendas = gerar_legenda(video.filename, idiomas)

        nomes_arquivos = []
        for i in idiomas:
                nomes_arquivos.append(f'{video.filename}.{i}.srt')

        return render_template('download.html', legendas=legendas, arquivos=nomes_arquivos)

@app.route('/download/<path:filename>',  methods=['POST'])
def download(filename):
    if request.method == 'POST':
        print('Escrevendo Arquivo de Legenda...')

        
        with open(f'legendas/{filename}', 'w') as subtitlesfile:
            subtitlesfile.write(request.form['text'])

        diretorio_legendas = os.path.join(app.root_path, app.config['LEGENDAS-PASTA'])
        return send_from_directory(directory=diretorio_legendas, path=filename, environ=request.environ)

if __name__ == "__main__":
    app.run()
