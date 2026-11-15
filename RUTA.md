# RUTA — Fases del proyecto

Se avanza en orden. Una fase empieza solo cuando la anterior cumple la definición de "terminado"
de `CLAUDE.md`.

**Mínimo para la hackathon:** fases 0 a 6, más la 7 con la pasarela simulada. Las fases 8 a 10 son
deseables si queda tiempo.

## Texto base para pedir una fase a Claude Code

Copia esto y cambia el número y el nombre de la fase:

```
Lee CLAUDE.md, RUTA.md y los documentos de spec/ que indica la Fase N.
Vamos a hacer la Fase N: <nombre>.
1. Primero muéstrame el plan: qué archivos vas a crear o cambiar y por qué. Si algo en spec/ falta
   o es ambiguo, dímelo antes y propón el cambio. Espera mi OK.
2. Luego implementa solo esa fase, con sus pruebas.
3. Al terminar, corre las pruebas, muéstrame el resultado, explícame paso a paso cómo probarlo yo
   y actualiza DIARIO-DE-PROYECTO.md y CHANGELOG.md.
```

## Fase 0 — Preparación (la hace el equipo, sin programar)

| Tarea | Listo cuando |
|---|---|
| Leer `spec/alcance-y-planes.md` y los ADR | El equipo los aprueba o anota cambios; cada ADR pasa de "Propuesta" a "Aceptada" |
| Elegir el nombre definitivo | Está anotado en el diario |
| Probar los datos de la NASA con una llamada real | La URL de `spec/contratos/fuentes-datos.md` devuelve datos en el navegador |
| Elegir la fuente de pronóstico | ADR-005 actualizado, con la licencia revisada |
| Crear cuenta de pruebas en la pasarela de pago | Hay credenciales de prueba guardadas fuera del repositorio |
| Elegir la nube y crear la cuenta | ADR-004 aceptado |
| Repartir responsabilidades | `spec/gobierno/objetivos-y-raci.md` con nombres |

## Fase 1 — Esqueleto del proyecto

- **Lee:** ADR-001, `spec/nfr.md`, `spec/contratos/api-v1.md` (formato de error), `spec/seguridad/`.
- **Entrega:** dependencias fijadas, `app/main.py` con `/healthz`, configuración por variables de
  entorno, formato único de error, cabeceras de seguridad, límite de tamaño, CORS con lista cerrada,
  primera prueba, revisión automática en `.github/workflows/`, sección "Comandos" de `CLAUDE.md`.
- **Listo cuando:** la API arranca en local, `/healthz` responde y `pytest` pasa.

## Fase 2 — Cuentas y acceso

- **Lee:** ADR-002, `spec/bdd/acceso.feature`, `spec/seguridad/controles-aplicables.md`.
- **Entrega:** registro, inicio de sesión, renovación y cierre de sesión, perfil propio, roles,
  límite de intentos, registro de auditoría, primera migración.
- **Listo cuando:** pasan todos los escenarios de `acceso.feature`.

## Fase 3 — Parcelas e historial de cultivos

- **Lee:** `spec/dominio.md`, `spec/privacidad/inventario-datos.md`.
- **Entrega:** crear, ver, editar y borrar parcelas; historial de cultivos; tope de parcelas por plan.
- **Listo cuando:** hay una prueba que demuestra que un usuario no puede ver la parcela de otro.

## Fase 4 — Fuentes de datos

- **Lee:** ADR-005, `spec/contratos/fuentes-datos.md`, `spec/gobierno/proveedores.md`.
- **Entrega:** cliente de NASA POWER, cliente de pronóstico, caché, tiempos de espera, manejo de
  datos faltantes, coordenadas redondeadas.
- **Listo cuando:** las pruebas pasan con respuestas simuladas y Joha comprobó una llamada real.

## Fase 5 — Rotación de cultivos (núcleo del reto)

- **Lee:** `spec/dominio.md`, `spec/bdd/rotacion.feature`.
- **Entrega:** catálogo de cultivos, motor de recomendación con puntaje y razones explicadas,
  prioridades del agricultor (agua, suelo, ingreso).
- **Listo cuando:** pasan los escenarios de `rotacion.feature` y cada recomendación dice por qué.
- **Ojo:** los valores agronómicos del catálogo deben tener fuente. Sin fuente, se marcan como
  "ilustrativo" en la respuesta.

## Fase 6 — Alertas y control por plan

- **Lee:** `spec/alcance-y-planes.md`, `spec/bdd/alertas.feature`.
- **Entrega:** motor de riesgo (helada, calor, lluvia intensa, sequía), frecuencia y nivel de
  detalle según plan, tarea programada de recálculo.
- **Listo cuando:** pasan los escenarios de `alertas.feature`.

## Fase 7 — Planes y pagos

- **Lee:** ADR-003, ADR-006, `spec/bdd/pagos.feature`, `spec/seguridad/pagos-pci.md`.
- **Entrega:** catálogo de planes, inicio de pago, webhook verificado, pasarela simulada para
  desarrollo y adaptador de la pasarela real en modo de pruebas.
- **Listo cuando:** pasan los escenarios de `pagos.feature`, incluidos firma falsa y aviso repetido.

## Fase 8 — Comerciantes, mermas y promociones

- **Lee:** `spec/alcance-y-planes.md`, `spec/privacidad/inventario-datos.md`.
- **Entrega:** perfil de comerciante, listado para plan pro, publicación de mermas, ideas de
  promoción según la alerta activa.
- **Listo cuando:** un productor free recibe rechazo y uno pro accede.

## Fase 9 — Privacidad y observabilidad

- **Lee:** `spec/privacidad/`, `spec/mejora-continua/indicadores.md`.
- **Entrega:** consentimientos, descargar mis datos, eliminar mi cuenta, registros sin datos
  personales, métricas para los indicadores.
- **Listo cuando:** al eliminar una cuenta no queda dato personal, y hay prueba de ello.

## Fase 10 — Despliegue y demo

- **Lee:** ADR-004, `spec/servicio/`, `spec/gobierno/matriz-cumplimiento.md`.
- **Entrega:** imagen de contenedor sin usuario root, secretos en el gestor de la nube, base de
  datos administrada, despliegue, respaldo probado, guion de demo.
- **Listo cuando:** la demo corre de punta a punta en la nube y la matriz de cumplimiento está
  actualizada con lo que sí y lo que no se cumple.

## Después de cada fase

Agrega al menos una línea en `spec/mejora-continua/registro-mejoras.md`: qué salió mal o lento y
qué se cambiará.
