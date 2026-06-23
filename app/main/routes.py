import json
import bleach
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.main import main_bp
from app.models import HouseType, Category, Component, Quote, QuoteItem
from app.floorplan import render_svg


@main_bp.route('/')
@login_required
def index():
    house_types = HouseType.query.all()
    return render_template('main/index.html', house_types=house_types)


@main_bp.route('/configurador/<int:house_type_id>')
@login_required
def configurador(house_type_id):
    house_type = HouseType.query.get_or_404(house_type_id)
    categories = Category.query.order_by(Category.order).all()
    # Components for this house type OR shared (house_type_id is NULL)
    components_by_cat = {}
    for cat in categories:
        comps = Component.query.filter(
            Component.category_id == cat.id,
            Component.is_active == True,
            db.or_(
                Component.house_type_id == house_type_id,
                Component.house_type_id.is_(None)
            )
        ).all()
        if comps:
            components_by_cat[cat] = comps
    return render_template('main/configurador.html',
                           house_type=house_type,
                           components_by_cat=components_by_cat)


@main_bp.route('/cotizacion/guardar', methods=['POST'])
@login_required
def guardar_cotizacion():
    house_type_id = request.form.get('house_type_id', type=int)
    if not house_type_id:
        abort(400)
    house_type = HouseType.query.get_or_404(house_type_id)

    quote_name = bleach.clean(request.form.get('quote_name', 'Mi Cotización')[:100])
    land_m2 = request.form.get('land_m2', 120.0, type=float)
    construction_m2 = request.form.get('construction_m2', 80.0, type=float)
    include_supervision = request.form.get('include_supervision') == '1'
    include_contingency = request.form.get('include_contingency') == '1'

    # Validate m2 values
    land_m2 = max(50.0, min(5000.0, land_m2))
    construction_m2 = max(30.0, min(land_m2, construction_m2))

    # Parse selected components JSON
    try:
        items_data = json.loads(request.form.get('items_json', '[]'))
    except (json.JSONDecodeError, ValueError):
        flash('Error al procesar los componentes.', 'danger')
        return redirect(url_for('main.configurador', house_type_id=house_type_id))

    # Validate each component belongs to this house type
    allowed_ids = {c.id for c in Component.query.filter(
        Component.is_active == True,
        db.or_(Component.house_type_id == house_type_id, Component.house_type_id == None)
    ).all()}

    quote = Quote(
        user_id=current_user.id,
        house_type_id=house_type_id,
        name=quote_name,
        land_m2=land_m2,
        construction_m2=construction_m2
    )
    db.session.add(quote)
    db.session.flush()

    subtotal = 0.0
    for item in items_data:
        comp_id = int(item.get('id', 0))
        qty = float(item.get('qty', 1))
        if comp_id not in allowed_ids:
            continue
        comp = db.session.get(Component, comp_id)
        if not comp:
            continue
        qty = max(1, min(10000, round(qty)))
        sub = round(comp.unit_price * qty, 2)
        qi = QuoteItem(
            quote_id=quote.id,
            component_id=comp_id,
            quantity=qty,
            unit_price=comp.unit_price,
            subtotal=sub
        )
        db.session.add(qi)
        subtotal += sub

    quote.subtotal = round(subtotal, 2)
    quote.supervision_pct = 15.0 if include_supervision else 0.0
    quote.supervision_amount = round(subtotal * 0.15, 2) if include_supervision else 0.0
    quote.contingency_pct = 10.0 if include_contingency else 0.0
    quote.contingency_amount = round(subtotal * 0.10, 2) if include_contingency else 0.0
    quote.total_price = round(subtotal + quote.supervision_amount + quote.contingency_amount, 2)

    db.session.commit()
    flash('Cotización guardada exitosamente.', 'success')
    return redirect(url_for('main.cotizacion', quote_id=quote.id))


@main_bp.route('/cotizacion/<int:quote_id>')
@login_required
def cotizacion(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    if quote.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    categories = Category.query.order_by(Category.order).all()
    items_by_cat = {}
    for item in quote.items:
        cat = item.component.category
        if cat not in items_by_cat:
            items_by_cat[cat] = []
        items_by_cat[cat].append(item)
    floorplan_svg, floorplan_rooms = render_svg(quote.construction_m2)
    return render_template('main/cotizacion.html', quote=quote, items_by_cat=items_by_cat,
                           floorplan_svg=floorplan_svg, floorplan_rooms=floorplan_rooms)


@main_bp.route('/mis-cotizaciones')
@login_required
def mis_cotizaciones():
    quotes = Quote.query.filter_by(user_id=current_user.id).order_by(Quote.created_at.desc()).all()
    return render_template('main/mis_cotizaciones.html', quotes=quotes)


@main_bp.route('/cotizacion/<int:quote_id>/eliminar', methods=['POST'])
@login_required
def eliminar_cotizacion(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    if quote.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    db.session.delete(quote)
    db.session.commit()
    flash('Cotización eliminada.', 'info')
    return redirect(url_for('main.mis_cotizaciones'))
