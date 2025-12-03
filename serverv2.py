import threading
import time
import serial
import sys
import pyatspi
from gi.repository import GLib
from flask import Flask, render_template_string

# --- CONFIGURACIÓN ---
SERIAL_PORT = '/dev/ttyACM0' 
BAUD_RATE = 115200

MODO_MANUAL = False
ser = None

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)
    print(f"✅ Conectado a {SERIAL_PORT}")
except:
    print("⚠️ Modo simulación (No Serial)")

# --- APPS AUTO ---
APPS_MAPPING = {
    "Code": "VSCODE", "Firefox": "FIREFOX", "Zen": "FIREFOX",
    "Spotify": "SPOTIFY", "Music": "SPOTIFY", "Ptyxis": "TERM",
    "Terminal": "TERM", "VMware": "VMWARE", "Python": "PYTHON",
    "Fedora": "FEDORA", "Discord": "DISCORD"
}

# --- MONITOR ---
class WaylandMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.current_app_code = "FEDORA"
        self.current_window_name = "Escritorio"
        GLib.timeout_add_seconds(1, self.update_clock)

    def get_elapsed_time(self):
        elapsed = time.time() - self.start_time
        m, s = divmod(elapsed, 60)
        h, m = divmod(m, 60)
        return "{:02d}:{:02d}:{:02d}".format(int(h), int(m), int(s)) if h>0 else "{:02d}:{:02d}".format(int(m), int(s))

    def send_to_pico(self):
        if MODO_MANUAL: return 
        clean = self.current_window_name.replace('|', '-')
        msg = f"{self.current_app_code}|{self.get_elapsed_time()}|{clean}\n"
        if ser and ser.is_open:
            try: ser.write(msg.encode('utf-8'))
            except: pass

    def update_clock(self):
        self.send_to_pico(); return True 

    def on_window_activated(self, event):
        try:
            acc = event.source
            if not acc: return
            w_title = acc.name if acc.name else ""
            app = acc.getApplication()
            a_name = app.name if app else ""
            
            new = "FEDORA"
            full = (a_name + " " + w_title).lower()

            for k, c in APPS_MAPPING.items():
                if k.lower() in full: new = c; break
            
            if new != self.current_app_code:
                self.start_time = time.time()
                self.current_app_code = new
                print(f"🔄 App: {new}")
            
            self.current_window_name = w_title
            self.send_to_pico()
        except: pass

monitor = WaylandMonitor()

