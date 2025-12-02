import pyatspi
import serial
import time
import sys
from gi.repository import GLib

# --- CONFIGURACIÓN ---
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200

# DICCIONARIO INTELIGENTE
# Buscaremos estas palabras CLAVE tanto en el nombre de la App como en el Título
APPS_MAPPING = {
    "Code":               "VSCODE",    # Atrapa "Visual Studio Code" y "Code"
    "Firefox":            "FIREFOX",   # Atrapa "Mozilla Firefox"
    "Zen":                "FIREFOX",   # Zen Browser
    "Spotify":            "YTM",       
    "Music":              "YTM",       # Atrapa "YouTube Music", "Apple Music"
    "Ptyxis":             "TERM",
    "Terminal":           "TERM",
    "VMware":             "VMWARE",
    "Antigravity":        "GRAVITY",
    "Python":             "GRAVITY",
    "Fedora":             "FEDORA"     # Para detectar escritorio/sistema
}

class WaylandMonitor:
    def __init__(self):
        self.ser = None
        self.connect_serial()
        self.start_time = time.time()
        self.current_app_code = "FEDORA"
        self.current_window_name = "Escritorio"
        
        print("📡 Monitor Wayland V2 (X11-Frames Fix) Iniciado.")
        
        # Timer para actualizar el reloj cada segundo
        GLib.timeout_add_seconds(1, self.update_clock)

    def connect_serial(self):
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
            time.sleep(2)
            print(f"✅ Conectado a {SERIAL_PORT}")
        except Exception as e:
            print(f"⚠️ Error Serial: {e}")

    def get_elapsed_time(self):
        elapsed = time.time() - self.start_time
        m, s = divmod(elapsed, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return "{:02d}:{:02d}:{:02d}".format(int(h), int(m), int(s))
        return "{:02d}:{:02d}".format(int(m), int(s))

    def send_to_pico(self):
        # Limpiar barras para proteger protocolo
        clean_name = self.current_window_name.replace('|', '-')
        msg = f"{self.current_app_code}|{self.get_elapsed_time()}|{clean_name}\n"
        
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(msg.encode('utf-8'))
            except Exception:
                pass

    def update_clock(self):
        self.send_to_pico()
        return True 

    def on_window_activated(self, event):
        try:
            accessible = event.source
            if not accessible: return

            # 1. Obtener Título de la Ventana (Lo más fiable en XWayland)
            # Ej: "1204 - YouTube Music" o "Mozilla Firefox"
            window_title = accessible.name if accessible.name else ""
            
            # 2. Obtener Nombre de la App (A veces falla y da mutter-x11-frames)
            app = accessible.getApplication()
            app_name = app.name if app else ""

            # Debug para que veas qué detecta
            print(f"🔎 Detectado: App=[{app_name}] | Titulo=[{window_title}]")

            new_code = "FEDORA" # Default
            
            # --- LÓGICA DE BÚSQUEDA MEJORADA ---
            # Unimos ambas cadenas para buscar keywords en todo a la vez
            full_info = (app_name + " " + window_title).lower()

            # Buscamos coincidencias
            for keyword, code in APPS_MAPPING.items():
                if keyword.lower() in full_info:
                    new_code = code
                    break
            
            # Si detectamos 'mutter' pero no encontramos app, intentamos limpiar el nombre
            if new_code == "FEDORA" and "YouTube Music" in window_title:
                 new_code = "YTM" # Parche específico si falla el loop

            # Gestión de cambio de estado
            if new_code != self.current_app_code:
                self.start_time = time.time()
                self.current_app_code = new_code
                print(f"✅ CAMBIO APLICADO: {new_code}")
            
            self.current_window_name = window_title
            self.send_to_pico()

        except Exception as e:
            print(f"Error evento: {e}")

    def run(self):
        pyatspi.Registry.registerEventListener(self.on_window_activated, "window:activate")
        try:
            pyatspi.Registry.start()
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo...")
            if self.ser: self.ser.close()

if __name__ == "__main__":
    monitor = WaylandMonitor()
    monitor.run()
