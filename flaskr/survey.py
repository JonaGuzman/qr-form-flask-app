from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
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
            cursor = db.cursor()

            if not db_utils.check_if_value_in_table("posters", {"name": poster_name}, cursor):
                db.execute(
                    db_utils.insert_query_str(
                        'posters', ['name', 'qr_id', 'qr_value']),
                    (poster_name, 'qr122', '')
                )

                img_file_name = create_qrcode_img(
                    request.url_root, poster_name)

                return render_template('survey/add_poster.html', img_file=img_file_name)
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
        question_answer_dict = collections.OrderedDict()
        for key, val in request.form.items():
            if key.startswith("a-"):
                question_answer_dict[int(
                    key.replace('a-for-q', ''))] = int(val)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()

            if not db_utils.check_if_value_in_table("users", {"email": email}, cursor):
                db.execute(db_utils.insert_query_str(
                    'users', ['email']), (email,))

            if not db_utils.check_if_value_in_table("posters", {"name": poster_name}, cursor):
                db.execute(db_utils.insert_query_str(
                    'posters', ['name', 'qr_id', 'qr_value']), (poster_name, 'qr122', ''))

            user_id = db_utils.get_table_id("users", {"email": email}, cursor)
            poster_id = db_utils.get_table_id(
                "posters", {"name": poster_name}, cursor)
            if not db_utils.check_if_value_in_table("users_posters", {"users_id": user_id, "posters_id": poster_id}, cursor):
                db.execute(db_utils.insert_query_str("users_posters", [
                           'users_id', 'posters_id']), [user_id, poster_id])
            else:
                flash('%s and %s entry exist. Please update values now' %
                      (poster_name, email))
                return redirect(url_for('survey.update', poster_name=poster_name, email=email))
            
            users_posters_id = db_utils.get_table_id(
                "users_posters", {"users_id": user_id, "posters_id": poster_id}, cursor)

            if not db_utils.check_if_value_in_table("surveys", {"users_posters_id": users_posters_id}, cursor):
                db.execute(db_utils.insert_query_str("surveys", ['comment', 'users_posters_id']),
                    ["", users_posters_id])

            survey_id = db_utils.get_table_id(
                "surveys", {"users_posters_id": users_posters_id}, cursor)

            for q, a in question_answer_dict.items():
                sql = db_utils.insert_query_str(
                    "answers", ["answer", "questions_id", "surveys_id"])
                val = [a, q, survey_id]
                db.execute(sql, val)

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
            cursor = db.cursor()

            survey_id = db_utils.get_survey_id(email, poster_name, cursor)
            question_answer_dict = collections.OrderedDict()
            for key, val in request.form.items():
                if key.startswith("a-"):
                    question_answer_dict[int(key.replace('a-for-q', ''))] = int(val)

            for q, a in question_answer_dict.items():
                sql = db_utils.update_query(
                    "answers", ["answer"], {'surveys_id': survey_id, 'questions_id': q})
                db.execute(sql, [a, ])

            db.commit()
            return redirect(url_for('survey.index'))
    else:
        surveys = get_survey(poster_name, email)
        # TODO: Pass in Question and Answer values into surveys when going to site/poster_name
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
            if db_utils.check_if_value_in_table("posters", {"name": poster_name}, db.cursor()):
                return redirect(url_for('survey.create', poster_name=poster_name, questions=questions_list))

        return render_template('survey/update.html', poster_name=poster_name, email=email, responses=surveys)


def get_survey(poster_name, email):
    survey = get_db().execute(
        """SELECT s.id, q.question, a.answer, p.name, u.email, s.comment, p.qr_value
        FROM surveys s
        LEFT JOIN users_posters up ON up.id = users_posters_id
        LEFT JOIN answers a ON a.surveys_id = s.id
        LEFT JOIN questions q ON q.id = a.questions_id
        LEFT JOIN posters p ON p.id = up.posters_id
        LEFT JOIN users u ON u.id = up.users_id
        WHERE p.name=? AND u.email=?
        ORDER BY a.questions_id""",
        (poster_name, email)
    ).fetchall()
    if survey is None:
        abort(404, "Survey id {0} doesn't exist.".format(id))

    return survey


@bp.route('/view_all_surveys')
def view_all_surveys():
    headers = ['id', 'email', 'Poster Name']
    questions = pandas.read_sql_query(
        "SELECT * FROM questions", get_db())['question'].values.tolist()
    headers.extend(questions)

    get_db().execute("""DROP VIEW IF EXISTS survey_view""")
    survey_view = get_db().execute(
        """CREATE VIEW survey_view (id, question, answer, name, email, comment, qr_value) AS
        SELECT s.id, q.question, a.answer, p.name, u.email, s.comment, p.qr_value
        FROM surveys s
        LEFT JOIN users_posters up ON up.id = users_posters_id
        LEFT JOIN answers a ON a.surveys_id = s.id
        LEFT JOIN questions q ON q.id = a.questions_id
        LEFT JOIN posters p ON p.id = up.posters_id
        LEFT JOIN users u ON u.id = up.users_id
        ORDER BY q.id""")
    surveys = pandas.read_sql_query(
        """SELECT id, email, name,
        %s
        FROM (
            SELECT survey_view.*,
            row_number() over (partition by email order by id) as seq
            from survey_view
            ) survey_view
            GROUP BY email""" % db_utils.prep_case_seq(questions), get_db())
    return render_template('survey/view_all_surveys.html', headers=headers, surveys=surveys.values.tolist())


def create_qrcode_img(url, poster_name):
    img = qrcode.make(f'{url}{poster_name}')
    img_file_name = f'qr_code_{poster_name.replace(" ", "_")}.png'
    img_dir = 'flaskr/static/images/'
    if not os.path.isdir(img_dir):
        os.mkdir(img_dir)
    img.save(f'{img_dir}{img_file_name}')

    return img_file_name
