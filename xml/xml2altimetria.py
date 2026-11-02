import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

class AltimetriaParser:
    """Clase encargada de leer el XML y procesar los datos con XPath."""
    
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.tree = ET.parse(self.xml_file)
        self.root = self.tree.getroot()

        if self.root.tag.startswith('{'):
            uri = self.root.tag.split('}')[0].strip('{')
            self.ns = {'ns': uri}
        else:
            self.ns = {}

    def _busqueda_xpath(self, expresion):
        """Método auxiliar para ejecutar búsquedas XPath soportando namespaces."""
        if self.ns:
            partes = expresion.split('/')
            partes_ns = [f"ns:{p}" if p and not p.startswith('.') else p for p in partes]
            expr_ns = '/'.join(partes_ns)
            
            nodos = self.root.findall(expr_ns, self.ns)
            if nodos:
                return nodos
        
        return self.root.findall(expresion)

    def obtener_puntos_anonimos(self):
        """Extrae la secuencia de puntos (distancia, altitud) usando XPath."""
        puntos = self._busqueda_xpath('.//puntoAnónimo')
            
        distancias = [float(p.attrib['distancia']) for p in puntos]
        altitudes = [float(p.attrib['altitud']) for p in puntos]
        return distancias, altitudes

    def obtener_hitos(self):
        """Extrae los hitos (puertos, sprints) usando XPath."""
        elementos_hito = self._busqueda_xpath('.//hito')
        
        hitos_x, hitos_y, etiquetas = [], [], []
        
        for hito in elementos_hito:
            hitos_x.append(float(hito.attrib['distancia']))
            hitos_y.append(float(hito.attrib['altitud']))
            
            tipo_nodo = hito.find('ns:tipo', self.ns) if self.ns else hito.find('tipo')
            if tipo_nodo is None:
                tipo_nodo = hito.find('tipo')
                
            cat_nodo = hito.find('ns:categoría', self.ns) if self.ns else hito.find('categoría')
            if cat_nodo is None:
                cat_nodo = hito.find('categoría')
            
            texto = tipo_nodo.text if tipo_nodo is not None else "Hito"
            if cat_nodo is not None and cat_nodo.text:
                texto += f" ({cat_nodo.text})"
            etiquetas.append(texto)
            
        return hitos_x, hitos_y, etiquetas


class GeneradorGrafico:
    """Clase encargada de la representación visual y exportación a SVG."""
    
    def __init__(self, parser: AltimetriaParser):
        self.parser = parser

    def renderizar_y_guardar(self, output_svg="altimetria.svg"):
        """Genera la gráfica, la guarda como archivo SVG y la muestra."""
        distancias, altitudes = self.parser.obtener_puntos_anonimos()
        hitos_x, hitos_y, etiquetas = self.parser.obtener_hitos()

        if not distancias:
            print("No se encontraron puntos anónimos en el archivo XML.")
            return

        plt.figure(figsize=(12, 6))
        
        # Dibujar perfil altimétrico
        plt.plot(distancias, altitudes, color='#d9534f', linewidth=2, label='Perfil de la etapa')
        plt.fill_between(distancias, altitudes, color='#d9534f', alpha=0.2)
        
        # Marcar hitos
        for x, y, texto in zip(hitos_x, hitos_y, etiquetas):
            plt.scatter(x, y, color='blue', zorder=5)
            plt.annotate(texto, (x, y), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8, weight='bold')

        plt.title('Perfil Altimétrico de la Etapa', fontsize=14, weight='bold')
        plt.xlabel('Distancia (km)', fontsize=11)
        plt.ylabel('Altitud (m)', fontsize=11)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend(loc='upper left')
        
        plt.tight_layout()
        
        # Guardar la gráfica como SVG antes de mostrarla
        plt.savefig(output_svg, format='svg', bbox_inches='tight')
        print(f"¡Éxito! El archivo SVG se ha guardado como '{output_svg}'")
        
        # Mostrar la ventana interactiva
        plt.show()


if __name__ == "__main__":
    parser = AltimetriaParser('etapaEsquema.xml')
    grafico = GeneradorGrafico(parser)
    grafico.renderizar_y_guardar('altimetria.svg')