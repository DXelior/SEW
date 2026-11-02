import xml.etree.ElementTree as ET

class Kml(object):
    def __init__(self):
        self.raiz = ET.Element(
            'kml',
            xmlns="http://www.opengis.net/kml/2.2"
        )
        self.doc = ET.SubElement(self.raiz, 'Document')
        self._crear_estilos()

    def _crear_estilos(self):
        estilos = {
            'estiloRojo': 'ff0000ff',
            'estiloVerde': 'ff00ff00',
            'estiloAzul': 'ffff0000',
            'estiloAmarillo': 'ff00ffff'
        }
        
        for id_estilo, color in estilos.items():
            style = ET.SubElement(self.doc, 'Style', id=id_estilo)
            icon_style = ET.SubElement(style, 'IconStyle')
            ET.SubElement(icon_style, 'color').text = color
            ET.SubElement(icon_style, 'scale').text = '1.1'
            icon = ET.SubElement(icon_style, 'Icon')
            ET.SubElement(icon, 'href').text = 'http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png'

    def addPlacemark(self, nombre, descripcion, long, lat, alt, modoAltitud, idEstilo):
        pm = ET.SubElement(self.doc, 'Placemark')

        ET.SubElement(pm, 'name').text = nombre
        ET.SubElement(pm, 'description').text = descripcion
        ET.SubElement(pm, 'styleUrl').text = f'#{idEstilo}'

        punto = ET.SubElement(pm, 'Point')
        ET.SubElement(punto, 'coordinates').text = f'{long},{lat},{alt}'
        ET.SubElement(punto, 'altitudeMode').text = modoAltitud

    def addLineString(self, nombre, extrude, tesela, listaCoordenadas,
                      modoAltitud, color, ancho):

        ET.SubElement(self.doc, 'name').text = nombre

        pm = ET.SubElement(self.doc, 'Placemark')

        ls = ET.SubElement(pm, 'LineString')
        ET.SubElement(ls, 'extrude').text = extrude
        ET.SubElement(ls, 'tessellation').text = tesela
        ET.SubElement(ls, 'coordinates').text = listaCoordenadas
        ET.SubElement(ls, 'altitudeMode').text = modoAltitud

        estilo = ET.SubElement(pm, 'Style')
        linea = ET.SubElement(estilo, 'LineStyle')
        ET.SubElement(linea, 'color').text = color
        ET.SubElement(linea, 'width').text = ancho

    def escribir(self, nombreArchivoKML):
        arbol = ET.ElementTree(self.raiz)
        ET.indent(arbol)
        arbol.write(
            nombreArchivoKML,
            encoding='utf-8',
            xml_declaration=True
        )


