""" Utility class for preparing SQL statements """


def select_query(table_name, columns_list=None, where_dict=None):
    cols = ""
    if columns_list is None or columns_list == "*":
        cols = "*"
    else:
        cols = get_sql_args(columns_list, str_frmt_args=False)

    sel_query = "SELECT %s FROM %s" % (cols, table_name)
    if where_dict is None:
        return sel_query
    else:
        return sel_query + get_where_clause(where_dict)


def get_id_from_tbl(table_name, where_dict, cursor):
    cursor.execute(select_query(table_name, ["id"], where_dict))
    id = cursor.fetchone()[0]
    return id


def insert_query(table_name, columns_list):
    return "INSERT OR IGNORE INTO %s (%s)" % (table_name, ', '.join(columns_list)) + " VALUES (%s)" % get_sql_args(columns_list)


def get_sql_args(values_list=None, str_frmt_args=True):
    """ Returns string with %s for sql values execute method """
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


def get_where_clause(col_val_dict):
    """ Returns properly formatted WHERE clause """
    where_text = " WHERE "
    count = 0
    for cv in col_val_dict:
        if len(col_val_dict) == 1:
            where_text += "%s = '%s'" % (cv, col_val_dict[cv])
            break
        if count == len(col_val_dict) - 1:
            where_text += "%s = '%s'" % (cv, col_val_dict[cv])
            break
        else:
            where_text += "%s = '%s' AND " % (cv, col_val_dict[cv])
        count += 1
    return where_text
