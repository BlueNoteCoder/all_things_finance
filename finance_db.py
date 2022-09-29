import sqlite3
import os
from sqlite3 import Error


def create_connection(path: str, db_name: str):
    db_path = path + '/' + db_name

    try:
        print(f"Establishing Connection to {db_path}")
        connection = sqlite3.connect(db_path)

        if not connection:
            raise Error
    except Error as e:
        print(e)

    return connection


class FinanceDB:
    def __init__(self, path: str, db_name: str):
        # variable with path and name?
        self.conn = create_connection(path, db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name: str, params: str):
        print(f"Creating {table_name}")

        stmt = f"CREATE TABLE IF NOT EXISTS {table_name} ({params});"
        con = self.cursor.execute(stmt)

    def initialize_database(self):
        print("Creating Tables")
        self.create_table(table_name="accounts", params="AccountId INTEGER PRIMARY KEY,"
                                                        "Name TEXT NOT NULL,"
                                                        "CurrBalance REAL")

        self.create_table(table_name="items", params="AccountId INTEGER PRIMARY KEY,"
                                                     "DateEntered TEXT NOT NULL,"
                                                     "Description TEXT NOT NULL,"
                                                     "PaymentType TEXT NOT NULL,"
                                                     "TransType TEXT NOT NULL,"
                                                     "Amount REAL NOT NULL,"
                                                     "CheckNum INTEGER")
        print("Tables created")

    @staticmethod
    def database_exist(path: str):
        return os.path.isfile(path)

    def add_item(self, date_entered, description, pay_type, trans_type, amount, check_num):
        stmt = f"INSERT INTO items (AccountId, DateEntered, Description, PaymentType, TransType, Amount, CheckNum) " \
               f"VALUES (NULL,?,?,?,?,?,?)"
        self.cursor.execute(stmt, (date_entered, description, pay_type, trans_type, amount, check_num))

        self.conn.commit()
        print("ADDED ITEM")

    def delete_item(self):
        pass

    def add_account(self, name, current_balance):
        stmt = f"INSERT INTO accounts (AccountId, Name, CurrBalance)" \
               f"VALUES (NULL,?,?)"
        self.cursor.execute(stmt, (name, current_balance))
        self.conn.commit()
        print("ADDED ACCOUNT")

    def get_account(self, name: str):
        stmt = f"SELECT * FROM accounts WHERE Name = '{name}'"
        self.cursor.execute(stmt)

        # returns a tuple, need to get first num in it
        return self.cursor.fetchall()

    def get_total_accounts(self):
        stmt = f"SELECT COUNT(*) FROM accounts"
        self.cursor.execute(stmt)

        # returns a tuple, need to get first num in it
        return self.cursor.fetchone()[0]

    def get_items(self):
        items = []
        count_stmt = f"SELECT * FROM items"
        self.cursor.execute(count_stmt)

        rows = self.cursor.fetchall()

        for row in rows:
            items.append({"id": row[0], "Date": row[1], "Description": row[2], "Payment Type": row[3], "Transaction Type": row[4], "Amount": row[5], "Check No.": row[6]})

        return items

    def get_last_item(self):
        count_stmt = f"SELECT COUNT(*) FROM items"
        self.cursor.execute(count_stmt)

        count = self.cursor.fetchone()[0]

        # returns a tuple, need to get first num in it
        return self.cursor.fetchone()[0]
