from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flaskr.db import get_db
from flaskr import db_utils
import collections
import os
import qrcode
import pandas

bp = Blueprint('survey', __name__)


@bp.route('/')
def index():
    return render_template('survey/index.html')


@bp.route('/add_poster', methods=('GET', 'POST'))
def add_poster():
    if request.method == 'POST':
        poster_name = request.form.get("poster-name")

        error = None
        if error is not None:
            flash(error)
        else:
            db = get_db()

            if not db_utils.check_if_value_in_table("posters", {"name": poster_name}):
                db.execute(
                    db_utils.insert_query_str(
                        'posters', ['name', 'qr_id', 'qr_value']),
                    (poster_name, 'qr122', '')
                )

                qr_img_file = create_qrcode_img(request.url_root, poster_name)

                return render_template('survey/add_poster.html', img_file=qr_img_file)
            else:
                flash("Poster name %s already exists" % poster_name)
            return redirect(url_for('survey.index'))

    return render_template('survey/add_poster.html', img_file=None)


@bp.route('/create/<path:poster_name>', methods=('GET', 'POST'))
@bp.route('/<path:poster_name>', methods=('GET', 'POST'))
@bp.route('/create', methods=('GET', 'POST'))
def create(poster_name=None):
    if poster_name is not None:
        poster_name = poster_name.replace("/", "")

    if request.method == 'POST':
        poster_name = request.form.get("poster-name")
        email = request.form.get("email")

        error = None
        
        if error is not None:
            flash(error)
        else:
            db = get_db()

            if not db_utils.check_if_value_in_table("users", {"email": email}):
                db.execute(db_utils.insert_query_str(
                    'users', ['email']), (email,))

            if not db_utils.check_if_value_in_table("posters", {"name": poster_name}):
                db.execute(db_utils.insert_query_str(
                    'posters', ['name', 'qr_id', 'qr_value']), (poster_name, 'qr122', ''))

            user_id = db_utils.get_table_id("users", {"email": email})
            poster_id = db_utils.get_table_id("posters", {"name": poster_name})
            if not db_utils.check_if_value_in_table("users_posters", {"users_id": user_id, "posters_id": poster_id}):
                db.execute(db_utils.insert_query_str("users_posters", [
                           'users_id', 'posters_id']), [user_id, poster_id])
            else:
                flash('%s and %s entry exist. Please update values now' %
                      (poster_name, email))
                return redirect(url_for('survey.update', poster_name=poster_name, email=email))
            
            users_posters_id = db_utils.get_table_id(
                "users_posters", {"users_id": user_id, "posters_id": poster_id})

            if not db_utils.check_if_value_in_table("surveys", {"users_posters_id": users_posters_id}):
                db.execute(
                    db_utils.insert_query_str("surveys",
                     ['comment', 'users_posters_id']),
                    ["", users_posters_id]
                )

            survey_id = db_utils.get_table_id("surveys", {"users_posters_id": users_posters_id})

            question_answer_dict = map_question_answer(request.form.items())
            db_utils.run_insert_answers_query(question_answer_dict.items(), survey_id)

            db.commit()
            return redirect(url_for('survey.index'))

    db = get_db()
    questions = db.execute(
        'SELECT id, question'
        ' FROM questions'
        ' ORDER BY id'
    ).fetchall()
    return render_template('survey/create.html', poster_name=poster_name, questions=questions)


@bp.route('/<poster_name>/<email>', methods=('GET', 'POST'))
def update(poster_name, email=None):
    if request.method == 'POST':
        poster_name = request.form.get("poster-name")
        email = request.form.get("email")

        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()

            survey_id = db_utils.get_survey_id(email, poster_name)
            
            question_answer_dict = map_question_answer(request.form.items())
            db_utils.run_insert_answers_query(question_answer_dict.items(), survey_id)

            db.commit()
            return redirect(url_for('survey.index'))
    else:
        surveys = db_utils.get_survey(poster_name, email)
        if len(surveys) == 0:
            db = get_db()
            questions = db.execute(
                'SELECT id, question'
                ' FROM questions'
                ' ORDER BY id'
            ).fetchall()

            questions_list = []
            for s in questions:
                questions_list.append(tuple(s))
            if db_utils.check_if_value_in_table("posters", {"name": poster_name}):
                return redirect(url_for('survey.create', poster_name=poster_name, questions=questions_list))

        return render_template('survey/update.html', poster_name=poster_name, email=email, responses=surveys)


@bp.route('/view_all_surveys')
def view_all_surveys():
    headers = ['id', 'email', 'Poster Name']
    questions = pandas.read_sql_query(
        "SELECT * FROM questions", get_db())['question'].values.tolist()
    headers.extend(questions)
    
    db_utils.run_survey_create_view_query()
    surveys = db_utils.pivot_all_surveys_table(questions)

    return render_template('survey/view_all_surveys.html', headers=headers, surveys=surveys.values.tolist())


def create_qrcode_img(url, poster_name):
    img = qrcode.make(f'{url}{poster_name}')
    img_file_name = f'qr_code_{poster_name.replace(" ", "_")}.png'
    
    img_dir = 'flaskr/static/images/'
    if not os.path.isdir(img_dir):
        os.mkdir(img_dir)
    img.save(f'{img_dir}{img_file_name}')

    return img_file_name

def map_question_answer(items):
    question_answer_dict = collections.OrderedDict()
    for key, val in items:
        if key.startswith("a-"):
            question_answer_dict[int(key.replace('a-for-q', ''))] = int(val)
    return question_answer_dict