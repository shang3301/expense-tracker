import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "groot",
    "database": "expenses"
}

current_user = None
_selected_table = None
current_table = None

def connect():
    return mysql.connector.connect(**DB_CONFIG)

def set_user(user):
    global current_user
    current_user = user

def get_user():
    return current_user

def set_table(name):
    global _selected_table, current_table
    _selected_table = name
    current_table = name

def get_table():
    return _selected_table

def create_user(username, password):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(50) PRIMARY KEY,
            password VARCHAR(50)
        )
    """)
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        return True
    except mysql.connector.IntegrityError:
        return False
    finally:
        cur.close()
        conn.close()

def validate_user(username, password):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result is not None

def get_user_tables():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SHOW TABLES")
    all_tables = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    if current_user:
        return [t for t in all_tables if t.startswith(f"{current_user}_")]
    return []

def create_table(table_name):
    if not current_user:
        return False
    full_table_name = f"{current_user}_{table_name}"
    conn = connect()
    cur = conn.cursor()
    cur.execute(f"""
        CREATE TABLE `{full_table_name}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE,
            category VARCHAR(100),
            amount DECIMAL(10, 2),
            description TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    return True

def fetch_expenses():
    conn = connect()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM `{get_table()}`")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def add_expense(date, category, amount, description):
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO {current_table} (date, category, amount, description) VALUES (%s, %s, %s, %s)",
            (date, category, amount, description)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        cur.close()
        conn.close()

def delete_expense(expense_id):
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM `{get_table()}` WHERE id = %s", (expense_id,))
        conn.commit()
        return cur.rowcount > 0 
    except Exception as e:
        print("Delete error:", e)
        return False
    finally:
        cur.close()
        conn.close()


def get_total_expenses(category, start_date, end_date):
    conn = connect()
    cur = conn.cursor()
    if category == "All":
        cur.execute(
            f"SELECT SUM(amount) FROM {current_table} WHERE date BETWEEN %s AND %s",
            (start_date, end_date)
        )
    else:
        cur.execute(
            f"SELECT SUM(amount) FROM {current_table} WHERE category = %s AND date BETWEEN %s AND %s",
            (category, start_date, end_date)
        )
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result[0] else 0

def delete_table(table_name):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        return True
    except Exception as e:
        print("Error deleting table:", e)
        return False
    finally:
        cursor.close()
        conn.close()


def rename_table(username, old_name, new_name):
    try:
        conn = connect()
        cur = conn.cursor()
        old_full = f"{username}_{old_name}"
        new_full = f"{username}_{new_name}"
        cur.execute(f"ALTER TABLE `{old_full}` RENAME TO `{new_full}`")
        conn.commit()
        return True
    except:
        return False
    finally:
        cur.close()
        conn.close()

def duplicate_table(username, old_name, new_name):
    try:
        conn = connect()
        cur = conn.cursor()
        old_full = f"{username}_{old_name}"
        new_full = f"{username}_{new_name}"
        cur.execute(f"CREATE TABLE `{new_full}` LIKE `{old_full}`")
        cur.execute(f"INSERT INTO `{new_full}` SELECT * FROM `{old_full}`")
        conn.commit()
        return True
    except:
        return False
    finally:
        cur.close()
        conn.close()

def get_table_info(table_name):
    conn = connect()
    cur = conn.cursor()
    cur.execute(f"DESCRIBE `{table_name}`")
    result = [(row[0], row[1]) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return result

def get_table_count(table_name):
    conn = connect()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM `{table_name}`")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count

def delete_user(username, password):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            cursor.execute("DELETE FROM users WHERE username=%s AND password=%s", (username, password))
            conn.commit()
            return True
        else:
            return False
    except Exception as e:
        print("Error deleting user:", e)
        return False
    finally:
        cursor.close()
        conn.close()