def xml_a_kml(archivo_xml, archivo_kml):

    ns = {'ns': 'http://www.uniovi.es'}

    try:
        tree = ET.parse(archivo_xml)
        root = tree.getroot()
    except (IOError, ET.ParseError) as e:
        print(f"Error al procesar el archivo {archivo_xml}: {e}")
        return

    etapa = root.find('ns:etapa', ns)
    if etapa is None:
        print("No se encontró el elemento 'etapa' en el XML.")
        return

    kml = Kml()
    coordenadas_linea = []

    # ---------------------------------------------------------
    # 1. DATOS DE SALIDA (ROJO)
    # ---------------------------------------------------------
    salida = etapa.find('ns:datosSalida', ns)
    if salida is not None:
        lon = salida.attrib['longitud']
        lat = salida.attrib['latitud']
        alt = salida.attrib['altitud']
        nombre = salida.text or "Salida"

        kml.addPlacemark(
            nombre,
            "Punto de salida",
            lon, lat, alt,
            'relativeToGround',
            'estiloRojo'
        )
        coordenadas_linea.append(f"{lon},{lat},{alt}")

    # ---------------------------------------------------------
    # 2. HITOS Y PUNTOS ANÓNIMOS
    # ---------------------------------------------------------
    elementos_ruta = []

    # HITOS (VERDE si es puerto, AZUL si es sprint, ROJO de otro modo)
    hitos = etapa.find('ns:hitos', ns)
    if hitos is not None:
        for index, hito in enumerate(hitos.findall('ns:hito', ns), start=1):
            lon = hito.attrib['longitud']
            lat = hito.attrib['latitud']
            alt = hito.attrib['altitud']
            distancia = float(hito.attrib['distancia'])

            tipo_elemento = hito.find('ns:tipo', ns)
            categoria_elemento = hito.find('ns:categoría', ns)

            tipo = tipo_elemento.text if tipo_elemento is not None else ""
            categoria = categoria_elemento.text if categoria_elemento is not None else ""

            # Determinar estilo de color según el tipo de hito
            tipo_lower = tipo.lower()
            if "puerto" in tipo_lower or "montaña" in tipo_lower:
                estilo_hito = 'estiloVerde'
            elif "sprint" in tipo_lower:
                estilo_hito = 'estiloAzul'
            else:
                estilo_hito = 'estiloRojo'

            kml.addPlacemark(
                f"Hito {index}: {tipo}",
                f"Categoría: {categoria}",
                lon, lat, alt,
                'relativeToGround',
                estilo_hito
            )

            elementos_ruta.append((distancia, f"{lon},{lat},{alt}"))

    # PUNTOS ANÓNIMOS (AMARILLO)
    puntos = etapa.find('ns:puntosAnónimos', ns)
    if puntos is not None:
        for index, punto in enumerate(puntos.findall('ns:puntoAnónimo', ns), start=1):
            lon = punto.attrib['longitud']
            lat = punto.attrib['latitud']
            alt = punto.attrib['altitud']
            distancia = float(punto.attrib['distancia'])

            kml.addPlacemark(
                f"Punto Anónimo {index}",
                f"Distancia: {distancia} km",
                lon, lat, alt,
                'relativeToGround',
                'estiloAmarillo'
            )

            elementos_ruta.append((distancia, f"{lon},{lat},{alt}"))

    # ---------------------------------------------------------
    # ORDENAR EL RECORRIDO
    # ---------------------------------------------------------
    elementos_ruta.sort(key=lambda elemento: elemento[0])

    for distancia, coordenadas in elementos_ruta:
        coordenadas_linea.append(coordenadas)

    # ---------------------------------------------------------
    # 3. DATOS DE META (ROJO)
    # ---------------------------------------------------------
    meta = etapa.find('ns:datosMeta', ns)
    if meta is not None:
        lon = meta.attrib['longitud']
        lat = meta.attrib['latitud']
        alt = meta.attrib['altitud']
        nombre = meta.text or "Meta"

        kml.addPlacemark(
            nombre,
            "Punto de llegada",
            lon, lat, alt,
            'relativeToGround',
            'estiloRojo'
        )
        coordenadas_linea.append(f"{lon},{lat},{alt}")

    # ---------------------------------------------------------
    # 4. TRAZADO DE RUTA (LineString)
    # ---------------------------------------------------------
    string_coordenadas = "\n".join(coordenadas_linea)
    nombre_elemento = etapa.find('ns:nombre', ns)
    nombre_etapa = nombre_elemento.text if nombre_elemento is not None else "Ruta"

    kml.addLineString(
        nombre_etapa,
        "1",
        "1",
        string_coordenadas,
        'relativeToGround',
        'ff0000ff',  # Línea en rojo
        "5"
    )

    # ---------------------------------------------------------
    # 5. GUARDAR ARCHIVO KML
    # ---------------------------------------------------------
    kml.escribir(archivo_kml)
    print(f"Archivo '{archivo_kml}' generado correctamente con el código de colores indicado.")


if __name__ == "__main__":
    xml_a_kml('etapaEsquema.xml', 'etapa.kml')