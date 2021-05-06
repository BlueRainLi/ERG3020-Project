# -*- coding: utf-8 -*-

from flask import flash, redirect, url_for, render_template
from sayhello import app, db
from sayhello.forms import HelloForm
from sayhello.models import Message
from sayhello.fact_entity_extraction import UserPredict
from sayhello.commands import forge, initdb
from sayhello.commonDataProcess import SingleFunction
from sayhello.mln_pack.mln_utils import write_mln_files
import os
from sayhello.mln_pack.mln_main import InferenceMachine, InfResult
import pickle


utils = UserPredict(debug_mode=False)

inf_res_url = os.path.dirname(app.root_path) + "/sayhello/mln_pack/result.txt"
mln_path = os.path.dirname(app.root_path) + "/sayhello/mln_pack/inference.mln"
db_path = os.path.dirname(app.root_path) + "/sayhello/mln_pack/inference.db"
func_url = os.path.dirname(app.root_path) + "/sayhello/commonData/func.pkl"
nen_url = os.path.dirname(app.root_path) + "/sayhello/commonData/nen.cmdata"


inf_machine = InferenceMachine(db_path=db_path, mln_path=mln_path)
inf_machine.engine(ask='steal', inf_res_url=inf_res_url)


@app.route('/', methods=['GET', 'POST'])
def index():

    fact_form = HelloForm()

    change = False

    if fact_form.validate_on_submit():
        change = True
        body = fact_form.body_textarea.data
        c_type = fact_form.c_type.data
        nl_body = body

        # Handle if user input facts
        if c_type == "Facts":
            query_result = utils.break_fact(body)

            print("*************************")
            print(query_result)
            print("*************************")

            if query_result:
                body = str(query_result)
            else:
                # seems like emotional
                c_type = "Emotional"

        if c_type == "Predicates":
            query_result = utils.break_logic(body)

            print("*************************")
            print(query_result)
            print("*************************")

            if query_result[0]:
                nl_body = query_result[0]
            else:
                # seems like with errors!
                c_type = "Emotional"

            body = query_result[1]

        if c_type == "Emotional":
            pass

        message = Message(body=body, c_type=c_type, nl_body=nl_body)
        db.session.add(message)
        db.session.commit()

        flash('Published 1 comment.')

        return redirect(url_for('index'))

    messages = Message.query.order_by(Message.timestamp.desc()).all()

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

    funcs = utils.funcDB.fetch()

    complex_functions = []
    for i in funcs:
        this = SingleFunction(i)
        complex_functions.append(this)

    result_stc = []
    with open(inf_res_url, mode="r") as file:
        for line in file:
            if "\n" in line:
                line = line.rstrip("\n")
                print(line)
                double = line.split(":")
                this = InfResult(double[0], double[1])
                result_stc.append(this)

    #
    functions_mln = []
    for i in funcs:
        try:
            functions_mln.append(i['function_mln'])
        except:
            print("bug handled!")
    write_mln_files(facts, predicates, functions_mln, nen_per, nen_org, nen_loc, db_path, mln_path)

    if change:
        inf_machine.engine(ask='steal', inf_res_url=inf_res_url)

    return render_template('index.html', fact_form=fact_form,
                           predicates=predicates, facts=facts, emotionals=emotionals, nen_per=nen_per,
                           nen_loc=nen_loc, nen_org=nen_org, functions=complex_functions,
                           infresult=result_stc)


@app.route('/refresh', methods=["GET"])
def refresh():
    db.drop_all()
    db.create_all()
    print("Deleted comments Database")

    # Clear Named entity
    # Clear caches:
    utils.commonDB.comments = {'PER': [], 'LOC': [], 'ORG': []}

    with open(nen_url, mode='w') as file:
        file.write("")

    # Clear Functions
    # Clear caches:
    utils.funcDB.comments = []

    with open(func_url, mode='w') as file:
        file.write("")

    print("Deleted named entity and functions")
    return redirect(url_for("index"))


@app.route('/refresh_inf', methods=["GET"])
def refresh_inf():

    answer_feedback = inf_machine.engine(ask='steal', inf_res_url=inf_res_url)

    print("%%%%")
    print("Refreshed inference result.")
    print("%%%%")

    if answer_feedback:
        flash('Inference result of Markov Logic Network updated.')
    else:
        flash('Inference result of Markov Logic Network is not available now, because the information '
              'is not yet enough or some errors occurred during inference. The result of last successful inference '
              'is displayed.')
    return redirect(url_for("index"))

