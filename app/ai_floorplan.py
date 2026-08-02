"""
Generador de plano esquemático usando IA (Claude Haiku).
Claude devuelve la distribución de cuartos como JSON; nosotros lo renderizamos como SVG
para mantener el estilo visual coherente con la app.
Si la API no está configurada o falla, se usa el layout estático de respaldo.
"""
import json
import logging
from flask import current_app

logger = logging.getLogger(__name__)

ROOM_COLORS = [
    '#2d3748', '#374151', '#3f3f56', '#2f3a4f',
    '#3a4a3a', '#4a3a3a', '#3a3a4a', '#454038',
]

# Layout de respaldo (mismo que el anterior floorplan.py)
_FALLBACK_FULL = [
    {'depth_pct': 0.40, 'rooms': [('Sala - Comedor', 0.62), ('Cocina', 0.38)]},
    {'depth_pct': 0.32, 'rooms': [('Recámara Principal', 0.50), ('Baño 1', 0.20), ('Pasillo', 0.30)]},
    {'depth_pct': 0.28, 'rooms': [('Recámara 2', 0.42), ('Recámara 3', 0.32), ('Baño 2', 0.26)]},
]
_FALLBACK_COMPACT = [
    {'depth_pct': 0.45, 'rooms': [('Sala - Comedor', 0.60), ('Cocina', 0.40)]},
    {'depth_pct': 0.55, 'rooms': [('Recámara Principal', 0.45), ('Recámara 2', 0.35), ('Baño', 0.20)]},
]


def generate_dalle_image(construction_m2, finish_level='popular'):
    """
    Genera una imagen del plano con DALL-E 3.
    Devuelve string base64 o lanza excepción si falla.
    La imagen se genera una sola vez y se guarda en la BD para no repetir el costo.
    """
    import openai

    api_key = current_app.config.get('OPENAI_API_KEY', '')
    if not api_key:
        raise ValueError('OPENAI_API_KEY no configurada')

    client = openai.OpenAI(api_key=api_key)

    bedrooms = 3 if construction_m2 >= 60 else 2
    bathrooms = 2 if construction_m2 >= 60 else 1
    finish_map = {'popular': 'económico', 'intermedio': 'intermedio', 'lujo': 'de lujo'}
    finish_str = finish_map.get(finish_level, 'estándar')

    prompt = (
        f"2D architectural floor plan, top-down view, {construction_m2:.0f} square meter "
        f"single-story house with {finish_str} finish level. "
        f"Rooms: sala-comedor, cocina, {bedrooms} recámaras, {bathrooms} baños"
        + (", pasillo" if bedrooms >= 3 else "") + ". "
        "Clean technical drawing style, black thin lines on white background, "
        "each room clearly delimited and labeled in Spanish with its area in m², "
        "entrance marked at the front, no furniture, no 3D perspective, flat 2D view, "
        "professional minimalist architectural style."
    )

    response = client.images.generate(
        model='dall-e-3',
        prompt=prompt,
        size='1024x1024',
        quality='standard',
        response_format='b64_json',
        n=1,
    )
    return response.data[0].b64_json


def _fallback_rooms(construction_m2):
    """Distribución estática cuando la API no está disponible."""
    aspect = 1.25
    width = (construction_m2 * aspect) ** 0.5
    depth = construction_m2 / width
    layout = _FALLBACK_FULL if construction_m2 >= 60 else _FALLBACK_COMPACT
    rooms, y = [], 0.0
    for row in layout:
        row_h = row['depth_pct'] * depth
        x = 0.0
        for name, pct in row['rooms']:
            room_w = pct * width
            rooms.append({'name': name, 'x': x, 'y': y, 'w': room_w, 'h': row_h,
                          'area_m2': round(room_w * row_h, 1)})
            x += room_w
        y += row_h
    return rooms, width, depth


