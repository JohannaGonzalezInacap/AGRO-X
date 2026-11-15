# ADR-004 — Nube y despliegue

- Estado: Reemplazada por ADR-015
- Fecha: 2026-11-14

**2026-11-15:** al llegar a la Fase 10, el proyecto de GCP no tenía facturación activa (ninguna
cuenta de facturación de Joha estaba abierta) y no había tiempo para resolverlo antes de la
entrega. Se desplegó en Render en su lugar — ver ADR-015. Esta decisión queda registrada tal como
se propuso, por trazabilidad, pero ya no es la que se sigue.

## Contexto
Se necesita desplegar barato, rápido y con seguridad razonable. Las tres nubes grandes tienen
región en Chile.

## Decisión
Google Cloud: Cloud Run para la API, PostgreSQL administrado, Secret Manager para secretos, Cloud
Scheduler para tareas programadas.

## Por qué
- Se despliega con un contenedor y baja a cero cuando nadie la usa.
- Capa gratuita mensual que cubre una demo.
- Región en Santiago.

## Alternativas consideradas

| Necesidad | AWS | Azure |
|---|---|---|
| Cómputo | Lambda con API Gateway, o ECS Express Mode | Container Apps |
| Secretos | Secrets Manager | Key Vault |
| Firewall web | WAF | Front Door WAF |
| Tareas programadas | EventBridge | Container Apps Jobs |

App Runner de AWS no acepta cuentas nuevas desde el 30 de abril de 2026.

## Consecuencias
- El costo real es la base de datos (estimación sin verificar: 10 a 15 dólares al mes la más
  pequeña). Para la hackathon se puede usar una capa gratuita de un proveedor externo.
- La capa gratuita de Cloud Run depende de la región; confirmar en la calculadora antes de elegir
  Santiago.
- Como la API corre en contenedor, cambiar de nube no obliga a reescribir código.
