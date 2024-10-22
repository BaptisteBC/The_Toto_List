import pymysql
import sqlite3


MysqlConfig = {
    'host': 'localhost',
    'user': 'root',
    'password': 'toto',
    'database': 'thetotodb',
    'port': 3306
}

def VerficicationCoBDD(config):
    try:
        connection = pymysql.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        connection.close()
        return True
    except pymysql.MySQLError as e:
        return False

def MysqlEnSqlite(MysqlConfig, sqlite_db_path):
    mysql_conn = pymysql.connect(
        host=MysqlConfig['host'],
        user=MysqlConfig['user'],
        password=MysqlConfig['password'],
        database=MysqlConfig['database'],
        port=MysqlConfig['port']
    )
    mysql_cursor = mysql_conn.cursor()

    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_cursor = sqlite_conn.cursor()

    mysql_cursor.execute("SHOW TABLES")
    tables = mysql_cursor.fetchall()

    for (table_name,) in tables:
        # Get table schema from MySQL
        mysql_cursor.execute(f"DESCRIBE {table_name}")
        schema = mysql_cursor.fetchall()

        columns = []
        for column in schema:
            col_name = column[0]
            col_type = column[1]

            if "int" in col_type:
                sqlite_type = "INTEGER"
            elif "char" in col_type or "text" in col_type:
                sqlite_type = "TEXT"
            elif "blob" in col_type:
                sqlite_type = "BLOB"
            elif "float" in col_type or "double" in col_type or "decimal" in col_type:
                sqlite_type = "REAL"
            elif "date" in col_type or "time" in col_type or "year" in col_type:
                sqlite_type = "TEXT"
            else:
                sqlite_type = "TEXT"  # Default to TEXT for unknown types

            columns.append(f"{col_name} {sqlite_type}")

        columns_str = ", ".join(columns)

        sqlite_cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})")

        mysql_cursor.execute(f"SELECT * FROM {table_name}")
        rows = mysql_cursor.fetchall()

        placeholders = ", ".join(["?" for _ in range(len(columns))])
        sqlite_cursor.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", rows)

        sqlite_conn.commit()

    mysql_cursor.close()
    mysql_conn.close()
    sqlite_cursor.close()
    sqlite_conn.close()

    print("Données exportées avec succès vers SQLite.")



if VerficicationCoBDD(MysqlConfig):
    print("Connexion à la base de données MySQL vérifiée.")
    MysqlEnSqlite(MysqlConfig, 'thetotodb.sqlite')
else:
    print("La connexion a échoué.")
