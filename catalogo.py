"""
catalogo.py - Crea productos.csv con 100 productos de ferreteria reales.

Proporciones pensadas como una ferreteria de barrio:
  Tornilleria          25  (es lo que mas rota)
  Electricidad         20
  Plomeria             20
  Pinturas             15
  Herramientas manuales 12
  Electricas            8  (pocas maquinas, son caras y rotan poco)

El precio y el stock los ponen despues ajustar-precios.py y ajustar-stock.py.
"""

import pandas as pd

CATALOGO = {
    "Tornillería": [
        "Tornillo Autoperforante 8 x 1\" Caja x 100",
        "Tornillo Autoperforante 10 x 2\" Caja x 100",
        "Tornillo Autoperforante 8 x 1/2\" Caja x 200",
        "Tornillo Drywall 6 x 1\" Caja x 500",
        "Tornillo Madera 10 x 3\" Caja x 50",
        "Clavo de Fierro 2\" 1 kg",
        "Clavo de Fierro 3\" 1 kg",
        "Clavo de Fierro 4\" 1 kg",
        "Clavo de Albañil 3\" 1 kg",
        "Clavo de Calamina 2 1/2\" 1 kg",
        "Tuerca Hexagonal 1/4\" Caja x 100",
        "Tuerca Hexagonal 3/8\" Caja x 50",
        "Arandela Plana 1/2\" Caja x 100",
        "Arandela de Presión 3/8\" Caja x 100",
        "Perno de Anclaje 3/8\" x 4\"",
        "Perno de Anclaje 1/2\" x 5\"",
        "Tarugo PVC 8 mm x 100 unid",
        "Tarugo PVC 10 mm x 50 unid",
        "Tirafondo 1/4\" x 2\" Caja x 100",
        "Remache Pop 1/8\" Caja x 100",
        "Abrazadera Omega 1/2\" x 50",
        "Grapa de Cerco 1 1/2\"",
        "Tornillo Fijación 3/16\" Caja x 100",
        "Espárrago Roscado 1/4\" x 1 m",
        "Cadena Galvanizada 1/8\" x metro",
    ],
    "Electricidad": [
        "Cable THW 14 AWG x 100 m",
        "Cable THW 12 AWG x 100 m",
        "Cable Mellizo 2x16 x 100 m",
        "Cable Vulcanizado 2x18 x 50 m",
        "Tubo Conduit PVC 3/4\" x 3 m",
        "Tubo Conduit PVC 1\" x 3 m",
        "Curva Conduit PVC 3/4\"",
        "Caja Octogonal PVC",
        "Caja Rectangular PVC",
        "Tomacorriente Doble 15A",
        "Tomacorriente con Tierra 15A",
        "Interruptor Simple 10A",
        "Interruptor Doble 10A",
        "Breaker Monofásico 20A",
        "Breaker Monofásico 32A",
        "Tablero Eléctrico 12 Polos",
        "Cinta Aislante Negra x 20 m",
        "Cinta Aislante Roja x 20 m",
        "Foco LED 9W Luz Fría",
        "Portalámpara Colgante E27",
    ],
    "Plomería": [
        "Tubo PVC SAP 1/2\" x 3 m",
        "Tubo PVC SAP 3/4\" x 3 m",
        "Tubo PVC SAP 1\" x 3 m",
        "Tubo Desagüe 2\" x 3 m",
        "Tubo Desagüe 4\" x 3 m",
        "Codo PVC 1/2\" x 90°",
        "Codo PVC 3/4\" x 90°",
        "Codo PVC 1\" x 90°",
        "Tee PVC 1/2\"",
        "Tee PVC 3/4\"",
        "Llave Esférica 1/2\"",
        "Llave Esférica 3/4\"",
        "Válvula Check 1/2\"",
        "Unión Universal 1/2\"",
        "Pegamento PVC 1/4 Galón",
        "Teflón 1/2\" x 10 m",
        "Llave de Paso 1/2\"",
        "Flotador de Tanque 1/2\"",
        "Sifón PVC 1 1/4\"",
        "Inodoro Tanque Bajo Blanco",
    ],
    "Pinturas": [
        "Látex Lavable Blanco Hueso 1 Galón",
        "Látex Lavable Blanco Humo 1 Galón",
        "Látex Mate Blanco Hueso 1/4 Galón",
        "Látex Mate Celeste Cielo 1 Galón",
        "Látex Mate Gris Perla 1 Galón",
        "Óleo Mate Blanco Hueso 1/4 Galón",
        "Óleo Brillante Azul Colonial 1 Galón",
        "Esmalte Sintético Verde Sauces 1 Galón",
        "Esmalte Sintético Amarillo Tráfico 1/4 Galón",
        "Esmalte Brillante Negro Mate 1 Galón",
        "Anticorrosivo Gris Perla 1 Galón",
        "Fondo Antióxido Negro 1 Galón",
        "Base Selladora Blanca 1 Galón",
        "Barniz Marino Brillante 1/4 Galón",
        "Thinner Acrílico 1 Litro",
    ],
    "Herramientas manuales": [
        "Martillo Carpintero 16 oz Mango Madera",
        "Martillo de Bola 24 oz",
        "Desarmador Plano 6\" Cromo Vanadio",
        "Desarmador Estrella 6\" Cromo Vanadio",
        "Wincha 5 m Acero",
        "Flexómetro 8 m",
        "Llave Inglesa 10\"",
        "Alicate Universal 8\"",
        "Alicate de Presión 10\"",
        "Serrucho 20\"",
        "Nivel de Burbuja 60 cm",
        "Cuchilla de Vidia",
    ],
    "Eléctricas": [
        "Taladro Percutor 650W Compacto",
        "Esmeril Angular 4 1/2\" 820W Profesional",
        "Caladora 500W Compacto",
        "Lijadora Orbital 240W",
        "Atornillador 12V Compacto",
        "Amoladora 900W",
        "Pistola de Calor 1800W",
        "Sierra Circular 7 1/4\" 1400W",
    ],
}

filas = []
for categoria, nombres in CATALOGO.items():
    for nombre in nombres:
        filas.append({"nombre": nombre, "categoria": categoria})

productos = pd.DataFrame(filas)
productos.insert(0, "id_producto", range(1, len(productos) + 1))
productos["precio"] = 0.0
productos["stock"] = 0

productos.to_csv("productos.csv", index=False, encoding="utf-8")

print("Productos creados:", len(productos))
for categoria, grupo in productos.groupby("categoria"):
    print(f"  {categoria}: {len(grupo)}")
