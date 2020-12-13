from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.db import get_db
from flaskr import db_utils
import collections

bp = Blueprint('survey', __name__)


@bp.route('/')
def index():
    return render_template('survey/index.html')

@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        poster_name = request.form.get("poster-name")
        email = request.form.get("email")

        error = None
        question_answer_dict = collections.OrderedDict()
        for key, val in request.form.items():
            if key.startswith("a-"):
                question_answer_dict[int(key.replace('a-for-q', ''))] = int(val)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()
            db.execute(db_utils.insert_query('users', ['email']), (email,))
            db.execute(db_utils.insert_query(
                'posters', ['name', 'qr_id', 'qr_value']), (poster_name, 'qr122', ''))

            user_id = db_utils.get_id_from_tbl("users", {"email": email}, cursor)
            poster_id = db_utils.get_id_from_tbl(
                "posters", {"name": poster_name}, cursor)
            if not db_utils.value_exists_in_table("users_posters", {"users_id": user_id, "posters_id": poster_id}, cursor):
                db.execute(db_utils.insert_query("users_posters", ['users_id', 'posters_id']), [
                    user_id, poster_id])

            users_posters_id = db_utils.get_id_from_tbl(
                "users_posters", {"users_id": user_id, "posters_id": poster_id}, cursor)

            if not db_utils.value_exists_in_table("surveys", {"users_posters_id": users_posters_id}, cursor):
                db.execute(db_utils.insert_query("surveys", ['comment', 'users_posters_id']), [
                    "", users_posters_id])
            survey_id = db_utils.get_id_from_tbl(
                "surveys", {"users_posters_id": users_posters_id}, cursor)

            for q, a in question_answer_dict.items():
                sql = db_utils.insert_query(
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
    return render_template('survey/create.html', questions=questions)


@bp.route('/<poster_name>/<email>', methods=('GET', 'POST'))
def update(poster_name, email):
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
                    "answers", ["answer"], {'surveys_id' : survey_id, 'questions_id': q})
                db.execute(sql, [a,])

            db.commit()
            return redirect(url_for('survey.index'))
    else:        
        surveys = get_survey(poster_name, email)
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
