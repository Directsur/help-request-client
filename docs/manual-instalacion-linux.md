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

### Paso 2 — Ejecutar

```bash
./SolicitudAyuda-x86_64.AppImage
```

O haga doble clic en el archivo desde el gestor de archivos.

> **Instalación automática:** en el primer inicio, la aplicación se copia automáticamente
> a su ruta fija:
> - `/usr/local/bin/SolicitudAyuda` si el equipo pertenece a un entorno multiusuario y el
>   administrador ha dado permiso de escritura (o si el propio administrador ha ejecutado
>   la aplicación por primera vez con `sudo`).
> - `~/.local/bin/SolicitudAyuda` en caso contrario (instalación por usuario).
>
> El autoarranque y las actualizaciones automáticas usarán siempre esa ruta fija.
> No es necesario mover el archivo manualmente.

### Instalación del sistema para todos los usuarios

Si el equipo tiene varios usuarios y todos deben tener acceso a la aplicación,
use el instalador integrado ejecutando como **root**:

```bash
sudo ./SolicitudAyuda-x86_64.AppImage --install
```

Aparecerá una ventana de confirmación que informa de las rutas que se van a utilizar.
Al aceptar, el instalador realiza automáticamente:

- Copia el ejecutable a `/usr/local/bin/SolicitudAyuda`
- Crea `/etc/xdg/autostart/help-request.desktop` — lo leen todos los gestores de
  sesión XDG (GNOME, KDE, XFCE, lxsession…) para **todos** los usuarios presentes
  y futuros
- Añade una entrada en `/etc/xdg/openbox/autostart` si Openbox está instalado

Cada usuario verá la ventana de configuración de ubicación la primera vez que inicie
sesión. Sus datos se guardan en su propio perfil (`~/.config/HelpRequest/`).

Las actualizaciones automáticas quedan deshabilitadas en instalaciones del sistema.
Para actualizar, el administrador vuelve a ejecutar el instalador con la nueva versión:

```bash
sudo ./SolicitudAyuda-nueva-version.AppImage --install
```

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
   - **Equipo de seguridad** — active esta casilla si el equipo debe recibir
     todos los avisos del centro independientemente del grupo.
   - **Equipo portátil** — active esta casilla si el equipo se desplaza entre
     ubicaciones. En portátiles, la ventana de ubicación aparece en cada inicio
     de sesión. En equipos fijos, una vez configurada la ubicación, solo vuelve
     a aparecer automáticamente una vez al mes.
3. Pulse **Confirmar ubicación**. El icono aparece en la bandeja del sistema.

La aplicación se configura automáticamente para **arrancar con la sesión de escritorio**:

- Entornos con gestor de sesión XDG (GNOME, KDE, XFCE, lxsession…): archivo `.desktop`
  en `~/.config/autostart/`.
- **Openbox** sin gestor de sesión XDG: entrada añadida a `~/.config/openbox/autostart`.

En ambos casos el ejecutable referenciado es la ruta fija donde se instaló
(`/usr/local/bin/SolicitudAyuda` o `~/.local/bin/SolicitudAyuda`).

---

## Actualizaciones automáticas

La aplicación comprueba en segundo plano si hay una nueva versión disponible (60 segundos
después del arranque). Si la hay, la descarga directamente sobre `~/.local/bin/SolicitudAyuda`
y envía una notificación de escritorio. La nueva versión queda activa en el siguiente
inicio de la aplicación.

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

La forma más sencilla es usar el desinstalador integrado. Cierre primero la aplicación
(clic derecho en el icono → **Salir**) y luego ejecute:

```bash
SolicitudAyuda --uninstall
```

Aparecerá una ventana de confirmación. Al aceptar, se eliminarán el ejecutable,
el autoarranque y la configuración del usuario actual.

> **Instalación del sistema** (`/usr/local/bin/`): el desinstalador necesita permisos
> de administrador para borrar el ejecutable y las entradas de autoarranque del sistema.
> Ejecútelo con:
> ```bash
> sudo SolicitudAyuda --uninstall
> ```
> Los datos de configuración de otros usuarios (`~/.config/HelpRequest/` en cada perfil)
> deben eliminarse manualmente o con el desinstalador en la sesión de cada usuario.

### Desinstalación manual

```bash
# Detener la aplicación (clic derecho en icono → Salir)
sudo rm /usr/local/bin/SolicitudAyuda           # instalación del sistema (si aplica)
rm ~/.local/bin/SolicitudAyuda                  # instalación de usuario (si aplica)
sudo rm /etc/xdg/autostart/help-request.desktop # autoarranque del sistema (si aplica)
rm ~/.config/autostart/help-request.desktop     # autoarranque del usuario (si aplica)
rm -rf ~/.config/HelpRequest/
```

Para Openbox, elimine también las líneas marcadas `# SolicitudAyuda` de
`~/.config/openbox/autostart` y/o `/etc/xdg/openbox/autostart`.

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
