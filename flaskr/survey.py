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

@bp.route('/create', methods=['GET'])
def create():
    db = get_db()
    questions = db.execute(
        'SELECT id, question'
        ' FROM questions'
        ' ORDER BY id'
    ).fetchall()
    return render_template('survey/create.html', questions=questions)


@bp.route('/create', methods=['POST'])
def response():
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

    return render_template("index.html", poster_name=poster_name, email=email)


# def get_survey(id):
#     survey = get_db().execute(
#         'SELECT s.id, q.question, a.answer, p.name, u.email, s.comment, p.qr_value'
#         'FROM surveys AS s LEFT JOIN users_posters AS up ON up.id = s.users_posters_id'
#         'LEFT JOIN answers AS a ON a.surveys_id = s.id'
#         'LEFT JOIN questions AS q ON q.id = a.questions_id'
#         'LEFT JOIN posters AS p ON p.id = up.posters_id'
#         'LEFT JOIN users AS u ON u.id = ?',
#         (id,)
#     ).fetchone()

#     if survey is None:
#         abort(404, "Survey id {0} doesn't exist.".format(id))

#     return survey
