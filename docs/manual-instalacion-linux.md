# Instalación del cliente — Linux

## Requisitos

- Distribución Linux de 64 bits (x86_64) con entorno gráfico
- Recomendado: Ubuntu 22.04 LTS o posterior, Debian 11 o posterior,
  Fedora 38 o posterior, Linux Mint 21 o posterior
- Conexión a la red local del centro
- El servidor de Solicitudes de Ayuda debe estar instalado y en marcha en la red

---

## Descarga

Descargue el archivo `SolicitudAyuda-x86_64.AppImage` desde la ubicación que le haya
indicado su administrador de sistemas.

---

## Instalación

El cliente se distribuye como **AppImage**: un único archivo ejecutable que no requiere
instalación ni permisos de administrador.

### Paso 1 — Hacer ejecutable el archivo

Abra un terminal y ejecute:

```bash
chmod +x SolicitudAyuda-x86_64.AppImage
```

O bien, en el gestor de archivos: clic derecho sobre el archivo →
**Propiedades → Permisos → Permitir ejecutar el archivo como programa**.

### Paso 2 — Mover a una ubicación permanente (recomendado)

```bash
mkdir -p ~/.local/bin
mv SolicitudAyuda-x86_64.AppImage ~/.local/bin/SolicitudAyuda
```

### Paso 3 — Ejecutar

```bash
~/.local/bin/SolicitudAyuda
```

O haga doble clic en el archivo desde el gestor de archivos.

---

## Primer inicio

1. Aparece la **ventana de información del atajo de teclado**.
2. A continuación la **ventana de configuración de ubicación**:
   - **Servidor** — si el servidor está en el mismo segmento de red que este equipo, se
     detecta automáticamente y el campo puede quedarse vacío. Si el servidor está en un
     segmento diferente (por ejemplo, en un CPD), introduzca su URL completa:
     `http://192.168.10.50:8080` y pulse **Conectar**.
   - Los campos de ubicación funcionan en **cascada**: seleccione primero el centro y cada
     selector siguiente se activará mostrando solo los elementos que le corresponden. Si
     algún elemento no aparece, pulse **[+]** para añadirlo.
   - Los cuatro campos de ubicación son obligatorios.
3. Pulse **Confirmar ubicación**. El icono aparece en la bandeja del sistema.

La aplicación se configura automáticamente para **arrancar con la sesión de escritorio**
mediante un archivo `.desktop` en `~/.config/autostart/`.

---

## Sesiones Wayland (Ubuntu 24.04, Fedora 38+, etc.)

En entornos Wayland, las aplicaciones no pueden capturar atajos de teclado globales por
seguridad. El cliente detecta automáticamente esta situación y ofrece configurar los atajos
en el propio entorno de escritorio.

### GNOME (Ubuntu, Fedora con GNOME)

Al pulsar **Sí** en el diálogo, la aplicación registra automáticamente dos atajos en
la configuración de GNOME:
- **Ctrl + F12** (o el atajo configurado en el servidor) → alerta real
- **Ctrl + Mayúsculas + F12** → simulacro

Puede verificarlos en: **Configuración → Teclado → Atajos de teclado → Atajos personalizados**

### KDE Plasma (Kubuntu, Fedora KDE)

Los atajos se registran en la configuración de `kglobalshortcutsrc`. Puede que sea
necesario cerrar y volver a abrir sesión para que queden activos.

### Otros entornos (XFCE, MATE, Cinnamon...)

En sesión **X11** (no Wayland), el atajo funciona sin configuración adicional.
En sesión **Wayland** con un entorno no compatible, la aplicación mostrará las instrucciones
para configurar el atajo manualmente. El comando a asociar es:

```
/ruta/a/SolicitudAyuda --trigger
```

---

## Desinstalación

```bash
# Detener la aplicación (clic derecho en icono → Salir)
rm ~/.local/bin/SolicitudAyuda                            # ejecutable
rm ~/.config/autostart/help-request.desktop              # arranque automático
rm -rf ~/.config/HelpRequest/                            # configuración
```

---

## Puertos de red utilizados

| Puerto | Protocolo | Dirección      | Uso                          |
|--------|-----------|----------------|------------------------------|
| 54321  | UDP       | Entrada/Salida | Alertas entre equipos        |
| 8080   | TCP       | Salida         | Comunicación con el servidor |

Si el sistema tiene `ufw` activo, no es necesario abrir puertos de entrada manualmente ya
que el cliente inicia las conexiones. En redes con cortafuegos estrictos, consulte con el
administrador de red.

---

## Licencia, soporte y contacto

**Licencia:** Solicitudes de Ayuda se publica bajo la
**GNU Affero General Public License, versión 3** (AGPL-3.0-or-later).
Puede usar, copiar, modificar y redistribuir el software libremente siempre que
conserve esta misma licencia y haga públicas las modificaciones que distribuya o
ponga en producción. Esta licencia no limita en ningún caso la prestación de
servicios profesionales sobre el software.

Texto completo: <https://www.gnu.org/licenses/agpl-3.0.html>

---

Solicitudes de Ayuda es un producto de **Direct Sevilla Global Services SL**, empresa con
20 años de experiencia en desarrollos para el sector sanitario.

Para soporte técnico, servicios de instalación o cualquier consulta:

**info@directsur.com**
