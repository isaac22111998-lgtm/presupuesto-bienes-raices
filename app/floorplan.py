"""
Generador de plano esquemático simple (vista superior aproximada).
No sustituye el plano oficial firmado por el arquitecto/ingeniero responsable;
es solo una referencia visual de cómo podría distribuirse la construcción.
"""

ROOM_COLORS = [
    '#2d3748', '#374151', '#3f3f56', '#2f3a4f', '#3a4a3a', '#4a3a3a', '#3a3a4a', '#454038',
]

# Distribución para casas de 60 m² de construcción o más (3 recámaras)
LAYOUT_FULL = [
    {'depth_pct': 0.40, 'rooms': [('Sala - Comedor', 0.62), ('Cocina', 0.38)]},
    {'depth_pct': 0.32, 'rooms': [('Recámara Principal', 0.50), ('Baño 1', 0.20), ('Pasillo', 0.30)]},
    {'depth_pct': 0.28, 'rooms': [('Recámara 2', 0.42), ('Recámara 3', 0.32), ('Baño 2', 0.26)]},
]

# Distribución compacta para construcciones menores a 60 m² (2 recámaras)
LAYOUT_COMPACT = [
    {'depth_pct': 0.45, 'rooms': [('Sala - Comedor', 0.60), ('Cocina', 0.40)]},
    {'depth_pct': 0.55, 'rooms': [('Recámara Principal', 0.45), ('Recámara 2', 0.35), ('Baño', 0.20)]},
]


def _layout_for(construction_m2):
    return LAYOUT_FULL if construction_m2 >= 60 else LAYOUT_COMPACT


def compute_rooms(construction_m2):
    """Devuelve (rooms, width, depth) en metros, distribuyendo el área en un rectángulo regular."""
    aspect = 1.25  # relación frente : fondo
    width = (construction_m2 * aspect) ** 0.5
    depth = construction_m2 / width

    layout = _layout_for(construction_m2)
    rooms = []
    y = 0.0
    for row in layout:
        row_h = row['depth_pct'] * depth
        x = 0.0
        for name, pct in row['rooms']:
            room_w = pct * width
            rooms.append({
                'name': name,
                'x': x, 'y': y, 'w': room_w, 'h': row_h,
                'area_m2': round(room_w * row_h, 1),
            })
            x += room_w
        y += row_h
    return rooms, width, depth


def render_svg(construction_m2):
    """Genera el SVG del plano esquemático. Devuelve (svg_str, rooms)."""
    construction_m2 = max(20.0, min(500.0, construction_m2 or 80.0))
    rooms, width, depth = compute_rooms(construction_m2)

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

    # Contorno exterior
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

    # Marca de entrada al frente
    door_w = max(18.0, 0.9 * scale)
    door_x = ox + (width * 0.5) * scale - door_w / 2
    parts.append(f'<rect x="{door_x:.1f}" y="{oy - 3:.1f}" width="{door_w:.1f}" height="6" fill="#f59e0b"/>')
    parts.append(
        f'<text x="{ox + ow / 2:.1f}" y="{oy - 8:.1f}" text-anchor="middle" font-size="10" '
        f'fill="#f59e0b" font-family="sans-serif">Entrada</text>'
    )

    parts.append('</svg>')
    return ''.join(parts), rooms
