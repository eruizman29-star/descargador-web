import os
import sys
from flask import Flask, render_template_string, request, send_file
import yt_dlp

app = Flask(__name__)

# Función para que los mensajes salgan en la pantalla negra de Render
def log(mensaje):
    print(f"--> {mensaje}", file=sys.stderr)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Test Ligero</title>
    <style>
        body { font-family: sans-serif; background: #000; color: #0f0; text-align: center; padding: 40px; }
        .box { border: 2px solid #0f0; padding: 20px; display: inline-block; }
        input, button { padding: 10px; margin: 10px; }
        button { background: #0f0; color: #000; font-weight: bold; cursor: pointer; }
    </style>
    <script>
        function cargar() {
            document.getElementById('btn').innerText = "TRABAJANDO (Mira los Logs en Render)...";
            document.getElementById('btn').disabled = true;
        }
    </script>
</head>
<body>
    <div class="box">
        <h1>MODO DIAGNÓSTICO</h1>
        <p>Este modo descarga en baja calidad para probar la conexión.</p>
        <form action="/descargar" method="post" onsubmit="cargar()">
            <input type="text" name="url" placeholder="Link de YouTube..." required>
            <button type="submit" id="btn">PROBAR DESCARGA</button>
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
    
    # RUTA TEMPORAL
    output = '/tmp/prueba.mp4'
    if os.path.exists(output):
        os.remove(output)

    log("INICIANDO DESCARGA...")
    
    ydl_opts = {
        'outtmpl': output,
        'cookiefile': 'cookies.txt',
        'noplaylist': True,
        # ESTO ES CLAVE: Bajamos la PEOR calidad para ver si funciona sin gastar RAM
        'format': 'worst', 
    }

    try:
        log(f"Intentando descargar: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            
        log("DESCARGA COMPLETADA EN EL SERVIDOR")
        log("ENVIANDO AL USUARIO...")
        
        return send_file(output, as_attachment=True, download_name='video_prueba.mp4')

    except Exception as e:
        log(f"ERROR FATAL: {str(e)}")
        return f"<h1>FALLO:</h1> <p>{str(e)}</p>"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
