# Modelo de amenazas

Estado: Propuesta. Se revisa al cerrar cada fase.

## Qué protegemos

| Activo | Por qué importa |
|---|---|
| Cuentas y contraseñas | Suplantación de identidad |
| Ubicación de parcelas | Dato personal y comercial sensible del productor |
| Contactos de comerciantes y productores | Dato personal |
| Estado del plan y pagos | Dinero y confianza |
| Secretos (claves de firma, de la pasarela, de la base de datos) | Dan control total |

## Por dónde entra y sale información

```
Aplicación cliente ──HTTPS──> API ──> Base de datos
                               │
                               ├──HTTPS──> NASA y fuente de pronóstico (solo coordenadas redondeadas)
                               └──HTTPS<─> Pasarela de pago (inicio de pago y webhook)
```

## Amenazas y controles

| # | Amenaza | Control | Fase |
|---|---|---|---|
| 1 | Robo de contraseñas desde la base de datos | Argon2id | 2 |
| 2 | Adivinar contraseñas por fuerza bruta | Límite de intentos, contraseña mínima de 12 | 2 |
| 3 | Averiguar qué correos están registrados | Mismo error para correo inexistente y contraseña errada | 2 |
| 4 | Robo de token | Acceso de 15 minutos; renovación de un solo uso con revocación en cadena | 2 |
| 5 | Ver o modificar datos de otro usuario | Filtro por dueño en toda consulta; identificadores UUID; respuesta 404 | 3 |
| 6 | Subirse de rol o de plan enviando campos extra | Entrada estricta; rol y plan los fija el servidor | 2, 7 |
| 7 | Webhook de pago falso o repetido | Firma, registro de avisos vistos, confirmación con la pasarela, verificación de monto | 7 |
| 8 | Exposición de datos de tarjeta | Pago por redirección; ninguna ruta acepta tarjetas | 7 |
| 9 | Usar la API para llamar a direcciones internas | Direcciones externas fijas en configuración | 4 |
| 10 | Inyección en base de datos | Consultas parametrizadas por el ORM; sin SQL armado con texto | 1 |
| 11 | Filtración por mensajes de error o registros | Error único sin trazas; registros sin datos personales | 1, 9 |
| 12 | Secretos en el repositorio | Variables de entorno, `.gitignore`, gestor de secretos, escaneo en revisión automática | 1, 10 |
| 13 | Dependencia vulnerable | Versiones fijadas y escaneo automático | 1 |
| 14 | Saturación del servicio | Límite de tamaño de cuerpo, límite de solicitudes, caché de fuentes externas | 1, 4 |
| 15 | Sitio malicioso usando la sesión del usuario | CORS con lista cerrada; token en cabecera, no en cookie | 1 |
| 16 | Arranque en producción con valores de prueba | La app se niega a arrancar si detecta secretos de desarrollo | 1 |
| 17 | Raspado masivo de contactos del listado | Solo plan pro, paginación y límite de solicitudes | 8 |
| 18 | Acceso indebido del propio equipo | Mínimo privilegio en la nube y auditoría | 10 |

## Riesgos aceptados por ahora

- Sin segundo factor de autenticación.
- El registro revela si un correo ya existe (409). Se mitiga con el límite de intentos.
- Sin pruebas de penetración externas.
