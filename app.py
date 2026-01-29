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
    <title>Descargador IPv4</title>
    <style>
        body { font-family: sans-serif; background: #0a0a0a; color: #00ff00; text-align: center; padding: 40px; }
        .box { border: 2px solid #00ff00; padding: 20px; display: inline-block; background: #000; border-radius: 10px;}
        input, button { padding: 10px; margin: 10px; width: 80%; }
        button { background: #00ff00; color: #000; font-weight: bold; cursor: pointer; border: none; }
    </style>
    <script>
        function cargar() {
            document.getElementById('btn').innerText = "INTENTANDO CONEXIÓN IPv4...";
            document.getElementById('btn').disabled = true;
        }
    </script>
</head>
<body>
    <div class="box">
        <h1>MODO IPv4</h1>
        <p>Forzando conexión estándar para evitar bloqueos.</p>
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
    output = '/tmp/video.mp4'
    if os.path.exists(output): os.remove(output)

    log("INICIANDO MODO IPv4...")
    
    ydl_opts = {
        'outtmpl': output,
        'cookiefile': 'cookies.txt', # TUS COOKIES SON VITALES AQUÍ
        'noplaylist': True,
        
        # --- EL ARREGLO ---
        'force_ipv4': True,  # Obliga a usar la red compatible
        'format': 'best[ext=mp4]/best', # Busca archivo único (ahorra RAM)
        'socket_timeout': 30,
    }

    try:
        log(f"Descargando: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            
        if os.path.exists(output) and os.path.getsize(output) > 1024:
            log("¡ÉXITO! Archivo descargado.")
            return send_file(output, as_attachment=True, download_name='video.mp4')
        else:
            return "<h1>ERROR:</h1> <p>YouTube aceptó la conexión pero envió un archivo vacío. Tus cookies pueden estar quemadas.</p>"

    except Exception as e:
        log(f"ERROR: {str(e)}")
        return f"<h1>ERROR TÉCNICO:</h1> <p>{str(e)}</p>"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
