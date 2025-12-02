# Guarda esto como convertir.py en tu PC y ejecútalo: python3 convertir.py
from PIL import Image
import struct
import os

archivos = [
    "vscode.png", "firefox.png", "spotify.png", "terminal.png", 
    "vmware.png", "fedora.png", "python.png"
]

def color565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

for nombre in archivos:
    if not os.path.exists(nombre):
        print(f"Falta: {nombre}")
        continue
        
    # Abrir y redimensionar a 100x100
    img = Image.open(nombre).convert("RGBA")
    img = img.resize((100, 100))
    background = Image.new("RGB", img.size, (0, 0, 0)) # Fondo NEGRO forzado
    background.paste(img, mask=img.split()[3]) # Pegar icono sobre negro usando transparencia
    
    nombre_bin = nombre.split('.')[0] + ".bin"
    print(f"Creando {nombre_bin} con fondo NEGRO...")
    
    with open(nombre_bin, "wb") as f:
        pixels = list(background.getdata())
        for r, g, b in pixels:
            c = color565(r, g, b)
            # Big Endian para ST7789
            f.write(struct.pack(">H", c))
