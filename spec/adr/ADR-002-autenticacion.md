# ADR-002 — Autenticación y sesiones

- Estado: Aceptada
- Fecha: 2026-11-14

## Contexto
La API la consumirán aplicaciones cliente. Hay que identificar a la persona, su rol y su plan sin
guardar contraseñas legibles y limitando el daño si se roba un token.

## Decisión
- Contraseñas con Argon2id. Mínimo 12 caracteres.
- Token de acceso JWT de 15 minutos, con algoritmo fijo, emisor y audiencia verificados.
- Token de renovación opaco, de un solo uso, guardado solo como hash. Si llega uno ya usado, se
  revoca toda la cadena de esa sesión.
- El plan no viaja en el token: se lee de la base de datos en cada solicitud.
- Roles: productor, comerciante, administrador. El administrador no se puede autoasignar.
- El mismo mensaje de error si el correo no existe o la contraseña es incorrecta.
- Límite de intentos por IP en registro e inicio de sesión.

## Alternativas consideradas
- Servicio de identidad administrado (de la nube): más seguro a largo plazo, pero agrega
  configuración y dependencia. Queda como mejora futura.
- Sesiones con cookie: más simple en web, menos práctico para aplicaciones móviles.

## Consecuencias
- Un token de acceso robado sirve como máximo 15 minutos.
- Segundo factor de autenticación queda diferido.
- Con varias instancias, el límite de intentos necesita un almacén compartido o delegarse al
  firewall de la nube.

## Implementación (Fase 2)
- Límite de intentos: contador en memoria por proceso, por IP y por acción (registro o login),
  ventana deslizante configurable (`LOGIN_RATE_LIMIT_ATTEMPTS`, `LOGIN_RATE_LIMIT_WINDOW_SECONDS`).
  Limitación conocida: con varias instancias cada una cuenta por su cuenta (ver Consecuencias
  arriba). Aceptable para el alcance de la hackathon; se revisa en la Fase 10 si el despliegue usa
  más de una instancia.
- El token de renovación se guarda solo como hash (SHA-256) con una `family_id` que agrupa toda la
  cadena de una sesión; reutilizar un token ya usado revoca la familia completa.
