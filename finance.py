import json
import sqlite3
import os
from prettytable import PrettyTable
from finance_db import FinanceDB

TRANSACTION_TYPES = {
    "w": "Withdrawal",
    "d": "Deposit"
}

COMMON_STORES = [
    "Cox",
    "Fi",
    "CarMax",
    "Netflix",
]


class Account:
    def __init__(self, name, account_id, starting_balance, current_balance=None):
        self.name = name
        self.account_id = account_id
        self.starting_balance = starting_balance
        self.current_balance = current_balance
        # self.debt = {}
        self.items = []
        self.new_items = []

    def get_account_id(self):
        return self.account_id

    def populate_items(self, fin_db: FinanceDB):
        items = fin_db.get_items()

        for item in items:
            self.items.append(Item(account_id=item["id"], date_entered=item["Date"], descript=item["Description"],
                                   pay_type=item["Payment Type"], trans_type=item["Transaction Type"],
                                   amount=item["Amount"], check_num=item["Check No."]))


class Item:
    def __init__(self, account_id: int, date_entered: str, descript: str, pay_type: str,
                 trans_type: str, amount: float, check_num: int = 0):
        self.account_id = account_id
        self.date_entered = date_entered
        self.description = descript
        self.pay_type = pay_type
        self.transaction_type = trans_type
        self.amount = amount
        self.check_num = check_num


def new_table(tbl_name: str, params: str, cursed: sqlite3.Cursor):
    """
    Creates a new table in the database with the given params
    """
    pass


def setup_account(total_accounts: int) -> Account:
    print(f"{'':*>30}ACCOUNT SETUP{'':*<30}")
    name = input("\nEnter Account name: ")
    starting_balance = float(input("Enter starting balance: "))

    return Account(name=name, account_id=total_accounts + 1, starting_balance=starting_balance)


def get_account(account_info: list):
    return Account(name=account_info[0][1], account_id=account_info[0][0], starting_balance=account_info[0][2])


def register(account: Account):
    balance = account.starting_balance

    register_table = PrettyTable()

    register_table.field_names = ["Date", "Description", "Payment Type", "Transaction Type", "Check No.", "Amount",
                                  f"Starting Balance: {account.starting_balance}"]

    for item in account.items:
        if item.transaction_type == "Withdrawal":
            balance = balance - item.amount
        else:
            balance = balance + item.amount

        register_table.add_row(
            [item.date_entered, item.description, item.pay_type, item.transaction_type, item.check_num, item.amount,
             f"{balance:.2f}"])
    print()
    print(register_table)


def make_deposit(account: Account, fin_db: FinanceDB):
    print(f"\n{'':*>30}MAKE DEPOSIT{'':*<30}")

    item = add_item(account.get_account_id(), "Deposit")

    account.items.append(item)
    fin_db.add_item(item.date_entered, item.description, item.pay_type, item.transaction_type, item.amount,
                    item.check_num)


def make_transaction(account: Account, fin_db: FinanceDB):
    print(f"\n{'':*>30}MAKE TRANSACTION{'':*<30}")

    item = add_item(account.get_account_id(), "Withdrawal")

    account.items.append(item)
    fin_db.add_item(item.date_entered, item.description, item.pay_type, item.transaction_type, item.amount, item.check_num)


def add_item(account_id: int, trans_type: str) -> Item:
    """
    Item object is made and returned
    """
    date_entered = input("\nDate (dd-mm-yyyy): ")
    description = input("\nItem Description: ")
    pay_type = input("\nPayment type: ")
    amount = float(input("\nItem total: "))
    check_num = int(input("Check No. (0 if no check): "))

    return Item(account_id=account_id, date_entered=date_entered, descript=description, pay_type=pay_type,
                trans_type=trans_type, amount=amount, check_num=check_num)


def get_all_items_by_date():
    """
    Returns a list of all the items sorted by date
    """
    pass


def print_bills(bills: dict):
    bill_table = PrettyTable()

    bill_table.field_names = ["Bill Name", "Amount", "Due on"]

    for bill in bills:
        bill_table.add_row([bill, bills[bill]["Amount"], bills[bill]["Due by"]])

    print()
    print(bill_table)


def bills_menu():
    loopin = True
    bills = {}
    while loopin:
        if not os.path.isfile(os.path.dirname(__file__) + "/bills.json"):
            print("No file exists for bills! Please select 'EDIT' to create one")

        print(f"\n{'':*>30}BILLS MENU{'':*<30}")
        print("\n1.View Bills"
              "\n2.Add/Edit Bill"
              "\n3.Delete bill"
              "\n4.Main menu")

        user_selection = input("\nSelection: ")

        if user_selection == '1' or user_selection == '3':
            if os.path.isfile(os.path.dirname(__file__) + "/bills.json"):
                with open(os.path.dirname(__file__) + "/bills.json") as bills_file:
                    bills = json.load(bills_file)

                print_bills(bills)
            if user_selection == '3':
                bill = input("Enter name of Bill to be deleted: ")
                if bill in bills:
                    del bills[bill]
                    with open(os.path.dirname(__file__) + "/bills.json", 'w') as bills_file:
                        json.dump(bills, bills_file)
        elif user_selection == '2':
            bill_name = input("\nBill name: ")
            bill_amount = input("Bill Amount: ")
            bill_due = input("Bill due by (DAY No.): ")

            bills[bill_name] = {"Amount": bill_amount, "Due by": bill_due}

            with open(os.path.dirname(__file__) + "/bills.json", 'w') as bills_file:
                json.dump(bills, bills_file)

        elif user_selection == '4':
            loopin = False

