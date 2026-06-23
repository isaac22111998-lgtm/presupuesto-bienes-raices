"""
Inicializa la base de datos con datos de seed.
Se ejecuta automáticamente al arrancar el contenedor Docker.
Si los datos ya existen, no los duplica.
"""
import os
import sys
from app import create_app, db
from app.models import User, HouseType, Category, Component

app = create_app()

HOUSE_TYPES = [
    {
        'name': 'Casa Popular',
        'description': 'Construcción de interés social con acabados básicos y funcionales. La opción más accesible.',
        'finish_level': 'popular',
        'color': '#3b82f6',
        'icon': 'bi-house',
    },
    {
        'name': 'Casa Intermedia',
        'description': 'Acabados de calidad media-alta. Porcelanato, boiler instalado, cocina integral y más comodidades.',
        'finish_level': 'intermedio',
        'color': '#8b5cf6',
        'icon': 'bi-house-fill',
    },
    {
        'name': 'Casa de Lujo',
        'description': 'Materiales premium: granito, duela de madera, calentador solar, cancelería de cristal templado y domótica.',
        'finish_level': 'lujo',
        'color': '#f59e0b',
        'icon': 'bi-stars',
    },
]

CATEGORIES = [
    ('Trabajos Preliminares', 'Topografía, trazo, permisos y licencias municipales', 1, 'bi-compass'),
    ('Cimentación', 'Excavación, zapatas, cadenas y contratrabe', 2, 'bi-layers-fill'),
    ('Estructura', 'Columnas, vigas, losa y castillos de concreto armado', 3, 'bi-building'),
    ('Muros y Tabiques', 'Levantamiento de muros y aplanados', 4, 'bi-bricks'),
    ('Cubierta y Techo', 'Impermeabilización y plafones', 5, 'bi-house-door'),
    ('Instalación Hidráulica', 'Red de agua, cisterna y sistema de presión', 6, 'bi-droplet-fill'),
    ('Instalación Sanitaria', 'Drenaje, bajadas y conexión a red municipal', 7, 'bi-pipe'),
    ('Instalación Eléctrica', 'Tablero, cableado, contactos e iluminación', 8, 'bi-lightning-charge-fill'),
    ('Gas y Calefacción', 'Sistema de gas y calentador de agua', 9, 'bi-fire'),
    ('Pisos', 'Recubrimiento de pisos y zoclos', 10, 'bi-grid-3x3'),
    ('Paredes y Pintura', 'Acabados en muros y techos', 11, 'bi-paint-bucket'),
    ('Carpintería', 'Puertas, ventanas, closets y cocina integral', 12, 'bi-tools'),
    ('Herrería y Seguridad', 'Rejas, portón y sistemas de seguridad', 13, 'bi-shield-fill'),
    ('Baños', 'Sanitarios, lavabos, regaderas y accesorios', 14, 'bi-droplet'),
    ('Cocina', 'Tarja y muebles de cocina', 15, 'bi-house-heart'),
    ('Exteriores y Jardinería', 'Barda, banqueta, cochera y jardín', 16, 'bi-tree-fill'),
    ('Honorarios Profesionales', 'Planos arquitectónicos, topógrafo y permisos', 17, 'bi-person-badge-fill'),
]

