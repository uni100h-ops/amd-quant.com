# AmdQuant v10: Connecting y avisos por correo cada 30 segundos

Este ZIP completo es para el proyecto de Render. Conserva los problemas, los
solvers, las mediciones independientes y la cabecera de v10. Añade un aviso al
propietario cada 30 segundos mientras alguien espera, con un indicador Connecting. No provisiona GPU y no necesita `AMD_NOTEBOOK_COOKIE`.

**Aún debes configurar el correo y desplegar estos archivos. No se ha enviado
ningún correo real desde las pruebas locales.**

## Configuración

1. Crea una cuenta gratuita en https://resend.com usando **el mismo correo en
   el que quieres recibir los avisos**. Selecciona el plan Free.
2. Abre https://resend.com/api-keys y crea una API key con permiso para enviar
   correos. Cópiala directamente a Render; no la pongas en el código ni en el chat.
3. En Render, abre tu servicio AmdQuant → Environment. Añade estas dos variables:

   | Variable | Valor |
   | --- | --- |
   | `RESEND_API_KEY` | La clave de Resend, que comienza por `re_` |
   | `GPU_ALERT_TO` | El correo con el que has creado la cuenta de Resend |

   El remitente predeterminado es `AmdQuant <onboarding@resend.dev>`. El dominio
   de prueba de Resend permite enviar únicamente al correo asociado a tu cuenta.
   Para esta demo y avisos a ti mismo, no tienes que comprar un dominio. Si usas
   otro destinatario, tendrás que verificar un dominio propio y configurar
   `GPU_ALERT_FROM` con un remitente de ese dominio.

