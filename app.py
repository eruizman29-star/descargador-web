import os
import traceback
from flask import Flask, render_template_string, request, send_file
import yt_dlp

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Descargador Ligero</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: white; text-align: center; padding: 40px; }
        .box { background: #1e1e1e; padding: 40px; border-radius: 15px; display: inline-block; width: 100%; max-width: 500px; }
        input, select, button { width: 100%; padding: 15px; margin: 10px 0; border-radius: 5px; border: none; }
        button { background: #007bff; color: white; font-weight: bold; cursor: pointer; }
    </style>
    <script>
        function cargar() {
            document.getElementById('btn').innerText = "PROCESANDO...";
            document.getElementById('btn').disabled = true;
        }
    </script>
</head>
<body>
    <div class="box">
        <h1>Descargador (Modo Seguro)</h1>
        <form action="/descargar" method="post" onsubmit="cargar()">
            <input type="text" name="url" placeholder="Enlace de YouTube..." required>
            <select name="calidad">
                <option value="video">Video (720p/MP4 - Rápido)</option>
                <option value="audio">Solo Audio (MP3)</option>
            </select>
            <button type="submit" id="btn">DESCARGAR</button>
        </form>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/descargar', methods=['POST'])
def descargar():
    url = request.form.get('url')
    calidad = request.form.get('calidad')
    
    # Usamos /tmp para descargas temporales
    output_path = '/tmp/%(title)s.%(ext)s'

    ydl_opts = {
        'outtmpl': output_path,
        'cookiefile': 'cookies.txt', # Intenta usar cookies si existen
        'noplaylist': True,
        'restrictfilenames': True, # Evita nombres con caracteres raros
    }

    if calidad == 'audio':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]
    else:
        # TRUCO PARA QUE NO EXPLOTE LA RAM:
        # Pedimos el mejor mp4 que NO necesite unir video+audio (suele ser 720p)
        ydl_opts['format'] = 'best[ext=mp4]/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Corrección de nombre para audio
            if calidad == 'audio':
                base = os.path.splitext(filename)[0]
                filename = base + ".mp3"

            return send_file(filename, as_attachment=True)

    except Exception as e:
        # Esto imprime el error real en tu pantalla en vez del "Internal Server Error"
        error_msg = traceback.format_exc()
        return f"<h3>Ocurrió un error (Muestrale esto al técnico):</h3><pre>{error_msg}</pre>"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
