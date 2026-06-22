# Instalación del cliente — Windows

## Requisitos

- Windows 10 (versión 1903 o posterior) o Windows 11
- Conexión a la red local del centro
- El servidor de Solicitudes de Ayuda debe estar instalado y en marcha en la red

---

## Descarga

Descargue el archivo `SolicitudAyuda.exe` desde la ubicación que le haya indicado su
administrador de sistemas (carpeta de red compartida, intranet del centro, etc.).

---

## Instalación

El cliente **no requiere instalación**. Es un único ejecutable portátil.

1. Descargue `SolicitudAyuda.exe` a cualquier carpeta accesible (Escritorio, Descargas…).
2. Haga doble clic para ejecutarlo.

> **Instalación automática:** en el primer inicio, la aplicación se copia automáticamente
> a su ubicación fija. Se intentan en orden:
> 1. `C:\ProgramData\SolicitudAyuda\SolicitudAyuda.exe` — compartida por todos los
>    usuarios del equipo (requiere permisos de administrador).
> 2. `C:\Users\<su usuario>\AppData\Local\SolicitudAyuda\SolicitudAyuda.exe` — solo
>    para el usuario actual (sin permisos especiales).
>
> El arranque automático de Windows usa siempre la ruta donde quedó instalada.
> No es necesario mover el archivo manualmente.

### Instalación del sistema para todos los usuarios

Si el equipo tiene varios usuarios y todos deben tener acceso a la aplicación,
use el instalador integrado. Haga **clic derecho → Ejecutar como administrador** sobre
`SolicitudAyuda.exe` y a continuación ejecute en la ventana de comandos:

```
SolicitudAyuda.exe --install
```

O con la ruta completa si hace falta:

```
"C:\Descargas\SolicitudAyuda.exe" --install
```

Aparecerá una ventana de confirmación. Al aceptar, el instalador:

- Copia el ejecutable a `C:\ProgramData\SolicitudAyuda\SolicitudAyuda.exe`
- Registra la entrada de autoarranque en `HKEY_LOCAL_MACHINE\...\Run`, lo que hace
  que la aplicación arranque para **todos** los usuarios presentes y futuros

Cada usuario verá la ventana de configuración de ubicación la primera vez que inicie
sesión. Sus datos se guardan en su propio perfil (`%APPDATA%\HelpRequest\`).

Las actualizaciones automáticas quedan deshabilitadas en instalaciones del sistema.
Para actualizar, el administrador vuelve a ejecutar el instalador:

```
"C:\Descargas\SolicitudAyuda-nueva.exe" --install
```

### Aviso de Windows SmartScreen

La primera vez puede aparecer el siguiente aviso de seguridad de Windows:

> «Windows protegió su equipo»

Haga clic en **Más información** y luego en **Ejecutar de todas formas**. Este aviso aparece
porque el ejecutable no tiene firma digital de Microsoft; es normal en software de gestión
interna que no se distribuye por la Microsoft Store.

### Antivirus

Algunos antivirus pueden marcar el archivo como sospechoso por ser un ejecutable empaquetado
con PyInstaller. Si ocurre, añada una excepción para la carpeta donde está instalado o
consulte con su administrador de sistemas.

---

## Primer inicio

Al arrancar por primera vez:

1. Aparece la **ventana de información del atajo de teclado** con la combinación de teclas
   configurada para enviar alertas (por defecto **Ctrl + F12**).
2. A continuación aparece la **ventana de configuración de ubicación**:
   - **Servidor** — si el servidor está en el mismo segmento de red que este equipo, se
     detecta automáticamente y el campo puede quedarse vacío. Si el servidor está en un
     segmento diferente (por ejemplo, en un CPD), introduzca su URL completa:
     `http://192.168.10.50:8080` y pulse **Conectar**.
   - Los campos de ubicación (centro, edificio, planta y sala) funcionan en **cascada**:
     seleccione primero el centro y cada selector siguiente se activará mostrando solo los
     elementos que le corresponden. Si algún elemento no aparece en la lista, pulse **[+]**
     junto al campo para añadirlo.
   - Los cuatro campos de ubicación son obligatorios antes de poder pulsar «Confirmar ubicación».
3. Pulse **Confirmar ubicación**. La aplicación queda activa en la bandeja del sistema
   (junto al reloj, en la esquina inferior derecha).

---

## Arranque automático con Windows

La aplicación se configura para arrancar automáticamente con Windows durante el primer
inicio. La entrada del Registro (`HKCU\...\Run`) apunta siempre a la ruta fija donde
quedó instalada (`C:\ProgramData\` o `%LOCALAPPDATA%`), por lo que el arranque
automático sobrevive a actualizaciones sin necesidad de reconfigurarlo.

Para desactivar el arranque automático, elimine la entrada «SolicitudAyuda» en:
**Administrador de tareas → Inicio → SolicitudAyuda → Deshabilitar**

---

## Actualizaciones automáticas

La aplicación comprueba en segundo plano si hay una nueva versión disponible (60 segundos
después del arranque). Si la hay, la descarga en segundo plano y muestra una notificación.
La actualización se aplica automáticamente en el siguiente inicio: al arrancar, la
aplicación detecta el archivo descargado, lo copia sobre sí misma y se relanza sin
intervención del usuario.

---

## Desinstalación

La forma más sencilla es usar el desinstalador integrado:

1. Cierre la aplicación: clic derecho en el icono de la bandeja → **Salir**.
2. Abra una ventana de comandos (si la instalación es del sistema, ábrala como
   **Administrador**) y ejecute:
   ```
   SolicitudAyuda --uninstall
   ```
   O bien, si conoce la ruta completa:
   ```
   "C:\ProgramData\SolicitudAyuda\SolicitudAyuda.exe" --uninstall
   ```
3. Confirme en la ventana que aparece. El desinstalador eliminará:
   - El ejecutable y su directorio (`C:\ProgramData\SolicitudAyuda\` o `%LOCALAPPDATA%\SolicitudAyuda\`)
   - La entrada de arranque automático del registro (`HKLM` si se ejecuta como
     Administrador, `HKCU` si se ejecuta como usuario normal)
   - Los datos de configuración del usuario actual (`%APPDATA%\HelpRequest\`)

> En una instalación del sistema (`C:\ProgramData\`), ejecute el desinstalador como
> **Administrador** para eliminar también la entrada `HKLM` y el ejecutable compartido.
>
> Cada usuario que haya iniciado sesión tiene su propia carpeta de configuración en
> `%APPDATA%\HelpRequest\`. El desinstalador solo elimina la del usuario que lo ejecuta.
> Para limpiarlas todas, elimine esa carpeta manualmente en cada perfil de usuario.

---

## Puertos de red utilizados

| Puerto   | Protocolo | Dirección  | Uso                                  |
|----------|-----------|------------|--------------------------------------|
| 54321    | UDP       | Entrada/Salida | Alertas entre equipos              |
| 8080     | TCP       | Salida     | Comunicación con el servidor         |

Asegúrese de que el cortafuegos de Windows no bloquea estos puertos para `SolicitudAyuda.exe`.
Al ejecutar por primera vez, Windows puede preguntar si se permite el acceso a la red;
responda **Permitir acceso**.

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
