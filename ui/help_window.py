# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Ventana de ayuda del cliente — muestra el manual de usuario."""
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from ui.fonts import SANS, MONO

# ─── Contenido del manual ──────────────────────────────────────────────────────

_SECTIONS = [
    ("¿Qué es este sistema?", """\
Solicitudes de Ayuda es un sistema de alerta inmediata entre equipos de una misma
red local. Está diseñado originalmente para personal sanitario y administrativo de
centros de salud y hospitales, aunque puede utilizarse en cualquier organización o
sector donde sea necesario comunicar una emergencia de forma rápida: centros
educativos, residencias, instalaciones industriales, servicios de seguridad, etc.

Cuando una persona pulsa el atajo de teclado configurado, todos los equipos del
mismo grupo reciben una notificación en pantalla con la ubicación exacta de quien
solicitó ayuda. Funciona en la red local sin necesidad de internet.\
"""),

    ("El icono en la bandeja del sistema", """\
El icono cambia de color según el estado:

  • Verde     — Configurado y conectado al servidor
  • Amarillo  — Sin ubicación (solo recibe alertas, no puede enviar)
  • Rojo      — Ubicación configurada, pero sin conexión al servidor
  • Gris      — Sin ubicación y sin servidor (modo desconectado)

Pase el cursor sobre el icono para ver el atajo activo y el estado de conexión.\
"""),

    ("Enviar una alerta de ayuda", """\
1. Pulse el atajo de teclado configurado (por defecto Ctrl + F12).
2. La alerta se envía inmediatamente a todos los equipos del mismo grupo
   y a los equipos de seguridad adscritos al mismo centro.
3. El mensaje incluye su nombre, el nombre del equipo y la ubicación completa.

El atajo funciona aunque la ventana esté cerrada o haya otras aplicaciones en
primer plano. Si el icono es amarillo o gris, el equipo no tiene ubicación
configurada y no puede enviar alertas.\
"""),

    ("Recibir una alerta", """\
Al recibir una alerta de un compañero aparece una ventana emergente ROJA con:

  • Nombre del usuario que solicitó ayuda
  • Nombre del equipo de origen
  • Ubicación: sala, planta, edificio y centro

La ventana se cierra automáticamente a los 30 segundos o al pulsar Escape.\
"""),

    ("Modo simulacro", """\
Para comprobar que el sistema funciona sin generar una alerta real:

  Pulse  Ctrl + Mayúsculas + F12

La ventana emergente aparece en NARANJA con la indicación «SIMULACRO».
Los simulacros quedan excluidos del historial de alertas, de los informes
y de los correos al responsable de prevención.
Solo se conservan los últimos 5 registros de simulacro en el servidor.\
"""),

    ("Configurar la ubicación", """\
La primera vez que abre la aplicación aparece la ventana de configuración.

Servidor
  En la parte superior hay un campo «Servidor». Si el servidor está en el
  mismo segmento de red, se detecta automáticamente y puede dejarlo vacío.
  Si está en un segmento distinto (por ejemplo, un CPD al que se llega a
  través del router), introduzca la URL completa y pulse Conectar:

    Ejemplo:  http://192.168.10.50:8080

  La URL se guarda y se usa en todos los arranques posteriores.

Ubicación
  Los campos funcionan en cascada: cada selector depende del anterior.

  1. Elija el Centro.
  2. Se activa Edificio → muestra solo los edificios de ese centro.
  3. Se activa Planta → muestra solo las plantas de ese edificio.
  4. Se activa Sala → muestra solo las salas de esa planta.

  Si un elemento no aparece en la lista, pulse [+] a la derecha del campo
  para añadirlo. El nuevo elemento queda disponible de inmediato.

  Los cuatro campos son obligatorios para poder enviar alertas.
  El botón «Confirmar ubicación» no se activa hasta que todos estén rellenos.

Tipo de equipo
  ☐  Equipo de seguridad/guardia — recibe todos los avisos del centro,
     independientemente del grupo al que pertenezca.

  ☐  Equipo portátil — la ventana de ubicación aparece en cada inicio de
     sesión para que el usuario pueda actualizar su posición.
     En equipos fijos, una vez configurada la ubicación, esta ventana solo
     vuelve a aparecer automáticamente una vez al mes.

Para omitir por ahora: cierre la ventana con la X y confirme el aviso.
El equipo arrancará en modo solo-recepción (icono amarillo o gris).

La próxima vez que abra la configuración, los campos se preseleccionan
automáticamente con los datos ya guardados.

Para volver a la configuración en cualquier momento:
  Clic derecho en el icono → Configurar ubicación...\
"""),

    ("Cambio del atajo de teclado", """\
El atajo puede ser modificado por el administrador desde el interfaz web del
servidor. El cliente descarga el nuevo atajo automáticamente la próxima vez que
arranque o se reconecte.

El atajo activo se muestra siempre:
  • En la ventana de inicio de la aplicación
  • Al pasar el cursor sobre el icono de la bandeja
  • En el menú del icono (clic derecho)\
"""),

    ("Preguntas frecuentes", """\
¿Qué pasa si el servidor está caído?
  El sistema sigue funcionando en red local: los equipos se comunican
  directamente. Solo se pierde el registro histórico mientras dura la caída.

¿Qué hago si pulsé el atajo por error?
  Informe verbalmente a sus compañeros. No hay confirmación previa por diseño.
  Hay un periodo de espera de 10 segundos antes de poder enviar otra alerta.

El icono está gris, ¿qué hago?
  Compruebe la conexión de red. Abra «Configurar ubicación...» y verifique
  que los datos son correctos. Si el servidor no responde, contacte con el
  administrador.

El cliente no encuentra el servidor (icono rojo o gris persistente).
  Si el servidor está en un segmento de red diferente al de este equipo,
  el descubrimiento automático por UDP no funcionará. Abra «Configurar
  ubicación...», introduzca la URL del servidor en el campo Servidor
  (p. ej. http://192.168.10.50:8080) y pulse Conectar.

¿Funciona sin conexión a internet?
  Sí. El sistema funciona completamente en la red local del centro.
  No necesita internet en ningún momento.\
"""),

    ("Instalación, actualización y desinstalación", """\
La aplicación se gestiona desde la línea de comandos con las siguientes opciones.
Todas muestran una ventana gráfica de confirmación antes de actuar.

──  Instalación del sistema (todos los usuarios)

  Requiere ejecutarse como root (Linux/macOS) o Administrador (Windows).
  Copia el ejecutable a la ruta del sistema y activa el autoarranque para
  todos los usuarios del equipo, incluidos los que se creen en el futuro.

    Linux:   sudo ./SolicitudAyuda-x86_64.AppImage --install
    Windows: SolicitudAyuda.exe --install   (como Administrador)
    macOS:   sudo /ruta/SolicitudAyuda.app/Contents/MacOS/SolicitudAyuda --install

  Rutas del sistema:
    Linux:   /usr/local/bin/SolicitudAyuda
             /etc/xdg/autostart/help-request.desktop
    Windows: C:\\ProgramData\\SolicitudAyuda\\SolicitudAyuda.exe
             HKLM\\...\\CurrentVersion\\Run
    macOS:   /Applications/SolicitudAyuda.app
             /Library/LaunchAgents/es.centrosalud.solicitudayuda.plist

  Las actualizaciones automáticas quedan deshabilitadas en instalaciones del
  sistema. Para actualizar, el administrador repite el mismo comando con la
  nueva versión.

──  Desinstalación

  Elimina el ejecutable, el autoarranque y la configuración del usuario actual.

    Linux:   SolicitudAyuda --uninstall
    Windows: SolicitudAyuda --uninstall
    macOS:   /Applications/SolicitudAyuda.app/Contents/MacOS/SolicitudAyuda --uninstall

  En instalaciones del sistema, ejecute como root/Administrador para eliminar
  también el ejecutable compartido y las entradas de autoarranque del sistema.

    Linux:   sudo SolicitudAyuda --uninstall
    Windows: SolicitudAyuda --uninstall   (como Administrador)
    macOS:   sudo /Applications/SolicitudAyuda.app/Contents/MacOS/SolicitudAyuda --uninstall

  Los datos de configuración de otros usuarios deben eliminarse manualmente
  en cada perfil (carpeta ~/.config/HelpRequest/ o %APPDATA%\\HelpRequest\\).\
"""),

    ("Licencia, soporte y contacto", """\
Licencia
  Solicitudes de Ayuda se publica bajo la GNU Affero General Public
  License, versión 3 (AGPL-3.0-or-later). Puede usar, copiar, modificar
  y redistribuir el software libremente siempre que conserve esta misma
  licencia y haga públicas las modificaciones que distribuya o ponga en
  producción. Esta licencia no limita la prestación de servicios
  profesionales sobre el software.

  https://www.gnu.org/licenses/agpl-3.0.html

Desarrollado por
  Direct Sevilla Global Services SL
  20 años de experiencia en desarrollos para el sector sanitario

Soporte técnico, instalación y consultas
  info@directsur.com\
"""),
]


