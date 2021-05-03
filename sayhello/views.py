# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask import flash, redirect, url_for, render_template

from sayhello import app, db
from sayhello.forms import HelloForm
from sayhello.models import Message

# This is AI algorithm
from sayhello.fact_entity_extraction import UserPredict

from sayhello.commands import forge, initdb

import os

#
utils = UserPredict(debug_mode=False)


#


@app.route('/', methods=['GET', 'POST'])
def index():

    """    type_form = HelloForm()

    if type_form.submit():
        print("Query Caught!")"""


    fact_form = HelloForm()

    if fact_form.validate_on_submit():
        body = fact_form.body_textarea.data
        c_type = "Facts"

        nl_body = body

        # Handle if user input facts
        if c_type == "Facts":
            query_result = utils.query(body)

            if query_result:
                atom_clau = query_result[1]
                # print(atom_clause)
                body = str(atom_clau)
                entity = str(query_result[2])

                # Commit to entity database
                for i in range(len(query_result[3])):
                    utils.commonDB.add(query_result[3][i], query_result[4][i])
                    print(query_result[3][i], query_result[4][i])
                utils.commonDB.commit()  # Commit your comments

                utils.funcDB.add(query_result[0]['verb'],query_result[4])
                utils.funcDB.commit()

            else:
                # seems like emotional!
                entity = None
                c_type = "Emotional"


        message = Message(body=body, c_type=c_type, nl_body=nl_body, entity=entity)
        db.session.add(message)
        db.session.commit()

        flash('Published 1 comment.')
        return redirect(url_for('index'))

    messages = Message.query.order_by(Message.timestamp.desc()).all()

    # print(messages)

    facts = []
    predicates = []
    emotionals = []
    for i in messages:
        if i.c_type == "Facts":
            facts.append(i)
        elif i.c_type == "Predicates":
            predicates.append(i)
        elif i.c_type == "Emotional":
            emotionals.append(i)

    entity_dict = utils.commonDB.fetch()
    nen_per = ','.join(entity_dict['PER'])
    nen_loc = ','.join(entity_dict['LOC'])
    nen_org = ','.join(entity_dict['ORG'])
    functions = utils.funcDB.fetch()

    return render_template('index.html', fact_form=fact_form,
                           predicates=predicates, facts=facts, emotionals=emotionals, nen_per=nen_per,
                           nen_loc=nen_loc, nen_org=nen_org, functions=functions)


@app.route('/refresh', methods=["GET"])
def refresh():
    db.drop_all()
    db.create_all()
    print("Deleted comments Database")

    # Clear Named entity
    nen_url = os.path.dirname(app.root_path) + "/sayhello/commonData/nen.cmdata"

    # Clear caches:
    utils.commonDB.comments = {'PER': [], 'LOC': [], 'ORG': []}
    print(nen_url)

    with open(nen_url, mode='w') as file:
        file.write("")

    # Clear Functions
    nen_url = os.path.dirname(app.root_path) + "/sayhello/commonData/func.cmdata"
    # Clear caches:
    utils.funcDB.comments = []
    print(nen_url)

    with open(nen_url, mode='w') as file:
        file.write("")

    return redirect(url_for("index"))

