# language: es
Característica: Comerciantes y mermas

  Escenario: Un comerciante crea o actualiza su perfil
    Dado que soy comerciante
    Cuando guardo mi perfil con nombre, región y productos de interés
    Entonces recibo 200 con mi perfil

  Escenario: Un productor no puede tener perfil de comerciante
    Dado que soy productor
    Cuando intento guardar un perfil de comerciante
    Entonces recibo 403 con código "forbidden"

  Escenario: Productor pro lista comerciantes
    Dado que tengo plan pro y soy productor
    Cuando pido el listado de comerciantes
    Entonces recibo la lista

  Escenario: Productor free no puede listar comerciantes
    Dado que tengo plan free y soy productor
    Cuando pido el listado de comerciantes
    Entonces recibo 403 con código "plan_required"

  Escenario: Productor pro publica una merma
    Dado que tengo plan pro y soy productor
    Cuando publico una merma con producto, kilos, precio, región y uso
    Entonces recibo 201 con la merma

  Escenario: Productor free no puede publicar mermas
    Dado que tengo plan free y soy productor
    Cuando intento publicar una merma
    Entonces recibo 403 con código "plan_required"

  Escenario: El contacto de una merma solo se publica si el productor lo decide
    Dado que publiqué una merma sin marcar que se publique el contacto
    Cuando un comerciante pro la consulta
    Entonces no ve ningún contacto

  Escenario: Comerciante pro ve el contacto si el productor lo publicó
    Dado que publiqué una merma marcando que se publique el contacto
    Cuando un comerciante pro la consulta
    Entonces ve el contacto

  # ND-001 (spec/alcance-y-planes.md): el comerciante también paga plan para las funciones pro.
  Escenario: Comerciante free ve el listado pero no el contacto
    Dado que publiqué una merma marcando que se publique el contacto
    Cuando un comerciante free la consulta
    Entonces ve la merma pero no ve el contacto

  Escenario: Solo el dueño cambia el estado de su merma
    Dado que publiqué una merma
    Cuando otro productor intenta cambiar su estado
    Entonces recibo 404