# ─── Ventana ───────────────────────────────────────────────────────────────────

def show():
    win = tk.Tk()
    win.title("Solicitudes de Ayuda — Ayuda")
    win.geometry("680x540")
    win.minsize(500, 400)
    win.configure(bg="#1a1a2e")

    # Cabecera
    header = tk.Frame(win, bg="#c0392b", pady=10)
    header.pack(fill="x")
    tk.Label(
        header,
        text="Manual de usuario",
        font=(SANS, 14, "bold"),
        fg="white",
        bg="#c0392b",
    ).pack()

    # Área de texto
    txt = ScrolledText(
        win,
        font=(SANS, 10),
        bg="#0d1117",
        fg="#e6edf3",
        insertbackground="white",
        relief="flat",
        wrap="word",
        padx=18,
        pady=14,
        state="normal",
    )
    txt.pack(fill="both", expand=True, padx=0, pady=0)

    # Etiquetas de formato
    txt.tag_configure("heading",
                      font=(SANS, 11, "bold"),
                      foreground="#f0f0a0",
                      spacing1=14,
                      spacing3=4)
    txt.tag_configure("separator",
                      foreground="#444466",
                      spacing1=2,
                      spacing3=6)
    txt.tag_configure("body",
                      font=(SANS, 10),
                      foreground="#e6edf3",
                      spacing1=0,
                      spacing3=0)

    for title, body in _SECTIONS:
        txt.insert("end", f"  {title}\n", "heading")
        txt.insert("end", "  " + "─" * 60 + "\n", "separator")
        # Indenta cada línea del cuerpo
        indented = "\n".join("  " + line for line in body.splitlines())
        txt.insert("end", indented + "\n\n", "body")

    txt.configure(state="disabled")

    # Botón de cierre
    btn_frame = tk.Frame(win, bg="#1a1a2e", pady=8)
    btn_frame.pack(fill="x")
    tk.Button(
        btn_frame,
        text="Cerrar",
        font=(SANS, 10),
        bg="#c0392b",
        fg="white",
        activebackground="#e74c3c",
        activeforeground="white",
        relief="flat",
        padx=24,
        pady=6,
        cursor="hand2",
        command=win.destroy,
    ).pack()

    win.bind("<Escape>", lambda _: win.destroy())
    win.focus_force()
    win.mainloop()
