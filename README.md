. venv/bin/activate
flask init-db
export FLASK_APP=flaskr
export FLASK_ENV=development
'SELECT s.id, q.question, a.answer, p.name, u.email, s.comment, p.qr_value'
        ' FROM surveys AS s LEFT JOIN users_posters AS up ON up.id = s.users_posters_id'
        ' LEFT JOIN answers AS a ON a.surveys_id = s.id'
        ' LEFT JOIN questions AS q ON q.id = a.questions_id'
        ' LEFT JOIN posters AS p ON p.id = up.posters_id'
        ' LEFT JOIN users AS u ON u.id = up.users_id'

cur = db.cursor()
        cur.execute('SELECT * FROM users')
        row = cur.fetchall()
        for r in row:
            print(tuple(r))