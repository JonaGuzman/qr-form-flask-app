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
    db = get_db()
    questions = db.execute(
        'SELECT id, question'
        ' FROM questions'
        ' ORDER BY id'
    ).fetchall()
    return render_template('survey/index.html', questions=questions)


@bp.route('/response', methods=['POST'])
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
        db.execute(db_utils.insert_query('users', ['email']), (email,))
        db.execute(db_utils.insert_query('posters', ['name', 'qr_id', 'qr_value']),
                   (poster_name, 'qr122', ''))
        db.commit()
        return redirect(url_for('survey.index'))

    return render_template("index.html", poster_name=poster_name, email=email)


def get_survey(id):
    post = get_db().execute(
        'SELECT s.id, q.question, a.answer, p.name, u.email, s.comment, p.qr_value'
        'FROM surveys AS s LEFT JOIN users_posters AS up ON up.id = s.users_posters_id'
        'LEFT JOIN answers AS a ON a.surveys_id = s.id'
        'LEFT JOIN questions AS q ON q.id = a.questions_id'
        'LEFT JOIN posters AS p ON p.id = up.posters_id'
        'LEFT JOIN users AS u ON u.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Survey id {0} doesn't exist.".format(id))

    return post
