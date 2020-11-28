from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.db import get_db

bp = Blueprint('survey', __name__)


@bp.route('/')
def index():
    db = get_db()
    surveys = db.execute(
        'SELECT id, question'
        ' FROM questions'
        ' ORDER BY id'
    ).fetchall()
    return render_template('survey/index.html', surveys=surveys)


@bp.route('/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        body = request.form['body']
        error = None

        if error is not None:
            flash(error)
        # else:
        #     db = get_db()
        #     db.execute(
        #         'INSERT INTO post (title, body, author_id)'
        #         ' VALUES (?, ?, ?)',
        #         (title, body, g.user['id'])
        #     )
        #     db.commit()
        #     return redirect(url_for('survey.index'))

    return render_template('index/create.html')



def get_post(id):
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
        abort(404, "Post id {0} doesn't exist.".format(id))

    return post
