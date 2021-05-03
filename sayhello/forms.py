# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from wtforms import RadioField


class HelloForm(FlaskForm):
    # name = StringField('Name', validators=[DataRequired(), Length(1, 20)])
    """   c_type = RadioField('Type of comments',
                        choices=[('Facts','Facts'),('Predicates','Predicates'),('Emotional','Emotional')],
                        validators=[DataRequired(), Length(1, 20)])"""
    body_textarea = TextAreaField('Your comments', validators=[DataRequired(), Length(1, 200)])
    submit_btn = SubmitField(label='Submit')


class RenderForm(FlaskForm):
    submit = SubmitField()

