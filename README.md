# Solicitudes de Ayuda — Cliente

> Sistema de alertas de emergencia en red local — cliente de escritorio

[![Licencia: AGPL v3](https://img.shields.io/badge/Licencia-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-yellow.svg)](https://www.python.org/)
[![Plataformas](https://img.shields.io/badge/Plataformas-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

Solicitudes de Ayuda es un sistema de alerta inmediata diseñado originalmente para personal sanitario y administrativo de centros de salud y hospitales, aunque es igualmente aplicable a cualquier organización o sector donde sea necesario comunicar una emergencia de forma rápida entre equipos de una misma red local: centros educativos, residencias, instalaciones industriales, servicios de seguridad, etc. Cuando alguien pulsa el atajo de teclado configurado, todos los equipos del mismo grupo reciben en décimas de segundo una notificación con la ubicación exacta de quien solicitó ayuda. Funciona en la red local sin necesidad de internet ni de servidor (modo P2P).

Este repositorio contiene el **cliente de escritorio** multiplataforma. El servidor está en un repositorio separado.

---

## Características

- **Alerta instantánea** con un atajo de teclado global (por defecto `Ctrl+F12`)
- **Funciona sin servidor** — comunicación P2P por UDP broadcast entre clientes
- **Con servidor** — registro histórico, informes y configuración centralizada
- **Modo simulacro** (`Ctrl+Mayúsculas+F12`) para verificar que el sistema funciona sin generar alertas reales
- **Icono en la bandeja del sistema** con indicador de estado en color (verde / amarillo / rojo / gris)
- **Configuración de ubicación en cascada** — selects dependientes Centro → Edificio → Planta → Sala con posibilidad de añadir nuevos elementos desde el propio cliente
- **URL de servidor manual** — para redes multi-segmento donde el servidor está en un CPD o segmento diferente al que el broadcast UDP no llega
- **Atajo configurable desde el servidor** — se distribuye automáticamente a todos los clientes al arrancar
- **Autoarranque con el sistema operativo** sin intervención del usuario (ruta de instalación fija en Windows y Linux)
- **Auto-actualización** en Linux (AppImage) y Windows (.exe) — descarga e instala nuevas versiones en segundo plano
- **Soporte Wayland** en Linux — registra atajos en GNOME y KDE automáticamente
- **Notificación sonora** al recibir alertas
- **Modo portátil** — los equipos portátiles piden confirmar la ubicación en cada inicio de sesión; los equipos fijos la solicitan solo una vez al mes tras la configuración inicial. Configurable desde el cliente y desde el panel web del servidor

---

## Compatibilidad

| Plataforma    | Versión mínima            | Distribución          | Estado     |
|---------------|---------------------------|-----------------------|------------|
| Windows       | Windows 10 (1903)         | `.exe` portátil       | ✅ Soportado |
| Linux (X11)   | Ubuntu 22.04 / Debian 11  | AppImage x86_64       | ✅ Soportado |
| Linux (Wayland GNOME) | Ubuntu 22.04+     | AppImage x86_64       | ✅ Soportado |
| Linux (Wayland KDE)   | Kubuntu 22.04+    | AppImage x86_64       | ✅ Soportado |
| macOS         | macOS 11 Big Sur          | `.app` / `.dmg`       | ✅ Soportado |
| macOS Apple Silicon   | macOS 11+         | `.dmg` nativo arm64   | ✅ Soportado |

---

## Primer uso

1. Descargue el paquete para su plataforma (`.exe`, `.AppImage` o `.dmg`).
2. Ejecute la aplicación. Aparecerá la **ventana de información** con el atajo de teclado activo.
3. A continuación, la **ventana de configuración de ubicación**:
   - **Servidor** — si el servidor está en el mismo segmento de red, se detecta automáticamente (campo vacío). Si está en un segmento distinto (CPD, VLAN separada), introduzca la URL completa, p. ej. `http://192.168.10.50:8080`, y pulse **Conectar**.
   - Seleccione Centro → Edificio → Planta → Sala (selects en cascada).
   - Si algún elemento no está en la lista, pulse **[+]** para añadirlo al servidor.
   - Los cuatro campos de ubicación son obligatorios para poder enviar alertas.
   - **Equipo portátil** — active esta casilla si el equipo se desplaza entre ubicaciones. La ventana de ubicación aparecerá en cada inicio de sesión. En equipos fijos solo vuelve a aparecer una vez al mes.
4. Pulse **Confirmar ubicación**. El icono queda en la bandeja del sistema.
5. A partir de ese momento, pulse `Ctrl+F12` para enviar una alerta.

### Colores del icono

| Color    | Significado                                              |
|----------|----------------------------------------------------------|
| 🟢 Verde  | Ubicación configurada y servidor conectado               |
| 🟡 Amarillo | Sin ubicación (solo recibe alertas)                   |
| 🔴 Rojo   | Ubicación configurada, sin conexión al servidor          |
| ⚫ Gris   | Sin ubicación y sin servidor                             |

### Modo simulacro

`Ctrl+Mayúsculas+F12` lanza un aviso de simulacro (ventana naranja, etiqueta «SIMULACRO»). Los simulacros no aparecen en el historial real ni en los informes. El servidor conserva solo los 5 últimos.

---

## Compilar desde el código fuente

### Requisitos comunes

```bash
git clone <url-del-repositorio>
cd help-request-client
```

### Windows

Requiere Python 3.10+ con Tkinter y PyInstaller.

```bash
python build.py
# Genera: dist/SolicitudAyuda.exe
```

### Linux

Requiere Python 3.10+, `python3-tk` y FUSE (para AppImage).

```bash
bash build_linux.sh
# Genera: SolicitudAyuda-x86_64.AppImage
```

El script descarga `appimagetool` automáticamente si no está presente.

### macOS

Requiere Python 3.10+, Xcode Command Line Tools y las herramientas de sistema (`iconutil`, `hdiutil`).

```bash
bash build_macos.sh
# Genera: dist/SolicitudAyuda.app  y  dist/SolicitudAyuda.dmg
```

El script instala automáticamente las dependencias `pyobjc` necesarias para pynput en macOS.

> **Nota:** Sin firma de desarrollador Apple, macOS mostrará un aviso de Gatekeeper. Consulta [`docs/manual-instalacion-macos.md`](docs/manual-instalacion-macos.md) para las instrucciones de autorización.

---

## Dependencias principales

| Paquete       | Uso                                               |
|---------------|---------------------------------------------------|
| `pynput`      | Captura de hotkeys globales (X11, Windows, macOS) |
| `pystray`     | Icono en la bandeja del sistema                   |
| `Pillow`      | Generación del icono y renderizado                |
| `requests`    | Comunicación HTTP con el servidor                 |
| `tkinter`     | Ventanas de configuración y ayuda                 |
| `pyobjc`      | Solo macOS — soporte nativo para pynput           |

Todas las dependencias están en [`requirements.txt`](requirements.txt).

---

## Estructura del proyecto

```
help-request-client/
├── main.py                          # Punto de entrada, arranque y coordinación
├── config.py                        # Configuración local, paths, conversión de hotkeys
├── core/
│   ├── alert.py                     # Envío de alertas (real y simulacro), deduplicación
│   └── network.py                   # Descubrimiento de servidor, registro, heartbeat, API REST
├── platform_support/
│   ├── hotkey.py                    # Registro de hotkeys globales con pynput
│   ├── autostart.py                 # Arranque automático (registro/LaunchAgent/.desktop/Openbox)
│   ├── updater.py                   # Auto-actualización desde GitHub Releases (Linux y Windows)
│   ├── sound.py                     # Sonido de alerta por plataforma
│   ├── trigger_socket.py            # Socket Unix para disparos externos (Wayland)
│   ├── wayland_shortcuts.py         # Registro de atajos en GNOME y KDE Plasma
│   └── macos_permissions.py         # Comprobación del permiso de Accesibilidad (macOS)
├── ui/
│   ├── alert_popup.py               # Ventana emergente de alerta (rojo) y simulacro (naranja)
│   ├── setup_window.py              # Configuración de ubicación con selects en cascada
│   ├── hotkey_info.py               # Ventana de bienvenida con el atajo activo
│   ├── help_window.py               # Ayuda in-app (manual de usuario embebido)
│   ├── tray.py                      # Icono y menú de la bandeja del sistema
│   └── fonts.py                     # Fuentes por plataforma (Segoe UI / SF Pro / DejaVu)
├── docs/
│   ├── manual-usuario.md
│   ├── manual-instalacion-windows.md
│   ├── manual-instalacion-linux.md
│   └── manual-instalacion-macos.md
├── build.py                         # Script de compilación para Windows
├── build_linux.sh                   # Script de compilación para Linux (AppImage)
├── build_macos.sh                   # Script de compilación para macOS (.app / .dmg)
├── macos_info.plist                 # Info.plist del bundle macOS (LSUIElement, Accesibilidad)
├── requirements.txt
└── LICENSE
```

---

## Puertos de red

| Puerto | Protocolo | Dirección      | Uso                                       |
|--------|-----------|----------------|-------------------------------------------|
| 54321  | UDP       | Entrada/Salida | Alertas P2P, descubrimiento de servidor   |
| 8080   | TCP       | Salida         | Comunicación REST con el servidor         |

---

## Licencia

Solicitudes de Ayuda se publica bajo la **GNU Affero General Public License, versión 3**
(AGPL-3.0-or-later). Puede usar, copiar, modificar y redistribuir el software libremente
siempre que conserve esta misma licencia y haga públicas las modificaciones que distribuya
o ponga en producción.

Texto completo: <https://www.gnu.org/licenses/agpl-3.0.html>

---

## Soporte comercial e instalación

Desarrollado por **Direct Sevilla Global Services SL**, con 20 años de experiencia en
desarrollos para el sector sanitario.

Ofrecemos la plantilla de máquina virtual del servidor preconfigurada lista para desplegar,
así como servicios profesionales de instalación, formación y soporte técnico.

**info@directsur.com**
