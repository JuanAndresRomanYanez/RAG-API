import re

# Diccionario de modismos/jerga a término estándar
LEXICAL_MAP = {
    # Accidentes de tránsito --> Atropello
    "atropellar":           "responsabilidad del conductor",
    "atropello":            "responsabilidad del conductor",
    "chocar":               "responsabilidad del conductor",
    "choco":                "responsabilidad del conductor",

    # Accidente de tránsito --> Fuga
    "no prestar auxilio":       "fuga",
    "no prestar ayuda":         "fuga",
    "no ayudar":                "fuga",

    # Ebrio o borracho
    "borracho":                 "estado de embriaguez",
    "ebrio":                    "estado de embriaguez",
    "tomado":                   "estado de embriaguez",
    "chaki":                    "estado de embriaguez",
    "yema":                     "estado de embriaguez",
    "duro":                     "estado de embriaguez",
    "pedo":                     "estado de embriaguez",
    "beodo":                    "estado de embriaguez",
    "estado de ebriedad":       "estado de embriaguez",
    "alcoholizado":             "estado de embriaguez",
    "mamado":                   "estado de embriaguez",
    "colgado":                  "estado de embriaguez",
    "chupado":                  "estado de embriaguez",
    "bebedor":                  "estado de embriaguez",
    
    # Exceso de velocidad
    "exceso de velocidad":                  "velocidades máximas",
    "exceso de velocidad permitido":        "velocidades máximas",
    "velocidad excesiva":                   "velocidades máximas",
    "velocidad máxima":                     "velocidades máximas",
    "velocidad permitida":                  "velocidades máximas",
    "limite de velocidad":                  "velocidades máximas",
    "velocidad punta":                      "velocidades máximas",

    # Policía
    "paco":            "policía",
    "rata":            "policía",
    "cana":            "policía",
    "maría":           "policía",
    "oficial":         "policía",
    "agente":          "policía",
    "poli":            "policía",
    "patrullero":      "policía",
    "operativo":       "policía",

    
    # Delincuente
    "motochoro":       "delincuente",
    "maleante":        "delincuente",
    "ladrón":          "delincuente",
    "chorro":          "delincuente",
    "choro":           "delincuente",
    "palomillo":       "delincuente",

    # Colisión
    "choque":          "colisión",
    "chocar":          "colisión",
    "golpe":           "colisión",

    # Multa
    "castigo":              "multa",
    "penalización":         "multa",
    "pena":                 "multa",
    "sancion":              "multa",
    "papeleta":             "multa",
    "boleta":               "multa",
    "boletita":             "multa",
    "papelito":             "multa",
    "tique":                "multa",
    "tiquet":               "multa",

    # Infracción
    "falta":           "infracción",

    # Licencia
    "papel":                    "licencia",
    "brevete":                  "licencia",
    "brevette":                 "licencia",
    "brevet":                   "licencia",
    "carnet de conducir":       "licencia",
    "carne de conducir":        "licencia",
    "duplicado":                "licencia",

    # LLevar licencia
    "porto licencia":           "exhibir su licencia",
    "porto licencia":           "exhibir la licencia",
    "llevo licencia":           "exhibir su licencia",
    "llevo licencia":           "exhibir la licencia",
    "portar licencia":          "exhibir su licencia",
    "portar licencia":          "exhibir la licencia",
    "llevar licencia":          "exhibir su licencia",
    "llevar licencia":          "exhibir la licencia",
    "poseo la licencia":        "exhibir su licencia",
    "poseo la licencia":        "exhibir la licencia",
    "tengo la licencia":        "exhibir su licencia",
    "tengo la licencia":        "exhibir la licencia",
    "tenia la licencia":        "exhibir su licencia",
    "tenia la licencia":        "exhibir la licencia",

    # Estacionamiento
    "parquear":        "estacionar",
    "parquearme":      "estacionar",
    "parqueo":         "estacionar",
    "parquee":         "estacionar",
    "parqueado":       "estacionar",

    # Zonas de estacionamiento
    "zona de discapacidad":         "lugares no autorizados",
    "zona de discapacitados":       "lugares no autorizados",
    "lugar de discapacidad":        "lugares no autorizados",
    "lugar de discapacitados":      "lugares no autorizados",

    # Control rutinario 
    "control rutinario":            "inspección imprevista o identificación",
    "inspección de rutina":         "inspección imprevista o identificación",
    "comprobación regular":         "inspección imprevista o identificación",
    "vigilancia habitual":          "inspección imprevista o identificación",
    "supervisión periódica":        "inspección imprevista o identificación",
    "verificación constante":       "inspección imprevista o identificación",
    "control en ciudad":            "inspección imprevista o identificación",
    "control en carretera":         "inspección imprevista o identificación",
    "control en ruta":              "inspección imprevista o identificación",
    "control en vía":               "inspección imprevista o identificación",
    "control en autopista":         "inspección imprevista o identificación",
    "control en la ciudad":         "inspección imprevista o identificación",
    "control en la carretera":      "inspección imprevista o identificación",
    "control en la ruta":           "inspección imprevista o identificación",
    "control en la vía":            "inspección imprevista o identificación",
    "control en la autopista":      "inspección imprevista o identificación",

    #Adelantar o rebasar
    "adelantar":                    "adelantamiento",
    "rebasar":                      "adelantamiento",
    "aventajar":                    "adelantamiento",
    "adelanto":                     "adelantamiento",
    "rebaso":                       "adelantamiento",
    "aventajo":                     "adelantamiento",
    "adelantando":                  "adelantamiento",
    "rebasando":                    "adelantamiento",
    "aventajando":                  "adelantamiento",


    # Auto / Vehículo
    "carro":           "vehículo",
    "coche":           "vehículo",
    "nave":            "vehículo",
    "fierro":          "vehículo",
    "maquinola":       "vehículo",
    "automóvil":       "vehículo",
    "auto":            "vehículo",
    "camioneta":       "vehículo",
    "camión":          "vehículo",
    "camioncito":      "vehículo",
    "camioncillo":     "vehículo",
    "carrito":         "vehículo",
    "vagoneta":        "vehículo",
    "vagón":           "vehículo",

    # Moto
    "moto":            "motocicleta",
    "motillo":         "motocicleta",
    "motocha":         "motocicleta",
    "motoneta":        "motocicleta",

    # Motociclista
    "motoquero":       "motociclista",

    # Conductor
    "chofer":          "conductor",
    "chofercito":      "conductor",
    "chofercillo":     "conductor",
    "choferazo":       "conductor",
    "maestro":         "conductor",
    "maestrito":       "conductor",
    "taxista":         "conductor",
    "el uber":         "conductor",
    "el yango":        "conductor",
    "tachero":         "conductor",

    # Bicicleta
    "bici":            "bicicleta",
    "triciclo":        "bicicleta",
    "bicla":           "bicicleta",

    # Semáforo
    "luz roja":        "semáforo",
    "sema":            "semáforo",
    "luz":             "semáforo",
    "farol":           "semáforo",

    # Paso de peatones
    "cebra":                    "franja de seguridad",
    "zebra":                    "franja de seguridad",
    "paso peatonal":            "franja de seguridad",
    "paso de cebra":            "franja de seguridad",
    "pasos peatonales":         "franja de seguridad",
    "pasos de cebra":           "franja de seguridad",
    "paso de peatones":         "franja de seguridad",
    "paso para peatón":         "franja de seguridad",
    "cruce peatonal":           "franja de seguridad",
    "senda peatonal":           "franja de seguridad",
    "paso para peatones":       "franja de seguridad",
    "zonas de intersección":    "franja de seguridad",

    # Peatón 
    "peatona":         "peatón",
    "peatones":        "peatón",
    "peatonales":      "peatón",
    "personas":        "peatón",

    # Carril
    "carrilito":       "carril",
    "carrileras":      "carril",

    # Arresto / Cárcel
    "chichi":          "arresto",
    "calabozo":        "arresto",
    "celda":           "arresto",
    "cárcel":          "arresto",

    # Pasajeros
    "viajero":        "pasajero",
    "acompañante":    "pasajero",
    "copiloto":       "pasajero",

    # Micros
    "minibus":              "micros",
    "colectivo":            "micros",
    "transporte público":   "micros",
    "bus":                  "micros",
    "transporte urbano":    "micros",

}

# Precompila el patrón de búsqueda con word‑boundary
_pattern = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in LEXICAL_MAP.keys()) + r")\b",
    flags=re.IGNORECASE
)

def apply_lexical_filters(text: str) -> str:
    """
    Reemplaza todas las apariciones de modismos según LEXICAL_MAP.
    Conserva mayúsculas/minúsculas originales en el resto del texto.
    """
    def _repl(match):
        slang = match.group(0).lower()
        return LEXICAL_MAP.get(slang, slang)
    # re.sub recorre todo el texto, busca cada coincidencia de _pattern
    # y la sustituye usando la función _repl
    return _pattern.sub(_repl, text)
