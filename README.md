# 📟 PRRPC (Pico Real Rich Presence)

PRRPC es un monitor de estado físico externo diseñado para entornos Linux modernos (Fedora/Wayland). Muestra información contextual de la aplicación activa en una pantalla secundaria conectada por USB, mejorando la gestión del tiempo y la visibilidad de tareas.

![Estado](https://img.shields.io/badge/Estado-Estable-blue)
![Hardware](https://img.shields.io/badge/Hardware-RP2040--Zero-green)
![OS](https://img.shields.io/badge/OS-Fedora%20Wayland-blue)


## ⚙️ Funcionamiento

El sistema opera mediante una arquitectura Cliente-Servidor sobre puerto serie:

1.  **Host (PC - Fedora):** Un servicio en Python (`server.py`) monitoriza los eventos de foco del entorno de escritorio GNOME mediante `pyatspi`. Esto permite una detección precisa de la ventana activa en Wayland, superando las restricciones de seguridad habituales.
2.  **Cliente (Dispositivo - RP2040):** Un microcontrolador recibe los datos procesados y renderiza la interfaz gráfica. Utiliza iconos en formato raw (RGB565) para maximizar la velocidad de dibujo y minimizar el uso de memoria.

## 🛠️ Hardware Requerido

* **Microcontrolador:** Waveshare RP2040-Zero (o compatible Raspberry Pi Pico).
* **Visualización:** Módulo LCD 1.69" IPS (Controlador ST7789, Resolución 240x280).
* **Interfaz:** Conexión USB-C (Datos y alimentación).

### 🔌 Diagrama de Conexiones (RP2040-Zero)

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

## 💾 Instalación

### 1. Configuración del Dispositivo (Firmware)

1.  Instala el firmware de **MicroPython** en la RP2040.
2.  Sube los siguientes archivos a la raíz del dispositivo:
    * `main.py`: Código fuente del cliente.
    * `st7789.py`: Controlador de pantalla optimizado.
3.  **Carga de Recursos Gráficos:**
    * Convierte tus imágenes PNG (150x150px) usando el script `convertir.py`.
    * Sube los archivos `.bin` resultantes (`firefox.bin`, `vscode.bin`, etc.) a la memoria de la placa.

### 2. Configuración del Host (Fedora Linux)

1.  **Dependencias:**
    Instala las librerías necesarias para la comunicación serie y accesibilidad:
    ```bash
    sudo dnf install python3-pyatspi python3-pyserial
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

## 🚀 Uso

1.  Conecta el dispositivo PRRPC al puerto USB.
2.  Ejecuta el monitor en el PC:
    ```bash
    python3 server.py
    ```
3.  El dispositivo mostrará el logo de Fedora por defecto y cambiará automáticamente al detectar aplicaciones configuradas.

## 📁 Estructura del Repositorio

* **`RP2040/`**: Carpeta principal del firmware. Contiene los scripts que deben subirse al microcontrolador (`main.py`, `st7789.py`) y las fuentes.
* **`host/`**: Contiene el script `server.py` que se ejecuta en el ordenador (Fedora).
* **`bin/`**: Imágenes en formato binario 
* **`convert2.py`**: Herramienta esencial para procesar las imágenes antes de subirlas.

## 📝 Notas Técnicas

* **Pantalla:** Se utiliza una resolución lógica de 280x240 (orientación horizontal).
* **Rendimiento:** El script del host funciona por eventos (no por sondeo), por lo que el consumo de CPU es despreciable.
* **Compatibilidad:** Diseñado para Wayland, pero compatible con X11 si se usa el backend AT-SPI.
---

## 📸 Galería y Demostración

El dispositivo PRRPC se integra perfectamente en el flujo de trabajo del escritorio. A continuación se muestran ejemplos reales del dispositivo en funcionamiento, reaccionando a las aplicaciones abiertas en el monitor principal.

### Entorno de Desarrollo (VS Code)
El editor Visual Studio Code abierto en el monitor de fondo. En primer plano, el PRRPC muestra el icono correspondiente y el tiempo de sesión.

![code](https://github.com/user-attachments/assets/acb33cca-38ba-4fd6-97c8-8df39ad331aa)

### Navegación Web (Firefox)
Al cambiar el foco al navegador, el dispositivo actualiza instantáneamente su estado para reflejar la actividad de navegación.

![firefox](https://github.com/user-attachments/assets/35271944-9dcd-47d4-8dce-dedabe273c94)

### Terminal del Sistema (Ptyxis)
Vista detallada del dispositivo mostrando el estado de la terminal de Fedora.

![terminal](https://github.com/user-attachments/assets/0c21cdd2-856f-4a4f-9339-7f9949d71b95)

## Reproduccion De Musica (youtube-music)
Se muestra el icono de Youtube music, asi como lo que se esta reproduciendo

![music](https://github.com/user-attachments/assets/8b5ba6d3-3349-43c8-a1fb-fc6c89d868b9)


---

## 🎨 Personalización y Nuevas Apps

> ⚠️ **Aviso Importante:**
> Por defecto, PRRPC solo reconoce y muestra iconos para las aplicaciones definidas en el código original (Firefox, VS Code, Terminal, Spotify, VMware, etc.).
>
> Si abres una aplicación que no está en la lista, el sistema mostrará el logo de **Fedora** (estado por defecto). Para añadir soporte a nuevas aplicaciones, debes seguir los pasos a continuación.

### Guía para agregar una nueva App

El proceso consta de 3 pasos: Crear el icono, configurar el PC y configurar la RP2040.

#### 1. Preparar el Icono
1.  Consigue el logo de la app en formato PNG (preferiblemente con fondo transparente).
2.  Añade el nombre del archivo a la lista en el script `convertir.py` y ejecútalo en tu PC.
3.  Sube el archivo `.bin` generado (ej: `obsidian.bin`) a la memoria de la RP2040.

#### 2. Actualizar el Host (`monitor_pc.py`)
Abre el script en tu PC y busca el diccionario `APPS_MAPPING`. Añade una nueva línea con la palabra clave que identifica la app y un **CÓDIGO INTERNO** (en mayúsculas) que tú inventes.

```python
APPS_MAPPING = {
    "Code":       "VSCODE",
    "Firefox":    "FIREFOX",
    # ... otras apps ...
    "Obsidian":   "NOTAS"  # <--- NUEVA LÍNEA: Si detecta "Obsidian", envía el código "NOTAS"
}
```
#### 3. Actualizar el Dispositivo (main.py)

Abre el archivo main.py en la RP2040 (usando Thonny) y busca la sección donde se asignan los archivos. Añade tu nuevo código:
```python
# ... dentro del bucle principal ...
if comando == "VSCODE": archivo = "vscode.bin"
elif comando == "FIREFOX": archivo = "firefox.bin"
# ... otras apps ...
elif comando == "NOTAS": archivo = "obsidian.bin" # <--- NUEVA LÍNEA: Asigna el código al archivo
```
Guarda los cambios, reinicia el script del PC y ¡listo! Tu nueva app ahora tendrá su propio icono personalizado.

## 🖼️ Gestión de Imágenes: Uso de `convert2.py`

La RP2040, aunque potente, no está optimizada para decodificar archivos `.png` o `.jpg` en tiempo real mientras gestiona la pantalla, ya que esto consume demasiada memoria RAM y CPU.

Para solucionar esto, utilizamos el script **`convert2.py`**.

### ¿Qué hace este script?
Este script de Python toma tus iconos estándar (PNG con transparencia) y los "pre-renderiza" a un formato crudo llamado **Raw RGB565**. Básicamente, convierte la imagen en una matriz de bytes exacta a la que la pantalla espera recibir, permitiendo que la RP2040 simplemente "copie y pegue" los datos a la pantalla instantáneamente sin procesarlos.

### Pasos para convertir nuevas imágenes:

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
