# language: es
Característica: Planes y pagos

  Escenario: Iniciar un pago
    Dado que tengo sesión iniciada
    Cuando inicio el pago del plan "basic"
    Entonces recibo una dirección de la pasarela para pagar
    Y mi plan sigue siendo el anterior

  Escenario: El plan no se puede cambiar desde el cliente
    Cuando envío una solicitud que intenta fijar mi plan en "pro"
    Entonces mi plan no cambia

  Escenario: Pago aprobado activa el plan
    Dado que inicié el pago del plan "pro"
    Cuando llega un aviso con firma válida y la pasarela confirma el pago aprobado por el monto correcto
    Entonces mi plan pasa a "pro" con vigencia de 30 días

  Escenario: Aviso con firma falsa
    Cuando llega un aviso con firma inválida
    Entonces la API responde 401
    Y ningún plan cambia

  Escenario: Aviso repetido
    Dado que un aviso ya fue procesado
    Cuando llega el mismo aviso otra vez
    Entonces la API responde 200
    Y la vigencia del plan no se extiende de nuevo

  Escenario: Monto distinto al esperado
    Cuando llega un aviso válido pero la pasarela informa un monto menor al del plan
    Entonces el plan no se activa
    Y queda registrado en auditoría

  Escenario: Pago rechazado
    Cuando la pasarela informa el pago como rechazado
    Entonces el plan no cambia

  Escenario: Ningún dato de tarjeta entra a la API
    Entonces ninguna ruta acepta número de tarjeta, vencimiento ni código de seguridad