# --- WEB ---
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PRRPC Control</title>
    <style>
        body { background-color: #1a1a1a; color: #ddd; font-family: sans-serif; text-align: center; margin: 0; padding-bottom: 80px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(60px, 1fr)); gap: 8px; max-width: 900px; margin: 0 auto; padding: 10px; }
        h3 { grid-column: 1/-1; text-align: left; border-bottom: 1px solid #444; margin-top: 20px; color: #888; }
        
        button { 
            background: #333; 
            border: 2px solid #333; /* Borde invisible inicial */
            border-radius: 8px; 
            padding: 10px; 
            font-size: 24px; 
            cursor: pointer; 
            transition: 0.2s all;
        }
        
        button:active { transform: scale(0.9); background: #555; }
        
        /* ESTILO PARA EL BOTÓN ACTIVO */
        button.active {
            background-color: #2e7d32 !important; /* Verde */
            border-color: #4caf50 !important;     /* Borde verde claro */
            color: white;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.6);
            transform: scale(1.05);
        }

        .lbl { display: block; font-size: 9px; margin-top: 4px; color: #aaa; text-transform: uppercase; }
        button.active .lbl { color: white; font-weight: bold; }

        .float-btn { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: #d32f2f; color: white; padding: 15px 30px; border-radius: 50px; font-weight: bold; border:none; box-shadow: 0 4px 10px rgba(0,0,0,0.5); z-index:99; cursor:pointer;}
        .float-btn.active { background-color: #d32f2f !important; border: 2px solid white !important; }
    </style>
</head>
<body>
    <div class="grid">
        <h3>Emociones</h3>
        <button onclick="s('FELIZ', this)">😀<span class="lbl">Feliz</span></button>
        <button onclick="s('RISA', this)">😂<span class="lbl">Risa</span></button>
        <button onclick="s('TRISTE', this)">☹️<span class="lbl">Triste</span></button>
        <button onclick="s('LLORANDO', this)">😭<span class="lbl">Lloro</span></button>
        <button onclick="s('ENFADADO', this)">😡<span class="lbl">Enfado</span></button>
        <button onclick="s('DESAPROB', this)">😒<span class="lbl">Bah</span></button>
        <button onclick="s('ABURRIDO', this)">🥱<span class="lbl">Aburro</span></button>
        <button onclick="s('DORMIDO', this)">😴<span class="lbl">Zzz</span></button>
        <button onclick="s('SORPRESA', this)">😱<span class="lbl">Susto</span></button>
        <button onclick="s('LOKO', this)">🤪<span class="lbl">Loko</span></button>
        <button onclick="s('PAYASO', this)">🤡<span class="lbl">Payaso</span></button>
        <button onclick="s('DIABLO', this)">😈<span class="lbl">Diablo</span></button>
        <button onclick="s('ANGEL', this)">😇<span class="lbl">Angel</span></button>
        <button onclick="s('PERVERTIDO', this)">😏<span class="lbl">Perv</span></button>
        <button onclick="s('SILENCIO', this)">🤫<span class="lbl">Shhh</span></button>
        <button onclick="s('SINBOCA', this)">😶<span class="lbl">Mudo</span></button>
        <button onclick="s('VOMITAR', this)">🤮<span class="lbl">Puaj</span></button>
        <button onclick="s('DERRETIR', this)">🫠<span class="lbl">Melt</span></button>
        <button onclick="s('DUDA', this)">🤷<span class="lbl">Duda</span></button>
        <button onclick="s('PENSANDO', this)">🤔<span class="lbl">Piensa</span></button>
        <button onclick="s('SUPLICAR', this)">🥺<span class="lbl">Porfi</span></button>
        <button onclick="s('TEMBLAR', this)">🫨<span class="lbl">Miedo</span></button>
        <button onclick="s('OJOS', this)">👀<span class="lbl">Ojos</span></button>
        <button onclick="s('EMPOLLON', this)">🤓<span class="lbl">Nerd</span></button>
        <button onclick="s('MOAI', this)">🗿<span class="lbl">Moai</span></button>
        <button onclick="s('SAPO', this)">🐸<span class="lbl">Pepe</span></button>

        <h3>Gestos y Personas</h3>
        <button onclick="s('SALUDO', this)">👋<span class="lbl">Hola</span></button>
        <button onclick="s('OK', this)">👌<span class="lbl">OK</span></button>
        <button onclick="s('BIEN', this)">👍<span class="lbl">Bien</span></button>
        <button onclick="s('APLAUDIR', this)">👏<span class="lbl">Clap</span></button>
        <button onclick="s('REZAR', this)">🙏<span class="lbl">Rezar</span></button>
        <button onclick="s('ABRAZO', this)">🫂<span class="lbl">Abrazo</span></button>
        <button onclick="s('BESO', this)">😘<span class="lbl">Beso</span></button>
        <button onclick="s('KISS_MEN', this)">👨‍❤️‍💋‍👨<span class="lbl">Gay</span></button>
        <button onclick="s('DEDO', this)">🖕<span class="lbl">F**k</span></button>
        <button onclick="s('CALLAR', this)">🙊<span class="lbl">Calla</span></button>
        <button onclick="s('POCO', this)">🤏<span class="lbl">Poco</span></button>
        <button onclick="s('PROFESOR', this)">🧑‍🏫<span class="lbl">Profe</span></button>
        <button onclick="s('MORA', this)">🧕<span class="lbl">Mora</span></button>

        <h3>Cosas y Eventos</h3>
        <button onclick="s('CORAZON', this)">❤️<span class="lbl">Love</span></button>
        <button onclick="s('ROTO', this)">💔<span class="lbl">Roto</span></button>
        <button onclick="s('FIESTA', this)">🥳<span class="lbl">Fiesta</span></button>
        <button onclick="s('PARTY', this)">🎉<span class="lbl">Party</span></button>
        <button onclick="s('CONFETI', this)">🎊<span class="lbl">Confeti</span></button>
        <button onclick="s('REGALO', this)">🎁<span class="lbl">Regalo</span></button>
        <button onclick="s('NAVIDAD', this)">🎄<span class="lbl">Navi</span></button>
        <button onclick="s('FANTASMA', this)">👻<span class="lbl">Boo</span></button>
        <button onclick="s('CACA', this)">💩<span class="lbl">Caca</span></button>
        <button onclick="s('FUMAR', this)">🚬<span class="lbl">Piti</span></button>
        <button onclick="s('PINGUINO', this)">🐧<span class="lbl">Pingu</span></button>
        <button onclick="s('COMIDA', this)">🍽️<span class="lbl">Ñam</span></button>
        <button onclick="s('CAFE', this)">☕<span class="lbl">Cafe</span></button>
        <button onclick="s('DORMIR', this)">🛏️<span class="lbl">Cama</span></button>
        <button onclick="s('CASA', this)">🏠<span class="lbl">Casa</span></button>
        <button onclick="s('VATER', this)">🚽<span class="lbl">WC</span></button>
        <button onclick="s('MOVIL', this)">📱<span class="lbl">Móvil</span></button>
        <button onclick="s('FOTOS', this)">📷<span class="lbl">Foto</span></button>
        <button onclick="s('DINERO', this)">💵<span class="lbl">$$$</span></button>
        <button onclick="s('STONKS', this)">📈<span class="lbl">Stonks</span></button>
        <button onclick="s('NOTSTONKS', this)">📉<span class="lbl">Bad</span></button>
        <button onclick="s('PROHIBIDO', this)">⛔<span class="lbl">No</span></button>
        <button onclick="s('TIMBRE', this)">🔔<span class="lbl">Ding</span></button>
        <button onclick="s('PREGUNTA', this)">❓<span class="lbl">Que?</span></button>
        <button onclick="s('LLUVIA', this)">☔<span class="lbl">Lluvia</span></button>
        <button onclick="s('ESPANA', this)">🇪🇸<span class="lbl">Esp</span></button>
        <button onclick="s('GAYS', this)">🏳️‍🌈<span class="lbl">Pride</span></button>

        <h3>Apps (Forzar)</h3>
        <button onclick="s('ORDENADOR', this)">💻<span class="lbl">PC</span></button>
        <button onclick="s('VSCODE', this)">📝<span class="lbl">Code</span></button>
        <button onclick="s('FIREFOX', this)">🦊<span class="lbl">Fox</span></button>
        <button onclick="s('SPOTIFY', this)">🎵<span class="lbl">Music</span></button>
        <button onclick="s('PYTHON', this)">🐍<span class="lbl">Py</span></button>
    </div>

    <button id="btn-auto" class="float-btn active" onclick="s('AUTO', this)">❌ MODO AUTO</button>

    <script>
        function s(cmd, el) {
            // Enviar comando
            fetch('/cmd/' + cmd);
            
            // 1. Quitar la clase 'active' de TODOS los botones
            document.querySelectorAll('button').forEach(btn => {
                btn.classList.remove('active');
            });

            // 2. Añadir clase 'active' SOLO al botón pulsado (el)
            if (el) {
                el.classList.add('active');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/cmd/<cmd>')
def command(cmd):
    global MODO_MANUAL
    if cmd == "AUTO":
        MODO_MANUAL = False
        monitor.send_to_pico()
    else:
        MODO_MANUAL = True
        if ser: ser.write(f"{cmd}|Manual|Emoji\n".encode())
    return "OK"

if __name__ == "__main__":
    t = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False), daemon=True)
    t.start()
    print("🌍 Panel: http://localhost:5000")
    
    pyatspi.Registry.registerEventListener(monitor.on_window_activated, "window:activate")
    try: pyatspi.Registry.start()
    except: pass
