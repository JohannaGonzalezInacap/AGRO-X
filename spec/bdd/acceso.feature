# language: es
Característica: Cuentas y acceso

  Escenario: Registro como productor
    Cuando me registro con correo, nombre, contraseña de 12 o más caracteres y rol "producer"
    Entonces recibo 201 con mi perfil
    Y la respuesta no incluye la contraseña

  Escenario: No se puede registrar como administrador
    Cuando me registro con rol "admin"
    Entonces recibo 422

  Escenario: No se pueden enviar campos extra
    Cuando me registro agregando el campo "plan" con valor "pro"
    Entonces recibo 422

  Escenario: Inicio de sesión correcto
    Dado que tengo una cuenta
    Cuando inicio sesión con mis datos
    Entonces recibo un token de acceso y uno de renovación

  Esquema del escenario: Inicio de sesión fallido no revela si la cuenta existe
    Cuando inicio sesión con <caso>
    Entonces recibo 401 con código "invalid_credentials"

    Ejemplos:
      | caso                         |
      | un correo que no existe      |
      | una contraseña incorrecta    |

  Escenario: El token de renovación sirve una sola vez
    Dado que renové mi sesión con un token
    Cuando vuelvo a usar ese mismo token
    Entonces recibo 401
    Y el token nuevo que obtuve también queda revocado

  Escenario: Sin token no hay acceso
    Cuando pido mi perfil sin token
    Entonces recibo 401

  # El escenario de ownership de parcelas vive en spec/bdd/farms.feature (Fase 3).

  Escenario: Límite de intentos
    Cuando intento iniciar sesión más veces que el límite por minuto
    Entonces recibo 429
