import os
import sys
from flask import Flask, render_template_string, request, send_file
import yt_dlp

app = Flask(__name__)

def log(mensaje):
    print(f"--> {mensaje}", file=sys.stderr)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Descargador Android Mode</title>
    <style>
        body { font-family: sans-serif; background: #000; color: #fff; text-align: center; padding: 40px; }
        .box { border: 1px solid #333; padding: 20px; display: inline-block; background: #111; border-radius: 10px;}
        input, button { padding: 10px; margin: 10px; width: 80%; }
        button { background: #e62117; color: #fff; font-weight: bold; cursor: pointer; border: none; }
    </style>
    <script>
        function cargar() {
            document.getElementById('btn').innerText = "ENVIANDO PETICIÓN...";
            document.getElementById('btn').disabled = true;
        }
    </script>
</head>
<body>
    <div class="box">
        <h1>MODO ANDROID</h1>
        <p>Simulando ser una App móvil para evitar bloqueo.</p>
        <form action="/descargar" method="post" onsubmit="cargar()">
            <input type="text" name="url" placeholder="Link de YouTube..." required>
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
    
    # Limpieza previa
    output = '/tmp/video_final.mp4'
    if os.path.exists(output): os.remove(output)

    log("INICIANDO MODO ANDROID...")
    
    ydl_opts = {
        'outtmpl': output,
        'cookiefile': 'cookies.txt', # Usa tus cookies
        'noplaylist': True,
        'format': 'best[ext=mp4]/best', # Calidad estándar para asegurar éxito
        
        # --- EL TRUCO MAESTRO ---
        # Esto engaña a YouTube para que crea que somos un celular
        'extractor_args': {'youtube': {'player_client': ['android']}},
    }

    try:
        log(f"Descargando: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            
        if os.path.getsize(output) > 0:
            log("¡ÉXITO! Archivo tiene peso.")
            return send_file(output, as_attachment=True, download_name='video.mp4')
        else:
            return "<h1>FALLO:</h1> <p>El archivo se descargó pero pesa 0 bytes.</p>"

    except Exception as e:
        log(f"ERROR: {str(e)}")
        return f"<h1>ERROR TÉCNICO:</h1> <p>{str(e)}</p>"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
