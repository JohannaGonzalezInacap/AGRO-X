# language: es
Característica: Alertas de riesgo climático por parcela

  # Alerta de cambio de cultivo (ADR-008): no es climática, se dispara por etapa del cultivo.

  Escenario: Helada pronosticada
    Dado que el pronóstico trae una mínima bajo el umbral del cultivo en los próximos días
    Cuando se recalculan las alertas de la parcela
    Entonces se crea una alerta de tipo "frost" con la fecha esperada

  Escenario: Sequía según lo observado y lo pronosticado
    Dado que la humedad de suelo observada es baja
    Y que no se pronostica lluvia relevante en 7 días
    Cuando se recalculan las alertas
    Entonces se crea una alerta de tipo "drought"

  Escenario: Plan free ve solo el resumen
    Dado que tengo plan free y la parcela tiene una alerta
    Cuando pido las alertas
    Entonces veo tipo, gravedad y título
    Y no veo detalle ni recomendaciones

  Escenario: Plan básico ve el detalle por parcela
    Dado que tengo plan básico y la parcela tiene una alerta
    Cuando pido las alertas
    Entonces veo además el detalle y las recomendaciones

  Escenario: Plan free actualiza una vez cada 30 días
    Dado que tengo plan free y recalculé alertas hoy
    Cuando intento recalcular de nuevo
    Entonces recibo 429 con código "too_soon" y la fecha en que podré hacerlo

  # Diferido a la Fase 8: depende de GET /farms/{id}/promotions/ideas, que no existe todavía.
  @diferido-fase-8
  Escenario: Plan vencido se comporta como free
    Dado que mi plan pro venció ayer
    Cuando pido las ideas de promoción
    Entonces recibo 403 con código "plan_required"

  Escenario: Falla la fuente externa
    Dado que la fuente de datos no responde
    Cuando se recalculan las alertas
    Entonces recibo 502 con código "upstream_unavailable"
    Y las alertas anteriores siguen disponibles

  Escenario: Dato faltante no se toma como número
    Dado que la fuente entrega un valor de relleno para un día
    Cuando se recalculan las alertas
    Entonces ese día se ignora en el cálculo

  Escenario: Plan free no recibe alerta de cambio de cultivo
    Dado que tengo plan free y mi cultivo vigente llegó a la etapa "cosecha"
    Cuando se recalculan las alertas de la parcela
    Entonces no se crea una alerta de tipo "cambio_de_cultivo"

  Escenario: Plan básico recibe el aviso sin sugerencia de cultivo
    Dado que tengo plan básico y mi cultivo vigente llegó a la etapa "cosecha"
    Cuando se recalculan las alertas de la parcela
    Entonces se crea una alerta de tipo "cambio_de_cultivo"
    Y no incluye una sugerencia de cultivo

  Escenario: Plan pro recibe el aviso con sugerencia de cultivo
    Dado que tengo plan pro y mi cultivo vigente llegó a la etapa "cosecha"
    Cuando se recalculan las alertas de la parcela
    Entonces se crea una alerta de tipo "cambio_de_cultivo"
    Y incluye la primera sugerencia del motor de rotación con sus razones

  Escenario: Plan pro sin recomendación disponible
    Dado que tengo plan pro, mi cultivo vigente llegó a la etapa "cosecha" y el motor de rotación
      no tiene datos suficientes para recomendar
    Cuando se recalculan las alertas de la parcela
    Entonces se crea una alerta de tipo "cambio_de_cultivo" sin sugerencia de cultivo
