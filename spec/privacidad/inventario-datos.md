# Inventario de datos personales

Estado: Propuesta. Actualizar antes de agregar cualquier dato personal nuevo. Las bases de licitud
son una propuesta y deben validarse con el área legal.

| Dato | De quién | Para qué | Base propuesta | Quién lo ve | Sale a terceros | Retención |
|---|---|---|---|---|---|---|
| Correo | Todo usuario | Identificar la cuenta, avisos | Ejecución del servicio | El titular, administrador | Pasarela (al pagar) | Mientras exista la cuenta |
| Contraseña (solo hash) | Todo usuario | Autenticación | Ejecución del servicio | Nadie | No | Mientras exista la cuenta |
| Nombre | Todo usuario | Identificación | Ejecución del servicio | El titular, administrador | No | Mientras exista la cuenta |
| Rol y plan | Todo usuario | Control de acceso | Ejecución del servicio | El titular, administrador | No | Mientras exista la cuenta |
| Ubicación de la parcela | Productor | Clima, alertas, rotación | Ejecución del servicio | El titular | Redondeada, a fuentes de clima | Mientras exista la parcela |
| Datos de suelo y cultivos (incluye tipo de cultivo, fecha de plantación y etapa actual) | Productor | Rotación y alertas | Ejecución del servicio | El titular | No | Mientras exista la parcela |
| Nombre del negocio, región, contacto | Comerciante | Aparecer en el listado | Consentimiento | Productores pro | No | Hasta retirar consentimiento |
| Contacto en una merma | Productor | Que lo contacten por esa merma | Consentimiento | Comerciantes | No | Mientras la merma esté activa |
| Historial de pagos | Quien paga | Activar plan, respaldo contable | Obligación legal y servicio | El titular, administrador | Pasarela | Según exigencia tributaria (por confirmar) |
| Tokens de sesión (hash) | Todo usuario | Mantener la sesión | Ejecución del servicio | Nadie | No | Hasta vencer o revocar |
| Auditoría (usuario, acción, fecha) | Todo usuario | Seguridad | Interés legítimo | Administrador | No | 12 meses (por confirmar) |
| Consentimiento de comunicaciones promocionales (otorgado, versión, fecha) | Todo usuario | Saber si puede recibírselas | Consentimiento | El titular, administrador | No | Hasta retirarlo o eliminar la cuenta |

## Datos que no se recolectan

Tarjetas de pago, documento de identidad, fecha de nacimiento, datos sensibles.

## Principios

1. Pedir solo lo necesario.
2. La ubicación exacta no sale de la plataforma.
3. Los contactos se publican solo con consentimiento y se pueden retirar.
