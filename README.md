. venv/bin/activate
flask init-db
export FLASK_APP=flaskr
export FLASK_ENV=development
cur = db.cursor()
        cur.execute('SELECT * FROM users')
        row = cur.fetchall()
        for r in row:
            print(tuple(r))