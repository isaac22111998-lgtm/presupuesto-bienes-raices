from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ComponentForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(2, 200)])
    description = TextAreaField('Descripción', validators=[Optional(), Length(0, 500)])
    category_id = SelectField('Categoría', coerce=int, validators=[DataRequired()])
    house_type_id = SelectField('Tipo de Casa', coerce=int)
    unit = SelectField('Unidad', choices=[
        ('global', 'Global'), ('m²', 'm²'), ('ml', 'ml (metro lineal)'),
        ('m³', 'm³'), ('pza', 'Pieza'), ('kg', 'kg'), ('lt', 'Litros')
    ])
    unit_price = FloatField('Precio por unidad (MXN)', validators=[DataRequired(), NumberRange(min=0)])
    default_quantity = FloatField('Cantidad por defecto', validators=[DataRequired(), NumberRange(min=0.01)], default=1.0)
    is_required = BooleanField('Componente obligatorio')
    group_name = StringField('Nombre de grupo (opcional)', validators=[Optional(), Length(0, 100)])
    submit = SubmitField('Guardar')
