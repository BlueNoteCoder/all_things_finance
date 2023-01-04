import datetime

import finance
import finance_db
import os
import subprocess
from finance_db import FinanceDB

PATH_OF_SCRIPT = os.path.dirname(__file__)
DB_NAME = 'my_numbers.sqlite'

methods = {
    1: finance.register,
    2: finance.make_deposit,
    3: finance.make_transaction,
    4: finance.bills_menu,
    5: finance.budget_menu,
    6: exit
}


def greeting():
    print(f"\n{'':*>30}'GREETINGS EARTHLING!'{'':*<30}")


def main_menu():
    print("Please select one of the following operations:")
    print("\n1. Register"
          "\n2. Make Deposit"
          "\n3. Make Transaction"
          "\n4. Bills Lookup"
          "\n5. Budget Menu"
          "\n6. Exit")


def deposit_menu():
    print(f"{'':*>30}DEPOSIT{'':*<30}")
    print("Please enter the following:")


def transaction_menu():
    print(f"{'':*>30}TRANSACTION{'':*<30}")
    print("Please enter the following:")


def main():
    db_alive = FinanceDB.database_exist(PATH_OF_SCRIPT + '/' + DB_NAME)
    fin_db = finance_db.FinanceDB(path=PATH_OF_SCRIPT, db_name=DB_NAME)
    keep_loopin = True

    if not db_alive:
        fin_db.initialize_database()
        account_1 = finance.setup_account(fin_db.get_total_accounts())
        fin_db.add_account(account_1.name, account_1.starting_balance)
    else:
        account_1 = finance.get_account(fin_db.get_account("Spencer"))

    if not os.path.isdir(os.path.dirname(__file__) + f"/json/month_{datetime.datetime.now().month}"):
        print(f"Creating month necessary month folder in json directory")
        os.makedirs(f"{os.path.dirname(__file__)}/json/month_{datetime.datetime.now().month}")
        print(f"Created {os.path.dirname(__file__)}/json/month_{datetime.datetime.now().month} directory")
    else:
        print(f"json/month_{datetime.datetime.now().month} directory already exists")
    account_1.populate_items(fin_db)

    while keep_loopin:
        user_selection = 0

        while user_selection < 1 or user_selection > 5:
            greeting()
            main_menu()
            user_selection = int(input("\nSELECTION(1-6):"))

            if user_selection in range(1, 7):
                if user_selection == 2 or user_selection == 3:
                    methods[user_selection](account_1, fin_db)
                elif user_selection == 4:
                    methods[user_selection]()
                elif user_selection == 5:
                    methods[user_selection]()
                elif user_selection == 6:
                    methods[user_selection]("\nHAVE A LOVELY DAY")
                else:
                    methods[user_selection](account_1)

            else:
                print("INVALID RESPONSE! TRY AGAIN!!!")


if __name__ == '__main__':
    main()
