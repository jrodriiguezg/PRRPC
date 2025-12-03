# Guardar como convertir.py en la carpeta de las imágenes
# Requiere: pip install pillow
import os
from PIL import Image
import struct

def color565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

archivos = [
    "feliz.png", "risa.png", "beso.png", "corazon.png",
    "aburrido.png", "enfadado.png", "distortsed.png", "pensando.png",
    "dormido.png", "cafe.png", "ordenador.png", "dedo.png",
    "payaso.png", "caca.png", "ok.png", "fantasma.png","fedora.png","firefox.png","python.png","spotify.png",
    "terminal.png","vmware.png","vscode.png"
]

print("Convirtiendo imágenes a 100x100 RGB565...")

for nombre in archivos:
    if not os.path.exists(nombre):
        print(f"⚠️ Falta: {nombre}")
        continue
        
    img = Image.open(nombre).convert("RGB")
    img = img.resize((100, 100)) # Forzamos el tamaño
    
    nombre_bin = nombre.replace(".png", ".bin")
    with open(nombre_bin, "wb") as f:
        pixels = list(img.getdata())
        for r, g, b in pixels:
            c = color565(r, g, b)
            # Big Endian para ST7789 por defecto en MicroPython
            f.write(struct.pack(">H", c))
            
    print(f"✅ Generado: {nombre_bin}")

print("¡Listo! Sube los archivos .bin a tu RP2040.")
