# Instalación del cliente — macOS

## Requisitos

- macOS 11 Big Sur o posterior (compatible con macOS 12, 13, 14 y 15)
- Mac con procesador Intel o Apple Silicon (M1/M2/M3/M4)
- Conexión a la red local del centro
- El servidor de Solicitudes de Ayuda debe estar instalado y en marcha en la red

---

## Descarga

Descargue el archivo `SolicitudAyuda.dmg` desde la ubicación que le haya indicado su
administrador de sistemas.

---

## Instalación

### Paso 1 — Abrir la imagen de disco

Haga doble clic en `SolicitudAyuda.dmg`. Se abrirá una ventana con el icono de la
aplicación y un acceso directo a la carpeta **Aplicaciones**.

### Paso 2 — Instalar la aplicación

Arrastre el icono **SolicitudAyuda** hasta la carpeta **Aplicaciones**.

### Paso 3 — Primer inicio y Gatekeeper

La primera vez que abra la aplicación, macOS mostrará el siguiente aviso:

> «"SolicitudAyuda" no se puede abrir porque Apple no puede comprobar que no contenga
> software malicioso.»

Esto ocurre porque la aplicación no tiene firma de Apple (requiere una costosa cuenta de
desarrollador). Para autorizarla:

**Opción A (recomendada):**
1. Vaya a **Ajustes del Sistema → Privacidad y Seguridad**.
2. Desplácese hasta la sección **Seguridad**.
3. Verá el mensaje «Se bloqueó "SolicitudAyuda" porque no es de un desarrollador identificado».
4. Pulse el botón **Abrir de todas formas**.
5. Confirme pulsando **Abrir** en el diálogo siguiente.

**Opción B (terminal):**
```bash
sudo xattr -cr /Applications/SolicitudAyuda.app
```
A partir de ese momento la aplicación se abrirá sin avisos.

---

## Permiso de Accesibilidad (obligatorio para el atajo de teclado)

macOS requiere un permiso especial para que las aplicaciones detecten atajos de teclado
cuando otra ventana está en primer plano.

Al iniciar por primera vez, la aplicación mostrará un diálogo explicativo y abrirá
automáticamente el panel de Privacidad y Seguridad.

Para conceder el permiso:

1. En **Ajustes del Sistema → Privacidad y Seguridad → Accesibilidad**.
2. Pulse el candado para desbloquear (necesita su contraseña de administrador).
3. Active la casilla junto a **SolicitudAyuda** en la lista.
4. **Cierre y vuelva a abrir la aplicación** para que el cambio surta efecto.

> **Sin este permiso**, la aplicación funciona en modo solo-recepción: recibirá las alertas
> de sus compañeros pero no podrá enviar alertas con el atajo de teclado.

---

## Primer inicio completo

Una vez concedido el permiso de Accesibilidad:

1. Aparece la **ventana de información del atajo de teclado** con la combinación activa.
2. A continuación la **ventana de configuración de ubicación**:
   - **Servidor** — si el servidor está en el mismo segmento de red que este equipo, se
     detecta automáticamente y el campo puede quedarse vacío. Si el servidor está en un
     segmento diferente (por ejemplo, en un CPD), introduzca su URL completa:
     `http://192.168.10.50:8080` y pulse **Conectar**.
   - Los campos de ubicación funcionan en **cascada**: seleccione primero el centro y cada
     selector siguiente se activará mostrando solo los elementos que le corresponden. Si
     algún elemento no aparece, pulse **[+]** para añadirlo.
   - Los cuatro campos de ubicación son obligatorios.
3. Pulse **Confirmar ubicación**. El icono aparece en la barra de menús superior.

La aplicación **no aparece en el Dock** por diseño: es una aplicación de barra de menús.

---

## Arranque automático

La aplicación se configura automáticamente para arrancar al iniciar sesión mediante un
archivo en `~/Library/LaunchAgents/es.centrosalud.solicitudayuda.plist`.

Para desactivar el arranque automático:
1. Abra **Ajustes del Sistema → General → Elementos de inicio de sesión**.
2. Elimine **SolicitudAyuda** de la lista.

---

## Desinstalación

1. Cierre la aplicación: clic en el icono de la barra de menús → **Salir**.
2. Elimine la aplicación:
   ```bash
   rm -rf /Applications/SolicitudAyuda.app
   ```
3. Elimine los archivos de configuración y arranque automático:
   ```bash
   rm -rf ~/.config/HelpRequest/
   launchctl unload ~/Library/LaunchAgents/es.centrosalud.solicitudayuda.plist
   rm ~/Library/LaunchAgents/es.centrosalud.solicitudayuda.plist
   ```

---

## Puertos de red utilizados

| Puerto | Protocolo | Dirección      | Uso                          |
|--------|-----------|----------------|------------------------------|
| 54321  | UDP       | Entrada/Salida | Alertas entre equipos        |
| 8080   | TCP       | Salida         | Comunicación con el servidor |

El cortafuegos integrado de macOS normalmente permite estas conexiones sin configuración
adicional. Si aparece un diálogo preguntando si se permite la conexión, responda
**Permitir**.

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