def _ai_rooms(construction_m2, finish_level='popular'):
    """
    Llama a Gemini Flash para obtener la distribución de cuartos.
    Devuelve (rooms, width, depth) o lanza excepción si falla.
    """
    import google.generativeai as genai

    api_key = current_app.config.get('GEMINI_API_KEY', '')
    if not api_key:
        raise ValueError('GEMINI_API_KEY no configurada')

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    bedrooms = 3 if construction_m2 >= 60 else 2
    bathrooms = 2 if construction_m2 >= 60 else 1
    aspect = 1.25
    width = round((construction_m2 * aspect) ** 0.5, 2)
    depth = round(construction_m2 / width, 2)

    prompt = f"""Eres un arquitecto que distribuye cuartos en una planta baja rectangular.
Terreno de construcción: {width} m de frente x {depth} m de fondo = {construction_m2} m² totales.
Nivel de acabado: {finish_level}.
Cuartos requeridos: sala-comedor, cocina, {bedrooms} recámaras, {bathrooms} baños, pasillo (si cabe).

Devuelve ÚNICAMENTE un JSON válido con este esquema (sin markdown, sin texto extra):
{{
  "rooms": [
    {{"name": "Sala - Comedor", "x_pct": 0.0, "y_pct": 0.0, "w_pct": 0.62, "h_pct": 0.40}},
    ...
  ]
}}
Reglas:
- x_pct + w_pct <= 1.0 para cada cuarto
- y_pct + h_pct <= 1.0 para cada cuarto
- Los cuartos NO deben traslaparse
- Los valores son porcentajes del ancho total ({width} m) y fondo total ({depth} m) respectivamente
- Ordena los cuartos de frente a fondo (sala al norte/entrada, recámaras al fondo)
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()
    # Gemini a veces envuelve en markdown ```json ... ```
    if raw.startswith('```'):
        raw = raw.split('```')[1]
        if raw.startswith('json'):
            raw = raw[4:]
    data = json.loads(raw.strip())

    rooms = []
    for r in data['rooms']:
        rw = r['w_pct'] * width
        rh = r['h_pct'] * depth
        rx = r['x_pct'] * width
        ry = r['y_pct'] * depth
        rooms.append({
            'name': r['name'],
            'x': rx, 'y': ry, 'w': rw, 'h': rh,
            'area_m2': round(rw * rh, 1),
        })

    return rooms, width, depth


def compute_rooms(construction_m2, finish_level='popular'):
    """
    Intenta obtener distribución de cuartos via IA; usa fallback si falla.
    Devuelve (rooms, width, depth, used_ai).
    """
    try:
        rooms, width, depth = _ai_rooms(construction_m2, finish_level)
        return rooms, width, depth, True
    except Exception as e:
        logger.warning('AI floor plan falló, usando fallback estático: %s', e)
        rooms, width, depth = _fallback_rooms(construction_m2)
        return rooms, width, depth, False


def render_svg(construction_m2, finish_level='popular'):
    """
    Genera el SVG del plano esquemático.
    Devuelve (svg_str, rooms, used_ai).
    """
    construction_m2 = max(20.0, min(500.0, construction_m2 or 80.0))
    rooms, width, depth, used_ai = compute_rooms(construction_m2, finish_level)

    padding = 1.0
    scale = 360 / max(width, depth)
    svg_w = width * scale + padding * 2 * scale
    svg_h = depth * scale + padding * 2 * scale

    parts = [
        f'<svg viewBox="0 0 {svg_w:.0f} {svg_h:.0f}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;max-width:480px;height:auto;background:#0d1117;border-radius:8px;">'
    ]

    ox, oy = padding * scale, padding * scale
    ow, oh = width * scale, depth * scale

    parts.append(
        f'<rect x="{ox:.1f}" y="{oy:.1f}" width="{ow:.1f}" height="{oh:.1f}" '
        f'fill="none" stroke="#e94560" stroke-width="3" rx="2"/>'
    )

    for i, r in enumerate(rooms):
        rx = ox + r['x'] * scale
        ry = oy + r['y'] * scale
        rw = r['w'] * scale
        rh = r['h'] * scale
        color = ROOM_COLORS[i % len(ROOM_COLORS)]
        parts.append(
            f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{rw:.1f}" height="{rh:.1f}" '
            f'fill="{color}" stroke="#30363d" stroke-width="1.5"/>'
        )
        cx, cy = rx + rw / 2, ry + rh / 2
        font_size = min(13, max(7, rw / 9))
        parts.append(
            f'<text x="{cx:.1f}" y="{cy - 6:.1f}" text-anchor="middle" '
            f'font-size="{font_size:.0f}" fill="#e6edf3" font-family="sans-serif" font-weight="600">'
            f'{r["name"]}</text>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{cy + 10:.1f}" text-anchor="middle" '
            f'font-size="{font_size * 0.85:.0f}" fill="#8b949e" font-family="sans-serif">'
            f'{r["area_m2"]:.0f} m²</text>'
        )

    # Marca de entrada
    door_w = max(18.0, 0.9 * scale)
    door_x = ox + (width * 0.5) * scale - door_w / 2
    parts.append(f'<rect x="{door_x:.1f}" y="{oy - 3:.1f}" width="{door_w:.1f}" height="6" fill="#f59e0b"/>')
    parts.append(
        f'<text x="{ox + ow / 2:.1f}" y="{oy - 8:.1f}" text-anchor="middle" font-size="10" '
        f'fill="#f59e0b" font-family="sans-serif">Entrada</text>'
    )

    # Indicador de si fue generado por IA
    if used_ai:
        parts.append(
            f'<text x="{ox + ow - 4:.1f}" y="{oy + oh + 14:.1f}" text-anchor="end" font-size="9" '
            f'fill="#6e7681" font-family="sans-serif">✦ Distribución generada por Gemini</text>'
        )

    parts.append('</svg>')
    return ''.join(parts), rooms
