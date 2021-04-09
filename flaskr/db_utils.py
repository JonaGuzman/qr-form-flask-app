""" Utility class for preparing SQL statements """
from flaskr.db import get_db
from werkzeug.exceptions import abort
import pandas


def get_sql_args(values_list=None, str_frmt_args=True):
    """ Returns string with ? for sql values execute method """
    val_args = ""
    for index, value in enumerate(values_list):
        
        val = '?' if str_frmt_args else value
        if index == len(values_list) - 1:
            val_args += val
        else:
            val_args += val + ', '
            
    return val_args


def select_query_str(table_name, columns=None, where=None):
    if len(columns) > 1:
        columns = get_sql_args(columns, str_frmt_args=False)
    else:
        columns = "*"

    query_str = f"SELECT {columns} FROM {table_name}"
    where_stmt = "" if where is None else get_where_clause(where)
    return query_str + where_stmt


def insert_query_str(table_name, columns):
    return f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({get_sql_args(columns)})"


def get_where_clause(col_val_dict):
    """ Returns properly formatted WHERE clause """
    where_text = " WHERE "
    
    if len(col_val_dict) == 1:
        column = list(col_val_dict.keys())[0]
        where_text += f"{column} = '{col_val_dict[column]}'"
        return where_text

    for count, cv in enumerate(col_val_dict):
        val = col_val_dict[cv]
        if count < len(col_val_dict) - 1:
            where_text += f"{cv} = {val} AND "            
        else:
            where_text += f"{cv} = {val}"

    return where_text


def update_query_str(table_name, col_val_list, where):
    col_val = ""
    for cv in col_val_list:
        col_val += f"{cv} = ?, "
    if col_val.endswith(', '):
        col_val = col_val.rstrip(', ')
    return f"UPDATE {table_name} SET {col_val + get_where_clause(where)}"


def get_table_id(table_name, where):
    cursor = get_db().cursor()
    cursor.execute(select_query_str(table_name, ['id'], where))
    id = cursor.fetchone()['id']
    return id


def check_if_value_in_table(table_name, where):
    cursor = get_db().cursor()
    sql = f"SELECT COUNT(*) FROM {table_name + get_where_clause(where)}"
    cursor.execute(sql)
    count = cursor.fetchone()[0]

    if count > 0:
        print(f"Existing entry in table {table_name}")
        return True
    else:
        return False


def get_survey_id(email, poster_name):
    users_id = get_table_id('users', {'email': email})
    posters_id = get_table_id('posters', {'name': poster_name})
    up_id = get_table_id(
        'users_posters', {'users_id': users_id, 'posters_id': posters_id})
    return get_table_id('surveys', {'users_posters_id': up_id})


def get_survey(poster_name, email):
    cursor = get_db().cursor()
    survey = cursor.execute(
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

def run_survey_create_view_query():
    cursor = get_db().cursor()
    cursor.execute("""DROP VIEW IF EXISTS survey_view""")
    cursor.execute(
        """CREATE VIEW survey_view (id, question, answer, name, email, comment, qr_value) AS
        SELECT s.id, q.question, a.answer, p.name, u.email, s.comment, p.qr_value
        FROM surveys s
        LEFT JOIN users_posters up ON up.id = users_posters_id
        LEFT JOIN answers a ON a.surveys_id = s.id
        LEFT JOIN questions q ON q.id = a.questions_id
        LEFT JOIN posters p ON p.id = up.posters_id
        LEFT JOIN users u ON u.id = up.users_id
        ORDER BY q.id"""
    )

def pivot_all_surveys_table(questions):
    """ Table with questions as columns """
    pivot = pandas.read_sql_query(
        f"""SELECT id, email, name, {frmt_case_seq(questions)}
        FROM (
            SELECT survey_view.*,
            row_number() over (partition by email order by id) as seq
            from survey_view
            ) survey_view
            GROUP BY email""", get_db())
    return pivot

def frmt_case_seq(questions_list):
    count = 1
    case_stmt = ""
    for q in range(0, len(questions_list)):
        endline = "," if count != len(questions_list) else ""
        case_stmt += "max(case when seq = %d then answer end) as \'%s\'%s\n" % (
            count, questions_list[q], endline)
        count += 1
    return case_stmt

def run_insert_answers_query(items, survey_id):
    for q, a in items:
        sql = insert_query_str(
            "answers", ["answer", "questions_id", "surveys_id"])
        val = [a, q, survey_id]
        get_db().execute(sql, val)
