import machine
import st7789
import time
import sys
import select
import vga1_bold_16x16 as font

# --- 1. DEFINICIÓN DE COLORES ---
def color565(r, g, b):
    return (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3

NEGRO    = 0x0000
BLANCO   = 0xFFFF
ROJO     = 0xF800
VERDE    = 0x07E0
AZUL     = 0x001F
CIAN     = 0x07FF
AMARILLO = 0xFFE0
GRIS     = color565(50, 50, 50)
COLOR_PIEL = color565(255, 200, 150)
MARRON     = color565(139, 69, 19)
NARANJA    = color565(255, 100, 0)
AZUL_CLARO = color565(100, 100, 255)

# --- 2. CONFIGURACIÓN DE PINES (RP2040-Zero) ---
spi = machine.SPI(0, baudrate=40000000, polarity=1, phase=1, 
                  sck=machine.Pin(2), mosi=machine.Pin(3))

tft = st7789.ST7789(
    spi, 280, 240, 
    reset=machine.Pin(4, machine.Pin.OUT),
    cs=machine.Pin(1, machine.Pin.OUT),
    dc=machine.Pin(5, machine.Pin.OUT),
    backlight=machine.Pin(0, machine.Pin.OUT),
    rotation=1
)

tft.init()
tft.fill(NEGRO) 

# --- 3. CONFIGURACIÓN ICONOS ---
POS_X = 90
POS_Y = 40
W_ICON = 100
H_ICON = 100

# --- MAPEO COMPLETO (EMOJIS + APPS) ---
# Clave: Comando del Server -> Valor: ("archivo.bin", COLOR_FONDO)
EMOJI_MAP = {
    # --- EMOJIS (INTERFAZ WEB) ---
    "FELIZ":    ("feliz.bin", AMARILLO),
    "RISA":     ("risa.bin", AMARILLO),
    "BESO":     ("beso.bin", AMARILLO),
    "CORAZON":  ("corazon.bin", ROJO),
    "ABURRIDO": ("aburrido.bin", AMARILLO),
    "ENFADADO": ("enfadado.bin", ROJO),
    "OJOS":     ("distortsed.bin", AMARILLO),
    "PENSANDO": ("pensando.bin", AMARILLO),
    "SUENO":    ("dormido.bin", AZUL),
    "CAFE":     ("cafe.bin", BLANCO),
    "PC":       ("ordenador.bin", GRIS),
    "DEDO":     ("dedo.bin", COLOR_PIEL),
    "PAYASO":   ("payaso.bin", BLANCO),
    "CACA":     ("caca.bin", MARRON),
    "OK":       ("ok.bin", COLOR_PIEL),
    "FANTASMA": ("fantasma.bin", BLANCO),
    
    # --- APPS DE ESCRITORIO (SERVIDOR PYTHON) ---
    # Mapeamos los comandos del server a los archivos de tu imagen
    "VSCODE":   ("vscode.bin", AZUL),           # Code/Visual Studio
    "FIREFOX":  ("firefox.bin", NARANJA),       # Firefox/Zen
    "YTM":      ("spotify.bin", VERDE),         # Music/Spotify (Usamos icono Spotify)
    "TERM":     ("terminal.bin", NEGRO),        # Terminal/Ptyxis
    "VMWARE":   ("vmware.bin", GRIS),           # VMware
    "GRAVITY":  ("python.bin", AZUL_CLARO),     # Python/Antigravity
    "FEDORA":   ("fedora.bin", AZUL),           # Escritorio
    "DISCORD":  ("discord.bin", AZUL_CLARO),    # Discord (Si tienes el icono)
    
    # --- DEFAULT ---
    "AUTO":     (None, NEGRO)
}

ultimo_comando = ""

def dibujar_icono(nombre, color_bg):
    try:
        with open(nombre, "rb") as f:
            buff = f.read()
            tft.blit_buffer(buff, POS_X, POS_Y, W_ICON, H_ICON)
    except Exception:
        # Si falla (no existe archivo), muestra cuadro de color
        tft.fill_rect(POS_X, POS_Y, W_ICON, H_ICON, color_bg)
        tft.text(font, "NO FILE", POS_X + 15, POS_Y + 40, NEGRO, color_bg)

print("Sistema Listo. Esperando serial...")

while True:
    input_ready = select.select([sys.stdin], [], [], 0)[0]
    
    if sys.stdin in input_ready:
        linea = sys.stdin.readline()
        if not linea: continue
        
        try:
            partes = linea.strip().split('|')
            if len(partes) < 1: continue
            
            comando = partes[0]
            tiempo = ""
            detalle = ""
            if len(partes) > 1: tiempo = partes[1]
            if len(partes) > 2: detalle = partes[2]
            
            if comando != ultimo_comando:
                tft.fill(NEGRO)
                
                if comando in EMOJI_MAP:
                    data = EMOJI_MAP[comando]
                    archivo = data[0]
                    color = data[1]
                    
                    if archivo:
                        dibujar_icono(archivo, color)
                    else:
                        tft.text(font, "MODO AUTO", 70, 100, BLANCO, NEGRO)
                else:
                    # Si llega una app desconocida
                    tft.text(font, comando, 90, 100, BLANCO, NEGRO)
                
                ultimo_comando = comando
            
            # --- Textos ---
            tft.fill_rect(0, 160, 280, 20, NEGRO)
            tft.text(font, detalle[:30], 10, 165, BLANCO, NEGRO)

            tft.fill_rect(0, 200, 280, 20, NEGRO)
            tft.text(font, "T: " + tiempo, 90, 205, CIAN, NEGRO)

        except Exception:
            pass
