import os
import glob
from flask import Flask, render_template_string, request, send_file
import yt_dlp

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Descargador Cloud</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: white; text-align: center; padding: 40px; }
        .box { background: #1e1e1e; padding: 40px; border-radius: 15px; display: inline-block; width: 100%; max-width: 500px; }
        input, select, button { width: 100%; padding: 15px; margin: 10px 0; border-radius: 5px; border: none; }
        button { background: #d32f2f; color: white; font-weight: bold; cursor: pointer; }
    </style>
    <script>
        function cargar() {
            document.getElementById('btn').innerText = "DESCARGANDO...";
            document.getElementById('btn').disabled = true;
        }
    </script>
</head>
<body>
    <div class="box">
        <h1>Descargador Web</h1>
        <form action="/descargar" method="post" onsubmit="cargar()">
            <input type="text" name="url" placeholder="Enlace de YouTube..." required>
            <select name="calidad">
                <option value="best">Mejor Calidad (Video+Audio)</option>
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
    
    # Limpiamos la carpeta temporal antes de empezar
    files = glob.glob('/tmp/*')
    for f in files:
        try: os.remove(f)
        except: pass

    # Configuración BLINDADA
    ydl_opts = {
        # Guardamos SIEMPRE como 'video' para evitar errores de nombres raros
        'outtmpl': '/tmp/video.%(ext)s', 
        'cookiefile': 'cookies.txt',
        'noplaylist': True,
        'socket_timeout': 30, # Esperar más si YouTube tarda
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    if calidad == 'audio':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]
    else:
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
        ydl_opts['merge_output_format'] = 'mp4'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            
            # Buscar qué archivo se creó (video.mp4 o video.mp3)
            if os.path.exists('/tmp/video.mp3'):
                return send_file('/tmp/video.mp3', as_attachment=True, download_name='audio_descargado.mp3')
            elif os.path.exists('/tmp/video.mp4'):
                return send_file('/tmp/video.mp4', as_attachment=True, download_name='video_descargado.mp4')
            else:
                # Búsqueda desesperada de cualquier archivo
                found = glob.glob('/tmp/video*')
                if found:
                    return send_file(found[0], as_attachment=True, download_name=os.path.basename(found[0]))
                return "Error: YouTube bloqueó la descarga (Archivo vacío)."

    except Exception as e:
        return f"Error técnico: {str(e)} <br> Probablemente las cookies caducaron."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
