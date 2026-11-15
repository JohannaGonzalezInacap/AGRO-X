# language: es
Característica: Privacidad — exportar datos, eliminar cuenta y consentimientos

  # ADR-014: alcance de los derechos de la Fase 9. ND-003: los consentimientos aquí solo cubren
  # "comunicaciones promocionales"; los otros dos de la spec original los gobierna el propio
  # marketplace (perfil de comerciante, contacto de una merma), no se duplican aquí.

  Escenario: Exportar mis datos entrega mi información
    Dado que tengo una parcela con historial de cultivo
    Cuando pido la exportación de mis datos
    Entonces recibo mi perfil y mi parcela con su historial

  Escenario: La exportación no incluye contraseñas ni tokens
    Cuando pido la exportación de mis datos
    Entonces la respuesta no contiene ningún hash de contraseña ni de token

  Escenario: Ver mis consentimientos antes de decidir nada
    Cuando pido mis consentimientos
    Entonces "comunicaciones_promocionales" aparece sin otorgar

  Escenario: Otorgar el consentimiento de comunicaciones
    Cuando otorgo el consentimiento de comunicaciones promocionales
    Entonces queda otorgado con fecha y versión

  Escenario: Retirarlo es tan fácil como darlo
    Dado que otorgué el consentimiento de comunicaciones promocionales
    Cuando lo retiro
    Entonces queda sin otorgar

  Escenario: Eliminar mi cuenta borra mis datos de las tablas activas
    Dado que tengo una parcela con historial de cultivo y alertas
    Cuando elimino mi cuenta
    Entonces ya no puedo iniciar sesión
    Y no queda ninguna parcela, historial ni alerta con mi identificador

  Escenario: Eliminar mi cuenta anonimiza mis pagos, no los borra
    Dado que tengo un pago registrado
    Cuando elimino mi cuenta
    Entonces el pago sigue existiendo pero sin vínculo con mi cuenta