# Formato: (nombre, descripción, unidad, precio_unit, obligatorio, cant_default, tipo_casa, grupo)
# tipo_casa: None = todos, 'popular', 'intermedio', 'lujo'
COMPONENTS = [
    # ── TRABAJOS PRELIMINARES ──────────────────────────────────────────────
    ('Trabajos Preliminares', [
        ('Levantamiento topográfico del terreno 120 m²',
         'Medición y delimitación precisa del terreno, ángulos y curvas de nivel para terrenos irregulares.',
         'global', 4000, True, 1, None, None),
        ('Limpieza, trazo y nivelación',
         'Desmonte del área, trazo de ejes, nivelación del terreno de 80 m² de construcción.',
         'global', 3500, True, 1, None, None),
        ('Permisos de construcción y licencias municipales',
         'Trámites ante el Ayuntamiento de Acapulco, alineamiento y número oficial.',
         'global', 9500, True, 1, None, None),
    ]),

    # ── CIMENTACIÓN ───────────────────────────────────────────────────────
    ('Cimentación', [
        ('Cimentación popular – zapatas y cadenas 80 m²',
         'Excavación, plantilla f\'c=100, zapatas f\'c=200, cadenas y contratrabe para casa popular.',
         'global', 48000, True, 1, 'popular', 'cimentacion'),
        ('Cimentación intermedia – zapatas y cadenas 80 m²',
         'Cimentación con concreto f\'c=250 y acero de refuerzo calculado estructuralmente.',
         'global', 58000, True, 1, 'intermedio', 'cimentacion'),
        ('Cimentación de lujo – reforzada 80 m²',
         'Cimentación con concreto f\'c=300, acero de alto desempeño, estudio de mecánica de suelos incluido.',
         'global', 76000, True, 1, 'lujo', 'cimentacion'),
    ]),

    # ── ESTRUCTURA ────────────────────────────────────────────────────────
    ('Estructura', [
        ('Estructura popular – columnas, vigas y losa 80 m²',
         'Columnas y vigas de concreto f\'c=200, losa de vigueta y bovedilla.',
         'global', 85000, True, 1, 'popular', 'estructura'),
        ('Estructura intermedia – columnas, vigas y losa maciza 80 m²',
         'Columnas y vigas reforzadas f\'c=250, losa maciza con acero calculado.',
         'global', 108000, True, 1, 'intermedio', 'estructura'),
        ('Estructura de lujo – reforzada 80 m²',
         'Estructura de alto desempeño f\'c=300, losa maciza, castillos y dalas de concreto reforzado.',
         'global', 138000, True, 1, 'lujo', 'estructura'),
    ]),

    # ── MUROS Y TABIQUES ──────────────────────────────────────────────────
    ('Muros y Tabiques', [
        ('Muros de tabique rojo recocido',
         'Tabique rojo con junteado de mortero. Aplica a los 3 tipos de casa (precio por m²).',
         'm²', 280, True, 160, None, None),
        ('Aplanado de mortero interior',
         'Aplanado de mortero cemento-arena acabado frotachado en paredes interiores.',
         'm²', 85, True, 160, None, None),
        ('Aplanado de mortero exterior / fachada',
         'Aplanado exterior con mortero impermeable en fachada.',
         'm²', 95, True, 80, None, None),
    ]),

    # ── CUBIERTA Y TECHO ──────────────────────────────────────────────────
    ('Cubierta y Techo', [
        ('Impermeabilización con membrana asfáltica',
         'Membrana impermeabilizante Sika o similar en azotea, garantía 10 años.',
         'm²', 185, True, 80, None, None),
        ('Plafón de yeso básico',
         'Plafón corrido de yeso con acabado liso.',
         'm²', 250, False, 75, 'popular', 'plafon'),
        ('Plafón de tablaroca (Durlock/Knauf)',
         'Plafón de placa de yeso-cartón con bordes definidos y acabado fino para pintura.',
         'm²', 390, False, 75, 'intermedio', 'plafon'),
        ('Plafón de diseño con luminarias embutidas',
         'Plafón arquitectónico con nichos, desniveles y luminarias LED embutidas.',
         'm²', 660, False, 75, 'lujo', 'plafon'),
    ]),

    # ── INSTALACIÓN HIDRÁULICA ────────────────────────────────────────────
    ('Instalación Hidráulica', [
        ('Red hidráulica en CPVC para toda la casa',
         'Tuberías CPVC, registros, llaves de paso y conexiones para casa de 80 m².',
         'global', 18500, True, 1, None, None),
        ('Cisterna de concreto armado 5,000 L',
         'Cisterna subterránea con tapa de concreto y conexión a bomba.',
         'pza', 12500, True, 1, None, None),
        ('Tinaco 1,100 L + bomba automática (popular/intermedio)',
         'Tinaco Rotoplas 1,100 L con bomba automática y flotador.',
         'global', 4800, True, 1, 'popular', 'agua_presion'),
        ('Tinaco 1,100 L + bomba automática (popular/intermedio)',
         'Tinaco Rotoplas 1,100 L con bomba automática y flotador.',
         'global', 4800, True, 1, 'intermedio', 'agua_presion'),
        ('Sistema hidroneumático de presión constante',
         'Hidro-neumático Grundfos con sensor de presión, filtro y conexiones.',
         'global', 13500, True, 1, 'lujo', 'agua_presion'),
    ]),

    # ── INSTALACIÓN SANITARIA ─────────────────────────────────────────────
    ('Instalación Sanitaria', [
        ('Red sanitaria en PVC para toda la casa',
         'Tuberías PVC sanitarias, bajadas pluviales y registros para casa de 80 m².',
         'global', 12500, True, 1, None, None),
        ('Conexión a drenaje municipal de Acapulco',
         'Acometida y conexión a la red de drenaje del Municipio de Acapulco.',
         'global', 5800, True, 1, None, None),
        ('Biodigestor Rotoplas 600 L (alternativa a drenaje)',
         'Sistema de tratamiento individual si no hay conexión a red municipal disponible.',
         'pza', 12800, False, 1, None, None),
    ]),

    # ── INSTALACIÓN ELÉCTRICA ─────────────────────────────────────────────
    ('Instalación Eléctrica', [
        ('Tablero eléctrico 12 circuitos Square-D',
         'Tablero con interruptores termomagnéticos, 12 circuitos, incluye acometida.',
         'pza', 3900, True, 1, 'popular', 'tablero'),
        ('Tablero eléctrico 16 circuitos con diferencial',
         'Tablero Square-D 16 circuitos, interruptor diferencial y tierra física.',
         'pza', 5800, True, 1, 'intermedio', 'tablero'),
        ('Tablero 20 circuitos + supresor de picos',
         'Tablero de alta capacidad con protección diferencial y supresor de sobrevoltaje.',
         'pza', 9800, True, 1, 'lujo', 'tablero'),
        ('Cableado y conduit – 15 salidas (popular)',
         'Cableado Cal.12 THHN en conduit metálico, 15 salidas con contactos básicos.',
         'global', 16500, True, 1, 'popular', None),
        ('Cableado y conduit – 20 salidas con GFCI (intermedio)',
         'Cableado Cal.12 THHN, 20 salidas, contactos GFCI en cocina y baños.',
         'global', 22500, True, 1, 'intermedio', None),
        ('Cableado de cobre – 25 salidas GFCI + tierra (lujo)',
         'Cableado de cobre de alta calidad, 25 salidas, GFCI, tierra física certificada.',
         'global', 33000, True, 1, 'lujo', None),
        ('Salidas para red/internet CAT6 (4 puntos)',
         'Puntos de red CAT6 en sala, habitaciones y cocina. Incluye patch panel.',
         'global', 4200, False, 1, 'intermedio', None),
        ('Salidas para red/internet CAT6 + WiFi (6 puntos)',
         'Red CAT6 completa con 6 puntos y 2 access points WiFi 6 empotrados.',
         'global', 8500, False, 1, 'lujo', None),
        ('Sistema domótico básico (luces + cortinas)',
         'Control de iluminación y cortinas desde app móvil, 8 zonas.',
         'global', 22000, False, 1, 'lujo', None),
    ]),

    # ── GAS Y CALEFACCIÓN ─────────────────────────────────────────────────
    ('Gas y Calefacción', [
        ('Preparación para gas LP (sin instalación activa)',
         'Tubería de cobre y válvulas colocadas, conexión pendiente por parte del usuario.',
         'global', 2800, True, 1, 'popular', 'gas_sistema'),
        ('Instalación completa de gas LP con tubería',
         'Sistema completo de gas LP con tubería de cobre, válvulas y reguladores. Tanque estacionario no incluido.',
         'global', 8800, True, 1, 'intermedio', 'gas_sistema'),
        ('Gas estacionario Tatsa 300 L + instalación completa',
         'Tanque estacionario 300 L con reguladores, válvula de seguridad y toda la instalación.',
         'pza', 19500, True, 1, 'lujo', 'gas_sistema'),
        ('Boiler de paso Calorex 14 L',
         'Calentador instantáneo a gas 14 L/min instalado en baño.',
         'pza', 4500, False, 1, 'intermedio', 'calefaccion'),
        ('Calentador solar 200 L + boiler de respaldo',
         'Sistema solar Calorex con 2 colectores planos y boiler de respaldo a gas.',
         'global', 29500, False, 1, 'lujo', 'calefaccion'),
    ]),

    # ── PISOS ─────────────────────────────────────────────────────────────
    ('Pisos', [
        ('Piso cerámico básico 33×33 instalado',
         'Cerámica nacional 33×33 con pegamento, boquilla y nivelado.',
         'm²', 220, True, 80, 'popular', 'piso_principal'),
        ('Porcelanato Interceramic 60×60 instalado',
         'Porcelanato rectificado 60×60, adhesivo de calidad, juntas mínimas.',
         'm²', 490, True, 80, 'intermedio', 'piso_principal'),
        ('Granito natural 60×60 pulido (áreas sociales)',
         'Granito nacional importado, pulido, instalado con adhesivo epóxico.',
         'm²', 860, True, 50, 'lujo', 'piso_principal'),
        ('Duela de madera sólida pino/encino (habitaciones)',
         'Duela de 3" barnizada en habitaciones, instalada sobre base nivelada.',
         'm²', 990, False, 30, 'lujo', None),
        ('Zoclo cerámico 8 cm',
         'Zoclo a tono con piso cerámico básico.',
         'ml', 88, False, 65, 'popular', None),
        ('Zoclo de porcelanato 10 cm',
         'Zoclo Interceramic a tono con el piso.',
         'ml', 165, False, 65, 'intermedio', None),
        ('Zoclo de granito pulido 10 cm',
         'Zoclo de granito natural a tono con el piso.',
         'ml', 290, False, 65, 'lujo', None),
    ]),

    # ── PAREDES Y PINTURA ─────────────────────────────────────────────────
    ('Paredes y Pintura', [
        ('Pintura vinílica Comex 2 manos (interiores + exteriores)',
         'Pintura vinílica en paredes y techos interiores, + fachada exterior.',
         'm²', 48, True, 320, 'popular', 'pintura'),
        ('Pasta niveladora + pintura premium Comex 3 manos',
         'Pasta de acabado fino + pintura Comex Ultrablock 3 manos en toda la casa.',
         'm²', 98, True, 320, 'intermedio', 'pintura'),
        ('Enlucido de yeso fino + pintura decorativa de diseño',
         'Aplanado muy liso con enlucido de yeso + pintura texturizada de alto diseño.',
         'm²', 185, True, 320, 'lujo', 'pintura'),
        ('Azulejo cerámico 20×20 en baño y cocina (1.5 m altura)',
         'Azulejo básico en zonas húmedas, 1.5 m de altura.',
         'm²', 285, True, 26, 'popular', None),
        ('Porcelanato Interceramic en paredes de baño y cocina',
         'Porcelanato de pared 30×60 en zonas húmedas.',
         'm²', 530, True, 26, 'intermedio', None),
        ('Porcelanato premium de piso a techo en todos los baños',
         'Porcelanato de alto brillo en paredes completas de todos los baños.',
         'm²', 860, True, 42, 'lujo', None),
        ('Piedra natural en acento de sala (lujo)',
         'Panel de piedra natural 10 cm en pared de acento de sala principal.',
         'm²', 980, False, 8, 'lujo', None),
    ]),

    # ── CARPINTERÍA ───────────────────────────────────────────────────────
    ('Carpintería', [
        ('Puertas interiores MDF básicas × 3',
         'Puertas de MDF con marco de madera y chapa básica, 3 juegos.',
         'global', 8700, True, 1, 'popular', 'puertas_int'),
        ('Puertas interiores madera sólida con diseño × 3',
         'Puertas de madera sólida con diseño en bajo relieve y cerradura de calidad.',
         'global', 14500, True, 1, 'intermedio', 'puertas_int'),
        ('Puertas interiores cedro/parota finas × 3',
         'Puertas de madera fina con diseño personalizado y cerradura de alta seguridad.',
         'global', 27000, True, 1, 'lujo', 'puertas_int'),
        ('Puerta principal de madera-MDF básica',
         'Puerta de acceso con chapa de seguridad y marco metálico.',
         'pza', 4800, True, 1, 'popular', 'puerta_principal'),
        ('Puerta principal con diseño madera-vidrio',
         'Puerta de acceso madera con ventana lateral, cerradura tipo palanca Dexter.',
         'pza', 8800, True, 1, 'intermedio', 'puerta_principal'),
        ('Puerta principal de lujo con vidrio esmerilado',
         'Puerta importada con vidrio esmerilado y cerradura biométrica de huella.',
         'pza', 23500, True, 1, 'lujo', 'puerta_principal'),
        ('Ventanas de aluminio básico (× 4)',
         'Ventanas corredizas de aluminio natural con vidrio sencillo, 4 piezas.',
         'global', 5200, True, 1, 'popular', 'ventanas'),
        ('Ventanas de aluminio anodizado con vidrio templado (× 4)',
         'Ventanas de aluminio anodizado oscuro, vidrio templado 6 mm, 4 piezas.',
         'global', 12000, True, 1, 'intermedio', 'ventanas'),
        ('Ventanas de PVC con doble vidrio hermético (× 4)',
         'Ventanas PVC blanco con doble acristalamiento, hermetismo y aislamiento térmico, 4 piezas.',
         'global', 22500, True, 1, 'lujo', 'ventanas'),
        ('Cocina integral de melamina blanca (3 ml)',
         'Muebles altos y bajos de melamina, cubierta de granito, 3 metros lineales.',
         'global', 12500, False, 1, 'intermedio', 'cocina_integral'),
        ('Cocina integral de madera con isla y granito',
         'Cocina de madera enchapada, isla central, cubierta de granito, iluminación bajo-mueble.',
         'global', 58000, False, 1, 'lujo', 'cocina_integral'),
        ('Closets de melamina (2 habitaciones)',
         'Armarios empotrados de melamina con riel corredero y organización interior.',
         'global', 13500, False, 1, 'intermedio', None),
        ('Closets de madera sólida con espejo (2 habitaciones)',
         'Armarios de madera con espejo de cuerpo completo e iluminación interior LED.',
         'global', 30000, False, 1, 'lujo', None),
        ('Cortineros ocultos embutidos (todos los cuartos)',
         'Sistema de cortineros embutidos en plafón para cortinas colgantes.',
         'ml', 880, False, 14, 'lujo', None),
    ]),

    # ── HERRERÍA Y SEGURIDAD ──────────────────────────────────────────────
    ('Herrería y Seguridad', [
        ('Rejas básicas de hierro cuadrado en ventanas',
         'Rejas de hierro cuadrado 1/2" en todas las ventanas.',
         'm²', 390, False, 9, 'popular', None),
        ('Rejas ornamentales en ventanas',
         'Rejas con diseño ornamental y acabado negro mate en ventanas.',
         'm²', 660, False, 9, 'intermedio', None),
        ('Herrería decorativa de hierro forjado',
         'Herrería fina con diseño personalizado, acabado antioxidante + esmalte.',
         'm²', 1250, False, 9, 'lujo', None),
        ('Portón de lámina galvanizada para cochera (manual)',
         'Portón de lámina galvanizada calibre 20, 3 m de ancho.',
         'pza', 5800, False, 1, 'popular', 'porton'),
        ('Portón de herrería con motor y control remoto',
         'Portón de herrería con motorización y 2 controles remotos.',
         'pza', 15000, False, 1, 'intermedio', 'porton'),
        ('Portón automático de acero con sensor y app',
         'Portón de acero inoxidable con sensor de apertura y control por app móvil.',
         'pza', 24000, False, 1, 'lujo', 'porton'),
        ('Sistema CCTV 4 cámaras IP + DVR',
         '4 cámaras IP Full HD exterior, DVR 8 canales, monitoreo remoto 24/7.',
         'global', 16500, False, 1, 'lujo', None),
    ]),

    # ── BAÑOS ─────────────────────────────────────────────────────────────
    ('Baños', [
        ('WC de dos piezas + lavabo empotrado (2 baños)',
         'WC básico marca Ideal Standard + lavabo empotrado, 2 juegos completos.',
         'global', 6400, True, 1, 'popular', 'sanitarios'),
        ('WC de una pieza + lavabo de sobreponer (2 baños)',
         'WC Interceramic de una pieza + lavabo de sobreponer, 2 juegos.',
         'global', 13500, True, 1, 'intermedio', 'sanitarios'),
        ('WC suspendido + lavabo de cubierta + bidet (2 baños)',
         'WC suspendido Duravit + lavabo de cubierta de diseño + bidet, 2 juegos.',
         'global', 45000, True, 1, 'lujo', 'sanitarios'),
        ('Regadera con barra y cortina',
         'Regadera básica, barra metálica y cortina de baño resistente.',
         'pza', 900, True, 1, 'popular', 'regadera'),
        ('Mampara de plástico deslizable para regadera',
         'Cabina de regadera con puerta deslizable de plástico templado.',
         'pza', 3500, True, 1, 'intermedio', 'regadera'),
        ('Cancel de cristal templado 8 mm para regadera',
         'Cancel con bisagra de acero inox y cristal templado 8 mm, medida estándar.',
         'pza', 9800, True, 1, 'lujo', 'regadera'),
        ('Sistema de ducha lluvia con mezcladora termostática',
         'Regadera lluvia 30×30 cm con mezcladora termostática Hansgrohe o similar.',
         'pza', 4800, False, 1, 'lujo', None),
        ('Accesorios de baño básicos – 2 baños',
         'Toallero, jabonera, portarrollos y gancho de plástico, 2 juegos.',
         'global', 1700, True, 1, 'popular', None),
        ('Accesorios de baño cromados Helvex – 2 baños',
         'Juego completo de accesorios cromados Helvex, 2 baños.',
         'global', 4200, True, 1, 'intermedio', None),
        ('Accesorios de baño latón/acero inox de lujo – 2 baños',
         'Accesorios de diseño en latón o acero inoxidable, 2 baños.',
         'global', 9200, True, 1, 'lujo', None),
    ]),

    # ── COCINA ────────────────────────────────────────────────────────────
    ('Cocina', [
        ('Tarja de acero inoxidable 1 tina Helvex',
         'Tarja de acero inox 1 tina, llave mezcladora incluida.',
         'pza', 1600, True, 1, 'popular', 'tarja'),
        ('Tarja de acero inox 2 tinas + escurridero',
         'Tarja Helvex 2 tinas con escurridero y llave mezcladora de cerámica.',
         'pza', 2900, True, 1, 'intermedio', 'tarja'),
        ('Tarja de granito negro + llave tipo cuello de ganso',
         'Tarja de granito negro + llave Moen o similar, estilo moderno.',
         'pza', 6800, True, 1, 'lujo', 'tarja'),
        ('Azulejo en zona de anafre y salpicadero',
         'Azulejo cerámico en área de preparación de alimentos, aprox. 4 m².',
         'm²', 290, True, 4, 'popular', None),
    ]),

    # ── EXTERIORES Y JARDINERÍA ───────────────────────────────────────────
    ('Exteriores y Jardinería', [
        ('Barda perimetral de block 1.8 m – 20 ml',
         'Barda de block de cemento 15×20×40 con mochetas, castillos y tapa.',
         'ml', 780, False, 20, None, None),
        ('Banqueta y andador exterior de concreto',
         'Banqueta al frente + andador perimetral de concreto f\'c=200.',
         'm²', 290, False, 30, None, None),
        ('Cochera techada con techo de lámina galvanizada',
         'Estructura metálica con lámina galvanizada pintada, 15 m².',
         'm²', 1250, False, 15, None, None),
        ('Jardín con pasto y plantas básicas',
         'Tierra vegetal, pasto San Agustín y plantas de ornato básicas.',
         'm²', 190, False, 20, None, None),
        ('Alberca pequeña 4×2 m (lujo)',
         'Alberca de concreto con recubrimiento de azulejo, filtro, bomba y escalera.',
         'pza', 90000, False, 1, 'lujo', None),
    ]),

    # ── HONORARIOS PROFESIONALES ──────────────────────────────────────────
    ('Honorarios Profesionales', [
        ('Elaboración de planos arquitectónicos – popular',
         'Proyecto ejecutivo firmado por arquitecto o ingeniero, sellado ante el Colegio. 500 MXN/m² × 80 m².',
         'global', 40000, True, 1, 'popular', 'planos'),
        ('Elaboración de planos arquitectónicos – intermedio',
         'Proyecto ejecutivo con perspectivas 3D y memoria de cálculo. 650 MXN/m² × 80 m².',
         'global', 52000, True, 1, 'intermedio', 'planos'),
        ('Elaboración de planos de lujo + renders 3D',
         'Proyecto ejecutivo completo con renders fotorrealistas y maqueta 3D. 800 MXN/m² × 80 m².',
         'global', 64000, True, 1, 'lujo', 'planos'),
        ('Actualización de planos después de entrega final (15%)',
         'Porcentaje de diseño por modificaciones solicitadas después de la entrega final.',
         'global', 8000, False, 1, None, None),
    ]),
]


