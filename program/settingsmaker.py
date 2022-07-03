"""
Handles the creation of the settings.db. 
This database stores settings data that toggles how the app works.
"""

import sqlite3 as sql3

conn = sql3.connect("database/settings.db")
cur = conn.cur()

class Settings:
    @staticmethod
    def create_table():
        cur.execute(""" CREATE TABLE IF NOT EXISTS Settings (
            """)

if __name__ == "__main__":
    conn.close()