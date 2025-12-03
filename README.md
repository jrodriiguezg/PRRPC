# 📟 PRRPC V2 (Pico Real Rich Presence & Control)

**PRRPC V2** es la evolución del monitor de estado físico para Linux. Ahora no solo visualiza tu actividad en **Fedora/Wayland**, sino que se convierte en un **MacroDeck interactivo**.

Esta versión introduce una **Interfaz Web de Control**, permitiéndote enviar reacciones (Emojis) a la pantalla manualmente o volver al modo automático de detección de ventanas con un solo clic.

---

## ✨ Novedades de la V2
* **Modo Híbrido:** Funciona como monitor de aplicaciones (Auto) o como panel de Emojis (Manual).
* **Interfaz Web Local:** Controla la pantalla desde cualquier navegador en tu red local (`localhost:5000`).
* **Arquitectura Multihilo:** El servidor de PC ahora gestiona la detección de ventanas y el servidor web simultáneamente.
* **Optimización Gráfica:** Nuevo sistema de mapeo por diccionarios y assets redimensionados a **100x100px** para mayor fluidez.

---

## ⚙️ Funcionamiento

El sistema utiliza una arquitectura avanzada Cliente-Servidor sobre puerto serie:

1.  **Host (PC - Fedora):**
    * Ejecuta un script híbrido (`server.py`) que combina **Flask** (Web) y **pyatspi** (Monitorización GNOME/Wayland) usando *Threading*.
    * Detecta la ventana activa o recibe comandos de la web y los envía a la RP2040.
2.  **Cliente (Dispositivo - RP2040):**
    * Recibe comandos simples (ej: `FIREFOX`, `FELIZ`, `AUTO`).
    * Busca en su **diccionario interno** (`EMOJI_MAP`) y carga instantáneamente el archivo `.bin` (RGB565) correspondiente desde la memoria flash.

---

## 🛠️ Hardware Requerido

* **Microcontrolador:** Waveshare RP2040-Zero (o Raspberry Pi Pico).
* **Visualización:** Módulo LCD 1.69" IPS (Driver ST7789, Resolución 240x280).
* **Interfaz:** Cable USB-C (Datos y alimentación).

### 🔌 Diagrama de Conexiones (RP2040-Zero)

| Pin Pantalla | Pin RP2040-Zero | Función |
| :--- | :--- | :--- |
| **VCC** | 3V3 | Alimentación (3.3V) |
| **GND** | GND | Tierra Común |
| **SCL** | GP2 | Reloj SPI (SCK) |
| **SDA** | GP3 | Datos SPI (MOSI) |
| **RES** | GP4 | Reset del Display |
| **DC** | GP5 | Datos/Comando |
| **CS** | GP1 | Selección de Chip |
| **BLK** | GP0 | Retroiluminación |

---

## 💾 Instalación

### 1. Configuración del Dispositivo (RP2040)
1.  Instala el firmware de **MicroPython** en la RP2040.
2.  Sube los siguientes archivos a la raíz del dispositivo:
    * `main.py`: Código principal (versión V2 con diccionario `EMOJI_MAP`).
    * `st7789.py`: Controlador de pantalla.
    * `vga1_bold_16x16.py`: Fuente externa para textos legibles.
3.  **Recursos Gráficos:**
    * Convierte tus imágenes PNG (**100x100px**) usando el script `convertir.py`.
    * Sube todos los archivos `.bin` resultantes (`feliz.bin`, `firefox.bin`, etc.) a la raíz de la placa.

### 2. Configuración del Host (PC Linux)
1.  **Instalar Dependencias:**
    Necesitas las librerías de sistema y Python para la comunicación serial, accesibilidad y el servidor web.
    ```bash
    sudo dnf install python3-pyatspi python3-pyserial python3-flask
    # O usando pip (si no usas dnf)
    pip install pyserial flask
    ```

2.  **Configurar GNOME (Wayland):**
    Para permitir que el script detecte las ventanas:
    ```bash
    gsettings set org.gnome.desktop.interface toolkit-accessibility true
    ```

3.  **Configurar Firefox:**
    En `about:config`:
    * `accessibility.force_disabled` -> `0`
    * `accessibility.loaded_via_client_api` -> `true`

---

## 🚀 Uso

1.  Conecta la RP2040 al USB.
2.  Ejecuta el servidor en tu PC:
    ```bash
    python3 server.py
    ```
3.  **Modo Automático:** La pantalla cambiará sola según la app que uses.
4.  **Modo Emoji/Manual:**
    * Abre tu navegador y ve a: `http://localhost:5000`
    * Haz clic en cualquier Emoji: La pantalla del RP2040 mostrará el emoji y bloqueará la detección de ventanas.
    * Haz clic en **"❌ MODO AUTOMÁTICO"** para volver a mostrar las apps.

---

## 🎨 Personalización (Nuevas Apps o Emojis)

El sistema V2 utiliza un sistema de **Diccionarios** que facilita añadir contenido sin tocar lógica compleja.

### Paso 1: Crear la Imagen
1.  Consigue un PNG con fondo transparente.
2.  Redimensiónalo a **100x100 píxeles** (¡Importante! 150px causa problemas de memoria).
3.  Ejecuta el script `convertir.py` en tu PC para obtener el `.bin`.
4.  Sube el `.bin` a la RP2040.

### Paso 2: Registrar en el PC (`server.py`)
Si es una **App**, añádela al diccionario `APPS_MAPPING`. La clave es una palabra que aparezca en el título de la ventana, y el valor es el COMANDO que se enviará.
```python
APPS_MAPPING = {
    "Code":     "VSCODE",
    "Blender":  "BLENDER"  # <--- Nuevo mapeo
}
