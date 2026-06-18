# Manual de usuario — Solicitudes de Ayuda (cliente)

## ¿Qué es este sistema?

Solicitudes de Ayuda es un sistema de alerta inmediata entre equipos de una misma red
local. Está diseñado originalmente para personal sanitario y administrativo de centros de
salud y hospitales, aunque puede utilizarse en cualquier organización o sector donde sea
necesario comunicar una emergencia de forma rápida: centros educativos, residencias,
instalaciones industriales, servicios de seguridad, etc.

Cuando una persona pulsa el atajo de teclado configurado, todos los equipos del mismo grupo
reciben una notificación en pantalla con la ubicación exacta de quien solicitó ayuda.
El sistema funciona en la red local sin necesidad de internet.

---

## El icono en la barra de tareas

La aplicación permanece activa en el área de notificaciones (bandeja del sistema). El icono
cambia de color según el estado:

| Color    | Significado                                                  |
|----------|--------------------------------------------------------------|
| Verde    | Todo correcto: ubicación configurada y servidor conectado    |
| Amarillo | Sin ubicación configurada (solo puede recibir alertas)       |
| Rojo     | Ubicación configurada pero sin conexión al servidor          |
| Gris     | Sin ubicación y sin servidor (modo desconectado)             |

Para ver el estado detallado, pase el cursor sobre el icono: aparecerá el atajo de teclado
activo y el estado de la conexión.

---

## Enviar una alerta de ayuda

1. Pulse el **atajo de teclado configurado** (por defecto **Ctrl + F12**).
2. La alerta se envía de forma inmediata a todos los equipos de su grupo y a los equipos de
   seguridad adscritos al mismo centro.
3. El mensaje incluye su nombre de usuario, el nombre del equipo y la ubicación exacta
   (sala, planta, edificio y centro).

> **Nota:** El atajo de teclado funciona aunque la ventana de la aplicación esté cerrada
> o haya otras ventanas en primer plano.
>
> Si su equipo no tiene ubicación configurada, la alerta no se enviará. El icono amarillo o
> gris le indicará esta situación.

---

## Recibir una alerta

Cuando un compañero solicita ayuda, aparecerá automáticamente una **ventana emergente roja**
con la información completa:

- Nombre del usuario que solicitó ayuda
- Nombre del equipo de origen
- Ubicación: sala, planta, edificio y centro

La ventana se cierra automáticamente pasados 30 segundos, o puede cerrarla manualmente
pulsando la tecla **Escape** o el botón **Cerrar**.

---

## Modo simulacro

Para comprobar que el sistema funciona sin generar una alerta real, utilice el atajo fijo
**Ctrl + Mayúsculas + F12**.

La ventana emergente aparecerá en **naranja** con la indicación «SIMULACRO» bien visible.
El servidor registra los simulacros por separado y los excluye de los informes y correos.
Solo se conservan los últimos 5 registros de simulacro.

---

## Configurar su ubicación

La primera vez que inicia la aplicación aparece la ventana de configuración de ubicación.
Los campos forman una **jerarquía en cascada**: cada selector solo muestra los elementos
que pertenecen a la selección anterior.

1. Elija el **Centro** en el primer desplegable.
2. Una vez seleccionado el centro, el desplegable **Edificio** se activa y muestra solo
   los edificios de ese centro.
3. Al seleccionar el edificio, se activa **Planta** con las plantas de ese edificio.
4. Al seleccionar la planta, se activa **Sala** con las salas de esa planta.

Si un elemento no aparece en la lista porque aún no existe en el servidor, pulse el botón
**[+]** situado a la derecha del campo correspondiente para añadirlo. El nuevo elemento
queda disponible inmediatamente en el selector.

Los **cuatro campos son obligatorios** para poder enviar alertas. El botón «Confirmar
ubicación» valida que todos estén rellenos antes de guardar.

Si desea omitir la configuración y configurarla más tarde, cierre la ventana con la **X**.
La aplicación le preguntará si desea continuar sin ubicación; en ese caso el equipo
solo podrá recibir alertas, no enviarlas (icono amarillo o gris).

Para volver a la ventana de configuración en cualquier momento:
**clic derecho en el icono → Configurar ubicación...**

La ubicación guardada se preselecciona automáticamente la próxima vez que se abra la
ventana, por lo que solo tendrá que revisar y confirmar si todo es correcto.

---

## Cambio automático del atajo de teclado

El atajo de teclado puede ser modificado por el administrador del sistema desde el interfaz
web del servidor. El cliente descarga automáticamente el nuevo atajo la próxima vez que
arranca o se conecta al servidor. No es necesario reinstalar nada.

El atajo activo se muestra siempre:
- En la ventana que aparece al iniciar la aplicación
- Al pasar el cursor sobre el icono de la bandeja
- En el menú del icono de la bandeja

---

## Preguntas frecuentes

**¿Qué ocurre si el servidor está caído?**
El sistema sigue funcionando en modo local: los equipos se comunican directamente entre sí
por la red local. Las alertas se envían y reciben con normalidad. Solo se pierde el registro
histórico en el servidor mientras dura la caída.

**¿Puedo usar el sistema en varias redes (edificios con VLANs)?**
Si la red tiene VLANs que separan los equipos, el sistema usa la lista de equipos conocidos
para enviar las alertas de forma individual. El administrador de red debe asegurarse de que
el puerto UDP 54321 y el puerto TCP 8080 estén permitidos entre las VLANs.

**¿Qué pasa si pulso el atajo por error?**
La alerta se envía inmediatamente. No hay confirmación previa por diseño (para no perder
tiempo en una emergencia real). Informe verbalmente a sus compañeros de que fue un error.
Existe un periodo de espera de 10 segundos antes de poder enviar otra alerta desde el mismo
equipo.

**El icono aparece en gris, ¿qué hago?**
Compruebe que el equipo está conectado a la red local. Si tiene red, abra la ventana de
configuración de ubicación y verifique que los datos son correctos. Si el servidor no
responde, contacte con el administrador del sistema.

**¿Por qué en Linux me pide configurar atajos del sistema?**
En sesiones Wayland (el nuevo sistema de ventanas de Linux), las aplicaciones no pueden
detectar pulsaciones de teclado globales por sí solas. Por eso la aplicación registra
los atajos directamente en GNOME o KDE. Este proceso es automático y solo ocurre una vez.

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