4. Sustituye los archivos del proyecto que despliegas en Render por el contenido
   de este ZIP y despliega esa revisión. Conserva tu servicio y el mismo
   `GPU_WORKER_TOKEN`; no crees otro servicio. Los comandos siguen siendo:

   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn server.main:app --host 0.0.0.0 --port $PORT --workers 1`

5. Mantén `PUBLIC_DEMO=1`. Si llegaste a configurar la propuesta anterior de
   arranque mediante cookie, elimina `AMD_NOTEBOOK_COOKIE` después de desplegar
   esta versión: este código no la utiliza. Conserva las variables que ya usa
   tu worker; esta actualización no cambia el protocolo ni su token.

**En AMD/Jupyter no tienes que cambiar nada.** Conserva
`INICIAR_AMDQUANT_V10.ipynb` y su ZIP original `AmdQuant_GPU_AMD_v10.zip`.
El notebook verifica el hash de ese ZIP: no sustituyas allí el ZIP original
por este nuevo paquete para Render.

## Qué sucede al entrar

1. La página muestra **Connecting…** con una rueda girando mientras comprueba
   la conexión y mientras la GPU siga desconectada. Run permanece deshabilitado.
2. Si la GPU ya está activa, desaparece la rueda y la web funciona normalmente.
3. Si está desconectada y el correo está configurado, se esperan 20 segundos
   para permitir una posible reconexión del worker. Después se envía el primer
   aviso si sigue desconectada.
4. Se repite la solicitud de correo **cada 30 segundos** mientras haya alguien
   esperando. El temporizador está en el servidor; no necesitas configurar cron.
5. Tú abres AMD y ejecutas el notebook v10. La web revisa el estado cada 15
   segundos. Al detectar el worker conectado, quita Connecting, habilita Run
   y cesan los avisos. No ejecuta un problema automáticamente.

Connecting significa que la página espera la conexión; no significa que esté
creando una GPU. El texto debajo explica que la activación es manual. Si el
correo falla, se informa sin quitar la rueda de espera. La recepción del correo
puede tardar más que el intervalo de envío y no está garantizada por la web.

## Repetición y visitas simultáneas

- Todos los visitantes comparten un solo temporizador: diez pestañas no generan
  diez correos cada 30 segundos.
- La página comunica que sigue esperando cada 15 segundos. Si dejan de llegar
  esas señales durante 60 segundos, el servidor detiene los avisos. Cerrar todas
  las pestañas puede dejar hasta 60 segundos de margen antes de parar. Un
  navegador suspendido o que congele la pestaña también puede interrumpirlos.
- Cuando la GPU está conectada no se envían avisos. Un correo ya enviado al
  proveedor justo antes de la reconexión no se puede retirar.
- Los errores se reintentan con el mismo intervalo. No se afirma que un envío
  haya sido aceptado si el proveedor devuelve un error.
- Resend recibe una clave de deduplicación por intervalo UTC de 30 segundos.
  Así no duplica un mismo mensaje de ese intervalo tras un reinicio de Render.
  Mientras el proceso sigue activo, los intentos están separados al menos
  30 segundos. Reinicios, red o carga del servidor pueden alterar el horario.
- Las consultas de salud y de información no activan avisos por sí solas:
  hace falta una señal de espera de la página. No hay pings para mantener AMD
  despierto ni consumo GPU provocado por este mecanismo.
- No se registra el correo, IP, pregunta o identidad del visitante. No se sabe
  si es un juez. Un bot que ejecute la página también puede activar la espera.

## Prueba real después de configurar

Cuando el worker esté desconectado, abre la web en una pestaña nueva, sin
pulsar Run. Tras unos 20 segundos, Resend debería registrar el mensaje en
https://resend.com/emails. La web reflejará el estado en su siguiente consulta.
Revisa tu bandeja de entrada y spam. El remitente de prueba puede aparecer
como `onboarding@resend.dev`.

Mantén una pestaña abierta: después del primer aviso deben solicitarse nuevos
envíos cada 30 segundos, sujetos a la cuota de Resend. Abre otra pestaña: no
debe multiplicar los avisos. Después conecta el notebook: debe desaparecer
Connecting, detenerse el envío y habilitarse Run. Si cierras todas las pestañas,
los avisos cesan cuando expira el margen de presencia de 60 segundos.

Si no llega:

- Comprueba que `GPU_ALERT_TO` coincide exactamente con tu cuenta de Resend.
- En Render → Logs, busca `GPU_VISIT_ALERT`. Un fallo muestra solo un código,
  sin revelar claves ni direcciones. Resend → Emails permite comprobar los
  mensajes aceptados y su entrega.
- Código 401: clave inválida. Código 403: revisa permisos, dominio y el
  destinatario permitido para `resend.dev`. Código 429: límite de envío.
- Verifica que las variables se han guardado y la nueva revisión está desplegada.
- Si el worker ya está conectado, no debe llegar otro aviso. Si Render está
  suspendido o no llega a cargar la aplicación, este código no puede avisarte.

## Coste y límites

Resend publica un plan Free de **3.000 correos/mes y 100/día**. Un correo cada
30 segundos son **120 por hora**: la cuota diaria se agota en unos **50 minutos
de espera acumulada**, o antes si tu cuenta envía otros correos. Al agotarse,
Resend rechaza los nuevos envíos. La cuota diaria se renueva a medianoche UTC.
La rueda continúa esperando la GPU aunque el correo no pueda enviarse.

Esta versión respeta el intervalo de 30 segundos solicitado; no lo aumenta
silenciosamente. Mantén el plan Free y no actives opciones de pago. El código
no contrata recursos, no cambia tu plan ni compra créditos GPU.

Render gratuito bloquea los puertos SMTP habituales. Esta versión usa la API
HTTPS de Resend y no añade paquetes Python. Render puede tardar en despertar;
la comprobación comienza cuando la aplicación ya puede atender peticiones.

**El aviso resuelve la notificación, no la disponibilidad automática.** Si
estás ausente, el juez tendrá que esperar a que reactives AMD. Para arrancar
una GPU sin tu intervención sigue haciendo falta acceso autorizado a una
API de provisión o una GPU que permanezca disponible.

Variables opcionales:

| Variable | Valor predeterminado |
| --- | --- |
| `GPU_ALERT_FROM` | `AmdQuant <onboarding@resend.dev>` |
| `GPU_ALERT_SITE_URL` | `https://amdquant.onrender.com` |

Si cambias de URL pública, configura `GPU_ALERT_SITE_URL` con tu nueva URL
HTTPS. Para desactivar los avisos, elimina `RESEND_API_KEY` de Render.

## Verificación de esta entrega

Pruebas locales con transporte de correo simulado: concurrencia, deduplicación,
intervalos de 30 segundos, caducidad de presencia, fallos y reintentos,
reconexión durante la espera, protección del destinatario,
modo privado y ausencia de avisos en health checks. La interfaz se verifica
con fixtures, incluida la entrega independiente de resultados y los cuatro
idiomas. No se han realizado envíos reales ni benchmarks GPU en esta revisión.

Fuentes oficiales consultadas el 16 de octubre de 2026:

- https://render.com/docs/free
- https://resend.com/pricing
- https://resend.com/docs/api-reference/errors
- https://resend.com/docs/knowledge-base/403-error-resend-dev-domain
- https://resend.com/docs/dashboard/emails/idempotency-keys
- https://resend.com/docs/api-reference/emails/send-email
