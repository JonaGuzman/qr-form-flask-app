""" Utility class for preparing SQL statements """


def get_sql_args(values_list=None, str_frmt_args=True):
    """ Returns string with ? for sql values execute method """
    val_args = ""
    for i in range(len(values_list)):
        if str_frmt_args:
            val = '?'
        else:
            val = values_list[i]
        if i == len(values_list) - 1:
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
    print(query_str + where_stmt)
    return query_str + where_stmt


def insert_query_str(table_name, columns):
    return f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({get_sql_args(columns)})"


def frmt_arg(value):
    if isinstance(value, str):
        frmt_arg = '\'%s\''
    else:
        frmt_arg = '%d'
    return frmt_arg


def get_where_clause(col_val_dict):
    """ Returns properly formatted WHERE clause """
    where_text = " WHERE "
    count = 0
    for cv in col_val_dict:
        val = col_val_dict[cv]
        if len(col_val_dict) == 1:
            where_text += "%s = %s" % (cv, frmt_arg(val) % val)
            break
        if count == len(col_val_dict) - 1:
            where_text += "%s = %s" % (cv, frmt_arg(val) % val)
            break
        else:
            where_text += "%s = %s" % (cv, frmt_arg(val) % val) + " AND "
        count += 1
    return where_text


def update_query_str(table_name, col_val_list, where):
    col_val = ""
    for cv in col_val_list:
        col_val += f"{cv} = ?, "
    if col_val.endswith(', '):
        col_val = col_val.rstrip(', ')
    return f"UPDATE {table_name} SET {col_val +get_where_clause(where)}"


def get_table_id(table_name, where, cursor):
    cursor.execute(select_query_str(table_name, ['id'], where))
    id = cursor.fetchone()['id']
    return id


def check_if_value_in_table(table_name, where, cursor):
    sql = f"SELECT COUNT(*) FROM {table_name + get_where_clause(where)}"
    cursor.execute(sql)
    count = cursor.fetchone()[0]

    if count > 0:
        print(f"Existing entry in table {table_name}")
        return True
    else:
        return False


def get_survey_id(email, poster_name, cursor):
    users_id = get_table_id('users', {'email': email}, cursor)
    posters_id = get_table_id('posters', {'name': poster_name}, cursor)
    up_id = get_table_id(
        'users_posters', {'users_id': users_id, 'posters_id': posters_id}, cursor)
    return get_table_id('surveys', {'users_posters_id': up_id}, cursor)


def prep_case_seq(questions_list):
    count = 1
    case_stmt = ""
    for q in range(0, len(questions_list)):
        endline = "," if count != len(questions_list) else ""
        case_stmt += "max(case when seq = %d then answer end) as \'%s\'%s\n" % (
            count, questions_list[q], endline)
        count += 1
    return case_stmt
