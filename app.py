import os
from flask import Flask, render_template_string, request, send_file
import yt_dlp

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Descargador Online</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: white; text-align: center; padding: 40px; }
        .box { background: #1e1e1e; padding: 40px; border-radius: 15px; display: inline-block; width: 100%; max-width: 500px; }
        input, select, button { width: 100%; padding: 15px; margin: 10px 0; border-radius: 5px; border: none; }
        button { background: #d32f2f; color: white; font-weight: bold; cursor: pointer; }
        button:hover { background: #b71c1c; }
    </style>
    <script>
        function cargar() {
            document.getElementById('btn').innerText = "PROCESANDO EN LA NUBE...";
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
                <option value="best">Video HD + Audio</option>
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
    
    # En la nube usamos /tmp porque no tenemos carpeta de usuario
    ydl_opts = {
        'outtmpl': '/tmp/%(title)s.%(ext)s',
        'noplaylist': True,
        # Ya no ponemos ffmpeg_location porque Docker lo instalará en el sistema
    }

    if calidad == 'audio':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]
    else:
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
        ydl_opts['merge_output_format'] = 'mp4'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base = os.path.splitext(filename)[0]
            # Ajuste de extensiones
            final = base + (".mp3" if calidad == 'audio' else ".mp4")
            
            # Buscar si quedó como mkv o webm por seguridad
            if not os.path.exists(final):
                for f in os.listdir('/tmp'):
                    if f.startswith(os.path.basename(base)):
                        final = os.path.join('/tmp', f)
                        break

            return send_file(final, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    # Esto permite que Render asigne el puerto automáticamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)