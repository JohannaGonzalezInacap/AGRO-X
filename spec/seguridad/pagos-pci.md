# Pagos y PCI DSS

Estado: Propuesta. Versión vigente de la norma: PCI DSS v4.0.1.

## Decisión

Pago por redirección a la página de la pasarela (ver ADR-003). Con eso el proyecto apunta al
cuestionario de autoevaluación más liviano, el SAQ A. Qué cuestionario aplica lo confirma la
pasarela o el adquirente, no el equipo.

## Reglas

1. Ninguna ruta acepta número de tarjeta, vencimiento ni código de seguridad.
2. Esos datos no se guardan en base de datos, registros, pruebas ni capturas de pantalla.
3. De un pago solo se guarda: plan, monto, moneda, estado, referencia propia e identificador que
   entrega la pasarela.
4. Las claves de la pasarela viven en el gestor de secretos.
5. El webhook verifica firma, descarta repetidos y confirma el pago consultando a la pasarela.
6. La aplicación cliente que lleva a la página de pago debe evitar scripts de terceros innecesarios,
   porque el SAQ A exige que el sitio no sea vulnerable a scripts que afecten el pago.
7. La cuenta de la pasarela usa segundo factor.

## Pendiente antes de producción

- [ ] Confirmar con la pasarela qué cuestionario corresponde.
- [ ] Revisar la documentación vigente de la pasarela: formato de firma del webhook y rutas.
- [ ] Probar en modo de pruebas: aprobado, rechazado, aviso repetido, firma inválida.