def seed():
    with app.app_context():
        # Admin user
        if not User.query.filter_by(role='admin').first():
            admin = User(username='admin', email='admin@presupuesto.com', role='admin')
            admin.set_password('Admin1234!')
            db.session.add(admin)
            print('✓ Usuario admin creado  (admin@presupuesto.com / Admin1234!)')

        # House types
        ht_map = {}
        for data in HOUSE_TYPES:
            ht = HouseType.query.filter_by(finish_level=data['finish_level']).first()
            if not ht:
                ht = HouseType(**data)
                db.session.add(ht)
                db.session.flush()
                print(f'✓ Tipo de casa: {ht.name}')
            ht_map[data['finish_level']] = ht

        # Categories
        cat_map = {}
        for name, desc, order, icon in CATEGORIES:
            cat = Category.query.filter_by(name=name).first()
            if not cat:
                cat = Category(name=name, description=desc, order=order, icon=icon)
                db.session.add(cat)
                db.session.flush()
                print(f'✓ Categoría: {name}')
            cat_map[name] = cat

        # Components
        total_comps = 0
        for cat_name, comps in COMPONENTS:
            cat = cat_map.get(cat_name)
            if not cat:
                continue
            for (name, desc, unit, price, required, qty, finish, group) in comps:
                exists = Component.query.filter_by(name=name, category_id=cat.id).first()
                if exists:
                    continue
                ht_id = ht_map[finish].id if finish and finish in ht_map else None
                c = Component(
                    category_id=cat.id,
                    house_type_id=ht_id,
                    name=name,
                    description=desc,
                    unit=unit,
                    unit_price=price,
                    is_required=required,
                    default_quantity=qty,
                    group_name=group,
                )
                db.session.add(c)
                total_comps += 1

        db.session.commit()
        print(f'✓ {total_comps} componentes insertados.')
        print('✓ Base de datos lista.')


if __name__ == '__main__':
    seed()
