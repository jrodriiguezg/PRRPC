import time
from micropython import const
import ustruct as struct
import framebuf

# Comandos ST7789
ST7789_SWRESET = const(0x01)
ST7789_SLPIN   = const(0x10)
ST7789_SLPOUT  = const(0x11)
ST7789_NORON   = const(0x13)
ST7789_INVOFF  = const(0x20)
ST7789_INVON   = const(0x21)
ST7789_DISPOFF = const(0x28)
ST7789_DISPON  = const(0x29)
ST7789_CASET   = const(0x2A)
ST7789_RASET   = const(0x2B)
ST7789_RAMWR   = const(0x2C)
ST7789_MADCTL  = const(0x36)
ST7789_COLMOD  = const(0x3A)

class ST7789:
    def __init__(self, spi, width, height, reset, dc, cs=None, backlight=None, rotation=1):
        self.width = width
        self.height = height
        self.spi = spi
        self.reset = reset
        self.dc = dc
        self.cs = cs
        self.backlight = backlight
        self.rotation = rotation
        
        if self.cs: self.cs.init(self.cs.OUT, value=1)
        if self.dc: self.dc.init(self.dc.OUT, value=0)
        if self.reset: self.reset.init(self.reset.OUT, value=1)
        if self.backlight: self.backlight.init(self.backlight.OUT, value=1)
        self.init()

    def init(self):
        self.reset.value(0)
        time.sleep_ms(50)
        self.reset.value(1)
        time.sleep_ms(50)
        
        self._write(ST7789_SWRESET)
        time.sleep_ms(150)
        self._write(ST7789_SLPOUT)
        time.sleep_ms(10)
        self._write(ST7789_COLMOD, b'\x05')
        
        # Configuración de rotación
        madctl = 0x00
        if self.rotation == 0: madctl = 0x00
        elif self.rotation == 1: madctl = 0x60
        elif self.rotation == 2: madctl = 0xC0
        elif self.rotation == 3: madctl = 0xA0
        
        self._write(ST7789_MADCTL, bytes([madctl]))
        self._write(ST7789_INVON, None)
        self._write(ST7789_NORON, None)
        self._write(ST7789_DISPON, None)

    def _write(self, command, data=None):
        if self.cs: self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytearray([command]))
        if data:
            self.dc.value(1)
            self.spi.write(data)
        if self.cs: self.cs.value(1)

    def _set_window(self, x0, y0, x1, y1):
        # Ajustes de offset para tu pantalla 240x280
        off_x = 0
        off_y = 20 
        
        if self.rotation == 1 or self.rotation == 3: 
             off_x = 20; off_y = 0 
        
        x0 += off_x; x1 += off_x
        y0 += off_y; y1 += off_y
        
        self._write(ST7789_CASET, struct.pack(">HH", x0, x1))
        self._write(ST7789_RASET, struct.pack(">HH", y0, y1))
        self._write(ST7789_RAMWR)

    def fill(self, color):
        self._set_window(0, 0, self.width-1, self.height-1)
        
        # --- AQUÍ ESTABA EL ERROR ---
        # Usamos 'bytes' (inmutable) en lugar de 'bytearray'
        # Esto soluciona el TypeError: unsupported types for __mul__
        hi = color >> 8
        lo = color & 0xFF
        chunk = bytes([hi, lo]) * 1024
        # ----------------------------

        pixels = self.width * self.height
        
        self.dc.value(1)
        if self.cs: self.cs.value(0)
        
        while pixels > 0:
            write_len = min(pixels, 1024)
            self.spi.write(chunk[:write_len*2])
            pixels -= write_len
            
        if self.cs: self.cs.value(1)

    def blit_buffer(self, buffer, x, y, w, h):
        self._set_window(x, y, x+w-1, y+h-1)
        self.dc.value(1)
        if self.cs: self.cs.value(0)
        self.spi.write(buffer)
        if self.cs: self.cs.value(1)

    def text(self, font, text, x, y, color, background):
        # Ignoramos 'font' externo y usamos el interno de 8x8
        for char in text:
            self.draw_char_8x8(char, x, y, color, background)
            x += 8

    def draw_char_8x8(self, char, x, y, color, background):
        buffer = bytearray(8 * 8 * 2)
        fb = framebuf.FrameBuffer(buffer, 8, 8, framebuf.RGB565)
        fb.fill(background)
        fb.text(char, 0, 0, color)
        self.blit_buffer(buffer, x, y, 8, 8)