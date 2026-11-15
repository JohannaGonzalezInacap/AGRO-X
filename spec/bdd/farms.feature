# language: es
Característica: Parcelas e historial de cultivos

  Escenario: Crear una parcela
    Dado que soy productora
    Cuando registro una parcela con nombre, región, coordenadas y hectáreas
    Entonces recibo 201 con los datos de la parcela

  Esquema del escenario: Tope de parcelas según el plan
    Dado que tengo plan "<plan>" y ya tengo <tope> parcelas registradas
    Cuando intento registrar una parcela más
    Entonces recibo 403 con código "plan_required"

    Ejemplos:
      | plan   | tope |
      | free   | 1    |
      | basico | 3    |
      | pro    | 20   |

  Escenario: Un usuario no ve la parcela de otro
    Dado que la productora A tiene una parcela
    Cuando el productor B pide esa parcela por su identificador
    Entonces recibo 404

  Escenario: Un comerciante no puede crear parcelas
    Dado que soy comerciante
    Cuando intento registrar una parcela
    Entonces recibo 403 con código "forbidden"

  Escenario: Registrar un cultivo nuevo vuelve no vigente al anterior
    Dado que mi parcela tiene un cultivo vigente
    Cuando registro un cultivo nuevo para la temporada
    Entonces el cultivo anterior queda con "vigente" en falso
    Y el cultivo nuevo queda con "vigente" en verdadero

  Escenario: Cambiar solo la etapa no crea un historial nuevo
    Dado que mi parcela tiene un cultivo vigente en etapa "floracion"
    Cuando cambio la etapa del cultivo vigente a "fruto"
    Entonces sigue existiendo un solo registro de historial para esa temporada
    Y su etapa ahora es "fruto"

  Escenario: Borrar una parcela borra su historial
    Dado que mi parcela tiene historial de cultivos
    Cuando borro la parcela
    Entonces ya no puedo pedir su historial
