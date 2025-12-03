import threading
import time
import serial
import sys
import pyatspi
from gi.repository import GLib
from flask import Flask, render_template_string

# --- CONFIGURACIÓN ---
SERIAL_PORT = '/dev/ttyACM0'  # Ajusta esto si cambia
BAUD_RATE = 115200

# Estados Globales
MODO_MANUAL = False  # False = Muestra Apps, True = Muestra Emoji fijo
ser = None

# --- CONEXIÓN SERIAL ---
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)
    print(f"✅ Conectado a {SERIAL_PORT}")
except Exception as e:
    print(f"⚠️ Error Serial: {e}")
    print("Modo simulación activado.")

# --- DICCIONARIO DE APPS (Del server.py original) ---
APPS_MAPPING = {
    "Code":               "VSCODE",
    "Firefox":            "FIREFOX",
    "Zen":                "FIREFOX",
    "Spotify":            "YTM",
    "Music":              "YTM",
    "Ptyxis":             "TERM",
    "Terminal":           "TERM",
    "VMware":             "VMWARE",
    "Antigravity":        "GRAVITY",
    "Python":             "GRAVITY",
    "Fedora":             "FEDORA",
    "Discord":            "DISCORD"
}

# ==========================================
# PARTE 1: MONITOR DE VENTANAS (Wayland/X11)
# ==========================================
class WaylandMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.current_app_code = "FEDORA"
        self.current_window_name = "Escritorio"
        
        print("📡 Monitor de Apps Iniciado.")
        # Actualizar reloj cada segundo
        GLib.timeout_add_seconds(1, self.update_clock)

    def get_elapsed_time(self):
        elapsed = time.time() - self.start_time
        m, s = divmod(elapsed, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return "{:02d}:{:02d}:{:02d}".format(int(h), int(m), int(s))
        return "{:02d}:{:02d}".format(int(m), int(s))

    def send_to_pico(self):
        # --- LÓGICA CLAVE ---
        # Si estamos en MODO_MANUAL (Emoji puesto), NO enviamos datos de la ventana
        if MODO_MANUAL:
            return 

        clean_name = self.current_window_name.replace('|', '-')
        # Formato: COMANDO|TIEMPO|DETALLE
        msg = f"{self.current_app_code}|{self.get_elapsed_time()}|{clean_name}\n"
        
        if ser and ser.is_open:
            try:
                ser.write(msg.encode('utf-8'))
            except Exception:
                pass

    def update_clock(self):
        self.send_to_pico()
        return True 

    def on_window_activated(self, event):
        try:
            accessible = event.source
            if not accessible: return

            window_title = accessible.name if accessible.name else ""
            app = accessible.getApplication()
            app_name = app.name if app else ""

            # Detectar código de App
            new_code = "FEDORA"
            full_info = (app_name + " " + window_title).lower()

            for keyword, code in APPS_MAPPING.items():
                if keyword.lower() in full_info:
                    new_code = code
                    break
            
            # Parche específico para YouTube Music en navegadores/electron
            if new_code == "FEDORA" and "YouTube Music" in window_title:
                 new_code = "YTM"

            # Si cambia la App, reiniciamos el cronómetro
            if new_code != self.current_app_code:
                self.start_time = time.time()
                self.current_app_code = new_code
                print(f"🔄 Cambio detectado: {new_code}")
            
            self.current_window_name = window_title
            self.send_to_pico()

        except Exception as e:
            print(f"Error evento: {e}")

# Instancia global del monitor para poder llamarlo desde Flask
monitor = WaylandMonitor()

# ==========================================
# PARTE 2: SERVIDOR WEB (Flask)
# ==========================================
app = Flask(__name__)

# Usamos el mismo HTML bonito de antes
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Control MacroDeck</title>
    <style>
        body { background-color: #000000; color: white; font-family: sans-serif; text-align: center; padding: 10px; }
        .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; max-width: 500px; margin: 0 auto; }
        button { background-color: #222; border: 1px solid #444; border-radius: 10px; font-size: 30px; padding: 15px; cursor: pointer; }
        button:active { background-color: #555; transform: scale(0.95); }
        .label { font-size: 12px; display: block; margin-top: 5px; color: #888; }
        .cancel { grid-column: span 4; background-color: #d32f2f; color: white; font-weight: bold; margin-top: 20px;}
    </style>
</head>
<body>
    <h2>MacroDeck Emojis</h2>
    <div class="grid">
        <button onclick="send('FELIZ')">😀<span class="label">Feliz</span></button>
        <button onclick="send('RISA')">😂<span class="label">Risa</span></button>
        <button onclick="send('BESO')">😘<span class="label">Beso</span></button>
        <button onclick="send('CORAZON')">❤️<span class="label">Amor</span></button>
        <button onclick="send('ABURRIDO')">🥱<span class="label">Aburrido</span></button>
        <button onclick="send('ENFADADO')">🤬<span class="label">Enfadado</span></button>
        <button onclick="send('OJOS')">😳<span class="label">Ojos</span></button>
        <button onclick="send('PENSANDO')">🤔<span class="label">Pensando</span></button>
        <button onclick="send('SUENO')">😴<span class="label">Sueño</span></button>
        <button onclick="send('CAFE')">☕<span class="label">Café</span></button>
        <button onclick="send('PC')">💻<span class="label">PC</span></button>
        <button onclick="send('DEDO')">🖕<span class="label">Dedo</span></button>
        <button onclick="send('PAYASO')">🤡<span class="label">Payaso</span></button>
        <button onclick="send('CACA')">💩<span class="label">Caca</span></button>
        <button onclick="send('OK')">👌<span class="label">OK</span></button>
        <button onclick="send('FANTASMA')">👻<span class="label">Fantasma</span></button>
        
        <button class="cancel" onclick="send('AUTO')">❌ MODO AUTOMÁTICO (APPS)</button>
    </div>
    <script>
        function send(cmd) { fetch('/cmd/' + cmd); }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/cmd/<comando>')
def enviar_comando(comando):
    global MODO_MANUAL
    
    print(f"👉 Web recibió: {comando}")
    
    if comando == "AUTO":
        MODO_MANUAL = False
        # Forzar actualización inmediata con los datos de la app actual
        monitor.send_to_pico()
        print("✅ Regresando a modo Automático")
    else:
        MODO_MANUAL = True
        if ser and ser.is_open:
            # Enviar Emoji: COMANDO|Manual|Emoji
            msg = f"{comando}|Manual|Emoji\n"
            ser.write(msg.encode('utf-8'))
            
    return "OK"

# ==========================================
# LANZAMIENTO (Threading)
# ==========================================
def run_flask():
    # Desactivamos el reloader para que no cause problemas con hilos
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    # 1. Arrancar Servidor Web en un hilo separado (Daemon)
    #    Daemon significa que se cerrará si el programa principal se cierra
    hilo_web = threading.Thread(target=run_flask, daemon=True)
    hilo_web.start()
    print("🌍 Servidor Web iniciado en segundo plano (Puerto 5000)")

    # 2. Arrancar Monitor de Ventanas en el hilo principal
    #    pyatspi necesita estar en el hilo principal usualmente
    pyatspi.Registry.registerEventListener(monitor.on_window_activated, "window:activate")
    
    try:
        pyatspi.Registry.start()
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema...")
        if ser: ser.close()
