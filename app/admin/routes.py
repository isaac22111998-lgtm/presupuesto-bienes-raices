import bleach
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
from app import db
from app.admin import admin_bp
from app.admin.forms import ComponentForm
from app.decorators import admin_required
from app.models import Component, Category, HouseType, User, Quote


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    stats = {
        'users': User.query.filter_by(role='user').count(),
        'quotes': Quote.query.count(),
        'components': Component.query.filter_by(is_active=True).count(),
        'categories': Category.query.count(),
    }
    recent_quotes = Quote.query.order_by(Quote.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html', stats=stats, recent_quotes=recent_quotes)


@admin_bp.route('/components')
@login_required
@admin_required
def components():
    cats = Category.query.order_by(Category.order).all()
    house_types = HouseType.query.all()
    cat_filter = request.args.get('cat', type=int)
    ht_filter = request.args.get('ht', type=int)
    query = Component.query
    if cat_filter:
        query = query.filter_by(category_id=cat_filter)
    if ht_filter:
        query = query.filter_by(house_type_id=ht_filter)
    comps = query.order_by(Component.category_id, Component.id).all()
    return render_template('admin/components.html', components=comps,
                           categories=cats, house_types=house_types,
                           cat_filter=cat_filter, ht_filter=ht_filter)


@admin_bp.route('/components/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def new_component():
    form = ComponentForm()
    cats = Category.query.order_by(Category.order).all()
    house_types = HouseType.query.all()
    form.category_id.choices = [(c.id, c.name) for c in cats]
    form.house_type_id.choices = [(0, 'Todos los tipos')] + [(h.id, h.name) for h in house_types]
    if form.validate_on_submit():
        comp = Component(
            name=bleach.clean(form.name.data.strip()),
            description=bleach.clean(form.description.data or ''),
            category_id=form.category_id.data,
            house_type_id=form.house_type_id.data if form.house_type_id.data != 0 else None,
            unit=form.unit.data,
            unit_price=form.unit_price.data,
            default_quantity=form.default_quantity.data,
            is_required=form.is_required.data,
            group_name=bleach.clean(form.group_name.data or '') or None,
        )
        db.session.add(comp)
        db.session.commit()
        flash('Componente agregado.', 'success')
        return redirect(url_for('admin.components'))
    return render_template('admin/component_form.html', form=form, title='Nuevo Componente')


@admin_bp.route('/components/<int:comp_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_component(comp_id):
    comp = Component.query.get_or_404(comp_id)
    form = ComponentForm(obj=comp)
    cats = Category.query.order_by(Category.order).all()
    house_types = HouseType.query.all()
    form.category_id.choices = [(c.id, c.name) for c in cats]
    form.house_type_id.choices = [(0, 'Todos los tipos')] + [(h.id, h.name) for h in house_types]
    if request.method == 'GET':
        form.house_type_id.data = comp.house_type_id or 0
    if form.validate_on_submit():
        comp.name = bleach.clean(form.name.data.strip())
        comp.description = bleach.clean(form.description.data or '')
        comp.category_id = form.category_id.data
        comp.house_type_id = form.house_type_id.data if form.house_type_id.data != 0 else None
        comp.unit = form.unit.data
        comp.unit_price = form.unit_price.data
        comp.default_quantity = form.default_quantity.data
        comp.is_required = form.is_required.data
        comp.group_name = bleach.clean(form.group_name.data or '') or None
        db.session.commit()
        flash('Componente actualizado.', 'success')
        return redirect(url_for('admin.components'))
    return render_template('admin/component_form.html', form=form, title='Editar Componente', comp=comp)


@admin_bp.route('/components/<int:comp_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_component(comp_id):
    comp = Component.query.get_or_404(comp_id)
    comp.is_active = not comp.is_active
    db.session.commit()
    status = 'activado' if comp.is_active else 'desactivado'
    flash(f'Componente {status}.', 'info')
    return redirect(url_for('admin.components'))


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin():
        flash('No puedes desactivar a un administrador.', 'warning')
        return redirect(url_for('admin.users'))
    user.is_active = not user.is_active
    db.session.commit()
    flash(f'Usuario {"activado" if user.is_active else "desactivado"}.', 'info')
    return redirect(url_for('admin.users'))


@admin_bp.route('/cotizaciones')
@login_required
@admin_required
def quotes():
    all_quotes = Quote.query.order_by(Quote.created_at.desc()).all()
    return render_template('admin/quotes.html', quotes=all_quotes)
