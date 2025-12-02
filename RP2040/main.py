import machine
import st7789
import time
import sys
import select

# Configuración RP2040-Zero
spi = machine.SPI(0, baudrate=40000000, polarity=1, phase=1, 
                  sck=machine.Pin(2), mosi=machine.Pin(3))

tft = st7789.ST7789(
    spi, 
    280, 240,  # <--- CAMBIO AQUÍ: Primero el Ancho (280), luego Alto (240)
    reset=machine.Pin(4, machine.Pin.OUT),
    cs=machine.Pin(1, machine.Pin.OUT),
    dc=machine.Pin(5, machine.Pin.OUT),
    backlight=machine.Pin(0, machine.Pin.OUT),
    rotation=1
)

tft.fill(0) # Negro absoluto

# Colores
BLANCO = 0xFFFF
NEGRO = 0x0000
CIAN = 0x07FF

POS_X_ICONO = 70
POS_Y_ICONO = 40
ANCHO_ICONO = 100
ALTO_ICONO = 100

ultimo_comando = ""

def dibujar_icono(nombre):
    try:
        with open(nombre, "rb") as f:
            buff = f.read()
            tft.blit_buffer(buff, POS_X_ICONO, POS_Y_ICONO, ANCHO_ICONO, ALTO_ICONO)
    except:
        # Cuadro rojo si falla
        tft.fill(0xF800)

while True:
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        linea = sys.stdin.readline()
        if not linea: continue
        
        try:
            partes = linea.strip().split('|')
            if len(partes) < 2: continue
            
            comando = partes[0]
            tiempo = partes[1]
            detalle = partes[2] if len(partes) > 2 else ""
            
            if comando != ultimo_comando:
                tft.fill(NEGRO) # Limpiar pantalla
                
                archivo = "fedora.bin"
                if comando == "VSCODE": archivo = "vscode.bin"
                elif comando == "GRAVITY": archivo = "python.bin"
                elif comando == "YTM": archivo = "spotify.bin"
                elif comando == "FIREFOX": archivo = "firefox.bin"
                elif comando == "VMWARE": archivo = "vmware.bin"
                elif comando == "TERM": archivo = "terminal.bin"
                elif comando == "FEDORA": archivo = "fedora.bin"
                
                dibujar_icono(archivo)
                ultimo_comando = comando
            
            # --- TEXTOS (Usando la fuente interna fiable) ---
            # Como es 8x8, es pequeña. La duplicamos dibujando 2 veces o la dejamos así.
            # Limpiamos zona texto (rectangulo negro abajo)
            # tft.fill_rect no está en este driver simplificado, usamos blit negro
            
            # Detalle
            tft.text(None, detalle[:28], 10, 160, BLANCO, NEGRO)
            
            # Tiempo
            tft.text(None, "TIEMPO: " + tiempo, 60, 200, CIAN, NEGRO)

        except Exception as e:
            pass