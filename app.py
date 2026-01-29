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
    <title>Descargador Universal</title>
    <style>
        body { font-family: sans-serif; background: #000; color: #fff; text-align: center; padding: 40px; }
        .box { border: 1px solid #fff; padding: 20px; display: inline-block; background: #222; border-radius: 10px;}
        input, button { padding: 10px; margin: 10px; width: 80%; }
        button { background: #fff; color: #000; font-weight: bold; cursor: pointer; border: none; }
    </style>
    <script>
        function cargar() {
            document.getElementById('btn').innerText = "BAJANDO...";
            document.getElementById('btn').disabled = true;
        }
    </script>
</head>
<body>
    <div class="box">
        <h1>MODO IPHONE</h1>
        <p>Este modo es más compatible con servidores.</p>
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
    
    # Limpiamos
    output = '/tmp/video_descargado.mp4'
    if os.path.exists(output): os.remove(output)

    log("INICIANDO MODO IOS...")
    
    ydl_opts = {
        'outtmpl': output,
        'cookiefile': 'cookies.txt',
        'noplaylist': True,
        
        # CAMBIO 1: Pedimos "best" a secas.
        # "best" busca el mejor archivo ÚNICO (video+audio juntos).
        # Esto evita el error de "Requested format not available" y ahorra RAM.
        'format': 'best', 
        
        # CAMBIO 2: Simulamos ser un iPhone (iOS)
        # Los iPhones suelen recibir formatos más compatibles (.mp4/.m3u8) que Android.
        'extractor_args': {'youtube': {'player_client': ['ios']}},
    }

    try:
        log(f"Intentando: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            
        if os.path.exists(output) and os.path.getsize(output) > 0:
            log("¡CONSEGUIDO!")
            return send_file(output, as_attachment=True, download_name='video.mp4')
        else:
            # Plan B: Si falla el nombre exacto, buscamos cualquier archivo en /tmp
            import glob
            archivos = glob.glob('/tmp/*')
            # Filtramos para no agarrar cookies.txt u otros
            archivos_video = [f for f in archivos if len(f) > 10 and not f.endswith('.txt')]
            
            if archivos_video:
                log(f"Encontrado archivo alternativo: {archivos_video[0]}")
                return send_file(archivos_video[0], as_attachment=True, download_name='video.mp4')
            
            return "<h1>FALLO:</h1> <p>Parece que el video se descargó pero no lo encuentro con el nombre esperado.</p>"

    except Exception as e:
        log(f"ERROR: {str(e)}")
        return f"<h1>ERROR:</h1> <p>{str(e)}</p>"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
