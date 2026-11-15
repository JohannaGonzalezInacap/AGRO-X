# Dominio

Estado: Propuesta.

## Conceptos

| Concepto | Qué es | Datos principales |
|---|---|---|
| Usuario | Persona con cuenta | correo, nombre, rol, plan, vigencia del plan |
| Rol | Perfil del usuario | productor, comerciante, transportista (futuro), administrador |
| Plan | Nivel de servicio contratado | free, básico, pro |
| Parcela | Terreno de un productor | nombre, ubicación, región, superficie (hectáreas), textura de suelo, drenaje, materia orgánica, riego |
| Historial de cultivo | Qué se sembró, cuándo y en qué etapa está ahora | cultivo, temporada, fecha de plantación, etapa actual, vigente (sí/no) |
| Cultivo (catálogo) | Ficha agronómica | familia, necesidad de agua, efecto sobre nitrógeno, profundidad de raíz, tolerancia a helada y calor |
| Recomendación de rotación | Cultivos sugeridos para la próxima temporada | cultivo, puntaje, razones |
| Alerta | Riesgo climático para una parcela | tipo, gravedad, fecha esperada, detalle, recomendaciones |
| Idea de promoción | Sugerencia de venta ante una alerta | texto, cultivo, urgencia |
| Perfil de comerciante | Datos del negocio comprador | nombre, región, productos de interés, contacto |
| Merma | Producto no apto para venta normal, ofrecido para otro uso | producto, kilos, precio, región, uso (alimento animal), estado |
| Pago | Intento de compra de un plan | plan, monto, moneda, estado, referencia |
| Consentimiento | Permiso puntual que el usuario da o retira (ADR-014) | tipo, otorgado (sí/no), versión del texto aceptado, fecha |

## Reglas

1. Una parcela pertenece a un solo productor. Solo él y un administrador pueden verla.
2. El rol se elige al registrarse entre productor y comerciante. Administrador nunca se autoasigna.
3. Un plan vencido se comporta como free.
4. El plan solo cambia cuando la pasarela confirma el pago.
5. Una recomendación de rotación siempre explica sus razones.
6. Una alerta se calcula con dos insumos: lo observado (NASA) y lo pronosticado (otra fuente).
7. Una merma solo muestra el contacto que el productor decidió publicar en ella.
8. Tipos de alerta iniciales: helada, calor extremo, lluvia intensa, sequía.
9. El registro de cuenta (correo, contraseña, rol) no incluye datos de parcela ni de cultivo. Una
   parcela y su cultivo se crean en un paso aparte, después de registrarse.
10. Una parcela tiene como máximo **un** historial de cultivo vigente a la vez (el de la temporada
    actual). Las alertas y las recomendaciones de rotación usan siempre el cultivo vigente.
11. Al registrar un cultivo nuevo para una parcela, el anterior deja de estar vigente (no se borra,
    queda como historial).
12. La "vida de la planta" se guarda como fecha de plantación, no como un número de años fijo, para
    que la edad se calcule sola y no quede desactualizada.
13. Etapa actual de la planta: catálogo cerrado, **Ilustrativo** hasta que el equipo lo valide con
    una fuente agronómica: `recien_plantada`, `crecimiento`, `floracion`, `fruto`, `cosecha`. Puede
    variar según el tipo de cultivo (anual o perenne); se ajusta en la Fase 3 si hace falta.

## Relaciones

```
Usuario 1 ── N Parcela 1 ── N Historial de cultivo
                   │
                   ├── N Alerta
                   └── N Recomendación de rotación  (usa Catálogo de cultivos)
Usuario (comerciante) 1 ── 1 Perfil de comerciante
Usuario (productor)   1 ── N Merma
Usuario 1 ── N Pago
Usuario 1 ── N Consentimiento
```
