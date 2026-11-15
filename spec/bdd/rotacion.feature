# language: es
Característica: Recomendación de rotación de cultivos

  Antecedentes:
    Dado que soy productora con una parcela registrada

  Escenario: Después de un cultivo exigente se sugiere una leguminosa
    Dado que el último cultivo de la parcela fue maíz
    Cuando pido recomendaciones de rotación
    Entonces una leguminosa aparece mejor puntuada que el maíz
    Y la razón menciona la reposición de nitrógeno

  Escenario: Se evita repetir la misma familia
    Dado que los dos últimos cultivos fueron de la misma familia
    Cuando pido recomendaciones de rotación
    Entonces los cultivos de esa familia bajan de puntaje
    Y la razón menciona plagas y enfermedades

  Escenario: Con poca agua se prefieren cultivos de baja demanda
    Dado que la parcela no tiene riego y la zona es de baja precipitación
    Y que mi prioridad más alta es ahorrar agua
    Cuando pido recomendaciones de rotación
    Entonces los cultivos de alta demanda de agua bajan de puntaje

  Escenario: Toda recomendación explica sus razones
    Cuando pido recomendaciones de rotación
    Entonces cada cultivo sugerido trae al menos una razón
    Y la respuesta indica qué fuentes de datos se usaron

  Escenario: Sin historial igual hay respuesta
    Dado que la parcela no tiene historial de cultivos
    Cuando pido recomendaciones de rotación
    Entonces recibo recomendaciones basadas en clima y suelo
    Y la respuesta avisa que falta el historial

  Escenario: Valores sin fuente se marcan
    Dado que un dato del catálogo no tiene fuente agronómica
    Cuando ese dato influye en una recomendación
    Entonces la respuesta lo marca como ilustrativo
