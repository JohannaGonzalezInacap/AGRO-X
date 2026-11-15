# language: es
Característica: Ideas de venta urgente ante una alerta de riesgo alto

  # ADR-013: nace de aclarar el alcance de "ideas de promoción" (en pausa desde la Fase 8 original).
  # No es un motor de marketing general: solo sugiere vender cuando hay un riesgo real e inminente
  # de perder la cosecha (alerta activa de severidad "alta"). No depende del marketplace de mermas
  # (ND-002), que quedó en pausa por separado.

  Escenario: Hay ideas de venta si hay una alerta de severidad alta
    Dado que tengo plan básico y la parcela tiene una alerta activa de severidad "alta"
    Cuando pido las ideas de venta urgente
    Entonces recibo ideas de venta para esa alerta

  Escenario: No hay ideas de venta sin una alerta de severidad alta
    Dado que tengo plan pro y la parcela solo tiene alertas de severidad "media"
    Cuando pido las ideas de venta urgente
    Entonces recibo 404 con código "not_found"

  Escenario: Plan free no accede a las ideas de venta
    Dado que tengo plan free y la parcela tiene una alerta activa de severidad "alta"
    Cuando pido las ideas de venta urgente
    Entonces recibo 403 con código "plan_required"

  Escenario: Plan vencido se comporta como free
    Dado que mi plan pro venció ayer y la parcela tiene una alerta activa de severidad "alta"
    Cuando pido las ideas de venta urgente
    Entonces recibo 403 con código "plan_required"
