# 📟 PRRPC (Pico Real Rich Presence)

PRRPC is an external physical status monitor designed for modern Linux environments (Fedora/Wayland). It displays contextual information about the active application on a secondary USB-connected screen, improving time management and task visibility.

> The latest version of this project, with support for expressing states via emojis, can be found at https://github.com/jrodriiguezg/PRRPC/tree/v2

![Status](https://img.shields.io/badge/Estado-Estable-blue)
![Hardware](https://img.shields.io/badge/Hardware-RP2040--Zero-green)
![OS](https://img.shields.io/badge/OS-Fedora%20Wayland-blue)

## 🌐 Language / Idioma
- [English Version](#english-version)
- [Versión en Español](#versión-en-español)

---

<a id="english-version"></a>
## 🇬🇧 English Version

### ⚙️ How it Works

The system operates via a Client-Server architecture over a serial port:

1.  **Host (PC - Linux):** A Python service (`server.py`) monitors GNOME desktop focus events using `pyatspi`. This allows precise detection of the active window in Wayland, overcoming standard security restrictions.
2.  **Client (Device - RP2040):** A microcontroller receives the processed data and renders the graphical interface. It uses raw icons (RGB565) to maximize drawing speed and minimize memory usage.

### 🛠️ Hardware Required

* **Microcontroller:** Waveshare RP2040-Zero (or compatible Raspberry Pi Pico).
* **Display:** 1.69" IPS LCD Module (ST7789 Controller, 240x280 Resolution).
* **Interface:** USB-C Connection (Data and Power).

#### 🔌 Connection Diagram (RP2040-Zero)

Connection via SPI0 interface on the side pins:

| Display Pin | RP2040-Zero Pin | Function |
| :--- | :--- | :--- |
| **VCC** | 3V3 | Power (3.3V) |
| **GND** | GND | Common Ground |
| **SCL** | GP2 | SPI Clock (SCK) |
| **SDA** | GP3 | SPI Data (MOSI) |
| **RES** | GP4 | Display Reset |
| **DC** | GP5 | Data/Command |
| **CS** | GP1 | Chip Select |
| **BLK** | GP0 | Backlight |

---

### 💾 Installation

#### 1. Device Configuration (Firmware)

1.  Install **MicroPython** firmware on the RP2040.
2.  Upload the following files to the device root (Recommended using Thonny):
    * `main.py`: Client source code.
    * `st7789.py`: Optimized display driver.
3.  **Graphic Resources Loading:**
    * Convert your PNG images (150x150px) using the `convertir.py` script.
    * Upload the resulting `.bin` files (`firefox.bin`, `vscode.bin`, etc.) to the board's memory.

#### 2. Host Configuration (Fedora Linux)

1.  **Dependencies:**
    Install necessary libraries for serial communication and accessibility:
        **Fedora**
    ```bash
    sudo dnf install python3-pyatspi python3-pyserial
    ```
        **Debian/Ubuntu**
    ```bash
    sudo apt install python3-pyatspi python3-pyserial
    ```

2.  **Enable GNOME Accessibility:**
    Required for the script to detect windows:
    ```bash
    gsettings set org.gnome.desktop.interface toolkit-accessibility true
    ```

3.  **Firefox Configuration (Important):**
    To make Firefox detectable in Wayland:
    * In `about:config`, set `accessibility.force_disabled` to `0`.
    * Set `accessibility.loaded_via_client_api` to `true`.

---

### 🚀 Usage

1.  Connect the PRRPC device to the USB port.
2.  Run the monitor on the PC:
    ```bash
    python3 server.py
    ```
3.  The device will show the Fedora logo by default and automatically switch when configured applications are detected.

### 📁 Repository Structure

* **`RP2040/`**: Main firmware folder. Contains scripts to be uploaded to the microcontroller (`main.py`, `st7789.py`) and fonts.
* **`host/`**: Contains the `server.py` script that runs on the computer (Fedora).
* **`bin/`**: Binary format images.
* **`convert2.py`**: Essential tool for processing images before uploading.

### 📝 Technical Notes

* **Display:** Uses a logical resolution of 280x240 (landscape orientation).
* **Performance:** The host script works by events (not polling), so CPU consumption is negligible.
* **Compatibility:** Designed for Wayland, but compatible with X11 if the AT-SPI backend is used.

---

### 📸 Gallery and Demo

The PRRPC device integrates perfectly into the desktop workflow. Below are real examples of the device in operation, reacting to open applications on the main monitor.

#### Development Environment (VS Code)
Visual Studio Code open on the background monitor. In the foreground, the PRRPC shows the corresponding icon and session time.

![code](https://github.com/user-attachments/assets/acb33cca-38ba-4fd6-97c8-8df39ad331aa)

#### Web Browsing (Firefox)
Switching focus to the browser instantly updates the device status to reflect browsing activity.

![firefox](https://github.com/user-attachments/assets/35271944-9dcd-47d4-8dce-dedabe273c94)

#### System Terminal (Ptyxis)
Detailed view of the device showing the Fedora terminal status.

![terminal](https://github.com/user-attachments/assets/0c21cdd2-856f-4a4f-9339-7f9949d71b95)

#### Music Playback (youtube-music)
Shows the Youtube Music icon, as well as what is playing.

![music](https://github.com/user-attachments/assets/8b5ba6d3-3349-43c8-a1fb-fc6c89d868b9)


---

### 🎨 Customization and New Apps

> ⚠️ **Important Notice:**
> By default, PRRPC only recognizes and displays icons for applications defined in the original code (Firefox, VS Code, Terminal, Spotify, VMware, etc.).
>
> If you open an application not on the list, the system will show the **Fedora** logo (default state). To add support for new applications, follow the steps below.

#### Guide to Add a New App

The process consists of 3 steps: Create the icon, configure the PC, and configure the RP2040.

##### 1. Prepare the Icon
1.  Get the app logo in PNG format (preferably with transparent background).
2.  Add the filename to the list in the `convertir.py` script and run it on your PC.
3.  Upload the generated `.bin` file (e.g., `obsidian.bin`) to the RP2040 memory.

##### 2. Update the Host (`monitor_pc.py`)
Open the script on your PC and look for the `APPS_MAPPING` dictionary. Add a new line with the keyword identifying the app and an **INTERNAL CODE** (in uppercase) that you invent.

```python
APPS_MAPPING = {
    "Code":       "VSCODE",
    "Firefox":    "FIREFOX",
    # ... other apps ...
    "Obsidian":   "NOTAS"  # <--- NEW LINE: If "Obsidian" is detected, send code "NOTAS"
}
```

##### 3. Update the Device (main.py)

Open the `main.py` file on the RP2040 (using Thonny) and look for the section where files are assigned. Add your new code:

```python
# ... inside the main loop ...
if comando == "VSCODE": archivo = "vscode.bin"
elif comando == "FIREFOX": archivo = "firefox.bin"
# ... other apps ...
elif comando == "NOTAS": archivo = "obsidian.bin" # <--- NEW LINE: Assign code to file
```
Save changes, restart the PC script, and you're done! Your new app will now have its own custom icon.

### 🖼️ Image Management: Using `convert2.py`

The RP2040, while powerful, is not optimized to decode `.png` or `.jpg` files in real-time while managing the display, as this consumes too much RAM and CPU.

To solve this, we use the **`convert2.py`** script.

#### What does this script do?
This Python script takes your standard icons (PNG with transparency) and "pre-renders" them to a raw format called **Raw RGB565**. Basically, it converts the image into an exact byte matrix that the screen expects to receive, allowing the RP2040 to simply "copy and paste" the data to the screen instantly without processing.

#### Steps to convert new images:

1.  **Prepare your images:**
    * Must be **PNG** format.
    * Recommended size: **150x150 pixels**.
    * Transparent background (the script will automatically add a black background to blend with the interface).

2.  **Run the converter:**
    Ensure images are in the same folder as the script and run:
    ```bash
    python3 convert2.py
    ```

3.  **Result:**
    The script will generate files with **`.bin`** extension (e.g., `firefox.bin`).

4.  **Upload to Device:**
    Upload these `.bin` files directly to the root of the `RP2040+` folder (or board root if using Thonny) along with the `main.py` code.

> **Technical Note:** The RGB565 format uses 2 bytes per pixel (5 bits red, 6 green, 5 blue). A 150x150 icon...

---
---

<a id="versión-en-español"></a>
## 🇪🇸 Versión en Español

### ⚙️ Funcionamiento

El sistema opera mediante una arquitectura Cliente-Servidor sobre puerto serie:

1.  **Host (PC - Fedora):** Un servicio en Python (`server.py`) monitoriza los eventos de foco del entorno de escritorio GNOME mediante `pyatspi`. Esto permite una detección precisa de la ventana activa en Wayland, superando las restricciones de seguridad habituales.
2.  **Cliente (Dispositivo - RP2040):** Un microcontrolador recibe los datos procesados y renderiza la interfaz gráfica. Utiliza iconos en formato raw (RGB565) para maximizar la velocidad de dibujo y minimizar el uso de memoria.

### 🛠️ Hardware Requerido

* **Microcontrolador:** Waveshare RP2040-Zero (o compatible Raspberry Pi Pico).
* **Visualización:** Módulo LCD 1.69" IPS (Controlador ST7789, Resolución 240x280).
* **Interfaz:** Conexión USB-C (Datos y alimentación).

#### 🔌 Diagrama de Conexiones (RP2040-Zero)

Conexión mediante interfaz SPI0 en los pines laterales:

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

### 💾 Instalación

#### 1. Configuración del Dispositivo (Firmware)

1.  Instala el firmware de **MicroPython** en la RP2040.
2.  Sube los siguientes archivos a la raíz del dispositivo (Podeis usar Thonny):
    * `main.py`: Código fuente del cliente.
    * `st7789.py`: Controlador de pantalla optimizado.
3.  **Carga de Recursos Gráficos:**
    * Convierte tus imágenes PNG (150x150px) usando el script `convertir.py`.
    * Sube los archivos `.bin` resultantes (`firefox.bin`, `vscode.bin`, etc.) a la memoria de la placa.

#### 2. Configuración del Host 

1.  **Dependencias:**
    Instala las librerías necesarias para la comunicación serie y accesibilidad:
        **Fedora**
    ```bash
    sudo dnf install python3-pyatspi python3-pyserial
    ```
        **Debian/Ubuntu**
    ```bash
    sudo apt install python3-pyatspi python3-pyserial
    ```

2.  **Habilitar Accesibilidad en GNOME:**
    Necesario para que el script detecte las ventanas:
    ```bash
    gsettings set org.gnome.desktop.interface toolkit-accessibility true
    ```

3.  **Configuración de Firefox (Importante):**
    Para que Firefox sea detectable en Wayland:
    * En `about:config`, establece `accessibility.force_disabled` a `0`.
    * Establece `accessibility.loaded_via_client_api` a `true`.

---

### 🚀 Uso

1.  Conecta el dispositivo PRRPC al puerto USB.
2.  Ejecuta el monitor en el PC:
    ```bash
    python3 server.py
    ```
3.  El dispositivo mostrará el logo de Fedora por defecto y cambiará automáticamente al detectar aplicaciones configuradas.

### 📁 Estructura del Repositorio

* **`RP2040/`**: Carpeta principal del firmware. Contiene los scripts que deben subirse al microcontrolador (`main.py`, `st7789.py`) y las fuentes.
* **`host/`**: Contiene el script `server.py` que se ejecuta en el ordenador (Fedora).
* **`bin/`**: Imágenes en formato binario 
* **`convert2.py`**: Herramienta esencial para procesar las imágenes antes de subirlas.

### 📝 Notas Técnicas

* **Pantalla:** Se utiliza una resolución lógica de 280x240 (orientación horizontal).
* **Rendimiento:** El script del host funciona por eventos (no por sondeo), por lo que el consumo de CPU es despreciable.
* **Compatibilidad:** Diseñado para Wayland, pero compatible con X11 si se usa el backend AT-SPI.
---

### 📸 Galería y Demostración

El dispositivo PRRPC se integra perfectamente en el flujo de trabajo del escritorio. A continuación se muestran ejemplos reales del dispositivo en funcionamiento, reaccionando a las aplicaciones abiertas en el monitor principal.

#### Entorno de Desarrollo (VS Code)
El editor Visual Studio Code abierto en el monitor de fondo. En primer plano, el PRRPC muestra el icono correspondiente y el tiempo de sesión.

![code](https://github.com/user-attachments/assets/acb33cca-38ba-4fd6-97c8-8df39ad331aa)

#### Navegación Web (Firefox)
Al cambiar el foco al navegador, el dispositivo actualiza instantáneamente su estado para reflejar la actividad de navegación.

![firefox](https://github.com/user-attachments/assets/35271944-9dcd-47d4-8dce-dedabe273c94)

#### Terminal del Sistema (Ptyxis)
Vista detallada del dispositivo mostrando el estado de la terminal de Fedora.

![terminal](https://github.com/user-attachments/assets/0c21cdd2-856f-4a4f-9339-7f9949d71b95)

#### Reproduccion De Musica (youtube-music)
Se muestra el icono de Youtube music, asi como lo que se esta reproduciendo

![music](https://github.com/user-attachments/assets/8b5ba6d3-3349-43c8-a1fb-fc6c89d868b9)


---

### 🎨 Personalización y Nuevas Apps

> ⚠️ **Aviso Importante:**
> Por defecto, PRRPC solo reconoce y muestra iconos para las aplicaciones definidas en el código original (Firefox, VS Code, Terminal, Spotify, VMware, etc.).
>
> Si abres una aplicación que no está en la lista, el sistema mostrará el logo de **Fedora** (estado por defecto). Para añadir soporte a nuevas aplicaciones, debes seguir los pasos a continuación.

#### Guía para agregar una nueva App

El proceso consta de 3 pasos: Crear el icono, configurar el PC y configurar la RP2040.

##### 1. Preparar el Icono
1.  Consigue el logo de la app en formato PNG (preferiblemente con fondo transparente).
2.  Añade el nombre del archivo a la lista en el script `convertir.py` y ejecútalo en tu PC.
3.  Sube el archivo `.bin` generado (ej: `obsidian.bin`) a la memoria de la RP2040.

##### 2. Actualizar el Host (`monitor_pc.py`)
Abre el script en tu PC y busca el diccionario `APPS_MAPPING`. Añade una nueva línea con la palabra clave que identifica la app y un **CÓDIGO INTERNO** (en mayúsculas) que tú inventes.

```python
APPS_MAPPING = {
    "Code":       "VSCODE",
    "Firefox":    "FIREFOX",
    # ... otras apps ...
    "Obsidian":   "NOTAS"  # <--- NUEVA LÍNEA: Si detecta "Obsidian", envía el código "NOTAS"
}
```
##### 3. Actualizar el Dispositivo (main.py)

Abre el archivo main.py en la RP2040 (usando Thonny) y busca la sección donde se asignan los archivos. Añade tu nuevo código:
```python
# ... dentro del bucle principal ...
if comando == "VSCODE": archivo = "vscode.bin"
elif comando == "FIREFOX": archivo = "firefox.bin"
# ... otras apps ...
elif comando == "NOTAS": archivo = "obsidian.bin" # <--- NUEVA LÍNEA: Asigna el código al archivo
```
Guarda los cambios, reinicia el script del PC y ¡listo! Tu nueva app ahora tendrá su propio icono personalizado.

### 🖼️ Gestión de Imágenes: Uso de `convert2.py`

La RP2040, aunque potente, no está optimizada para decodificar archivos `.png` o `.jpg` en tiempo real mientras gestiona la pantalla, ya que esto consume demasiada memoria RAM y CPU.

Para solucionar esto, utilizamos el script **`convert2.py`**.

#### ¿Qué hace este script?
Este script de Python toma tus iconos estándar (PNG con transparencia) y los "pre-renderiza" a un formato crudo llamado **Raw RGB565**. Básicamente, convierte la imagen en una matriz de bytes exacta a la que la pantalla espera recibir, permitiendo que la RP2040 simplemente "copie y pegue" los datos a la pantalla instantáneamente sin procesarlos.

#### Pasos para convertir nuevas imágenes:

1.  **Prepara tus imágenes:**
    * Deben ser formato **PNG**.
    * Tamaño recomendado: **150x150 píxeles**.
    * Fondo transparente (el script añadirá automáticamente el fondo negro para que se fusione con la interfaz).

2.  **Ejecuta el conversor:**
    Asegúrate de tener las imágenes en la misma carpeta que el script y ejecuta:
    ```bash
    python3 convert2.py
    ```

3.  **Resultado:**
    El script generará archivos con extensión **`.bin`** (ej: `firefox.bin`).

4.  **Subida al Dispositivo:**
    Sube estos archivos `.bin` directamente a la raíz de la carpeta `RP2040+` (o la raíz de la placa si usas Thonny) junto con el código `main.py`.

> **Nota Técnica:** El formato RGB565 utiliza 2 bytes por píxel (5 bits rojo, 6 verde, 5 azul). Un icono de 150x15
