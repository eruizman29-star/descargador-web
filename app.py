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
            document.getElementById('btn').innerText = "PROCESANDO (NO CIERRES)...";
            document.getElementById('btn').disabled = true;
        }
    </script>
</head>
<body>
    <div class="box">
        <h1>Descargador Web (con Cookies)</h1>
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
    
    # OPCIONES DE DESCARGA
    ydl_opts = {
        'outtmpl': '/tmp/%(title)s.%(ext)s',
        'noplaylist': True,
        'cookiefile': 'cookies.txt',  # <--- ¡ESTA ES LA LÍNEA MÁGICA!
        # Trucos anti-bloqueo extra:
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
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base = os.path.splitext(filename)[0]
            
            final = base + (".mp3" if calidad == 'audio' else ".mp4")
            
            if not os.path.exists(final):
                for f in os.listdir('/tmp'):
                    if f.startswith(os.path.basename(base)):
                        final = os.path.join('/tmp', f)
                        break

            return send_file(final, as_attachment=True)
    except Exception as e:
        return f"Error de YouTube: {str(e)} <br> Intenta actualizar el archivo cookies.txt en GitHub."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
