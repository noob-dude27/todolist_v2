"""
Handles the creation of taskdatabase.db. This database handles the creation, deletion, and insertion of 
Tasks and Todo lists instances and tables.
"""

import sqlite3 as sql3

conn = sql3.connect("database/taskdatabase.db")
cur = conn.cursor()

class Task_DB:
    @staticmethod
    def create_Todo_lists_table():
        cur.execute(""" CREATE TABLE IF NOT EXISTS Todo_lists (
            name text UNIQUE,
            creation_date text ) """)

        conn.commit()
        print("Todo_lists table added successfully")

    @staticmethod
    def create_Tasks_table():
        cur.execute(""" CREATE TABLE IF NOT EXISTS Tasks (
            parent text,
            name text,
            creation_date text,
            deadline_date text,
            deadline_time text,
            is_completed text ) """)

        conn.commit()
        print("Tasks table added successfully")


def delete_table_contents(table):
    """Deletes all contents of a specified table in sqlite."""
    cur.execute(f""" DELETE FROM {table}""")
    conn.commit()

def delete_table(table):
    """Deletes a specified table itself in sqlite."""
    cur.execute(f""" DROP TABLE IF EXISTS {table}""")
    conn.commit()
    

def list_table_contents(table):
    """Lists contents of a specific table in sqlite."""
    cur.execute(f"""SELECT rowid, * FROM {table}""")
    conn.commit()
    return cur.fetchall()

if __name__ == "__main__":
    #delete_table("Todo_lists")
    #delete_table("Tasks")
    #Task_DB.create_Todo_lists_table()
    #Task_DB.create_Tasks_table()
    delete_table_contents("Tasks")
    conn.close()
