import datetime

import json
import sqlite3
import os
import subprocess
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
    fin_db.add_item(item.date_entered, item.description, item.pay_type, item.transaction_type, item.amount,
                    item.check_num)


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
            if os.path.isfile(os.path.dirname(__file__) + f"/json/month_{datetime.datetime.now().month}/bills.json"):
                with open(os.path.dirname(
                        __file__) + f"/json/month_{datetime.datetime.now().month}/bills.json") as bills_file:
                    bills = json.load(bills_file)

                print_bills(bills)
            if user_selection == '3':
                bill = input("Enter name of Bill to be deleted: ")
                if bill in bills:
                    del bills[bill]
                    with open(
                            os.path.dirname(__file__) + f"/json/month_{str(datetime.datetime.now().month)}/bills.json",
                            'w') as bills_file:
                        json.dump(bills, bills_file)
        elif user_selection == '2':
            bill_name = input("\nBill name: ")
            bill_amount = input("Bill Amount: ")
            bill_due = input("Bill due by (DAY No.): ")

            bills[bill_name] = {"Amount": bill_amount, "Due by": bill_due}

            with open(os.path.dirname(__file__) + f"/json/month_{str(datetime.datetime.now().month)}/bills.json",
                      'w') as bills_file:
                json.dump(bills, bills_file)

        elif user_selection == '4':
            loopin = False


def budget_menu():
    loopin = True

    while loopin:
        print("1.New Budget\n"
              "2.View Existing Budget\n"
              "3.Main Menu")
        user_selection = input("\nSelection: ")

        if int(user_selection) == 1:
            _calculate_budget()

        if int(user_selection) == 2:
            view_budget()

        if int(user_selection) == 3:
            loopin = False


def _calculate_budget():
    bills = []
    expenses = []
    bills_per_paycheck = []
    paychecks = gather_income()  # list of paychecks

    bills_path = f"{os.path.dirname(__file__)}/json/month_{str(datetime.datetime.now().month)}/bills.json"
    income_path = f"{os.path.dirname(__file__)}/json/month_{str(datetime.datetime.now().month)}/income.json"

    bills_exist = verify_file_dir_exists(bills_path, "file")
    income_exist = verify_file_dir_exists(income_path, "file")

    if not (bills_exist and income_exist):
        print("Need to add bills before you can start budget")
        return

    # load in bills.json into bills
    with open(bills_path, 'r') as bills_json:
        bills = json.load(bills_json)
    # Ask if there's other expenses need to be included

    other_expenses_option = input(
        "Aside from bills....\nIs there anything else you want included in the budget?(y/n) -> ").lower()

    while other_expenses_option != 'y' and other_expenses_option != 'n':
        print("NOPE")
        print("Try again\n\n")
        other_expenses_option = input(
            "Aside from bills...\nIs there anything else you want included in the budget?(y/n) ->")

    if other_expenses_option == 'y':
        pass
        # prompt for expense
        # prompt for date
        # store in expenses list

    # calculate bills per paycheck
    bills_per_paycheck = calculate_bills_to_paycheck(bills, paychecks, expenses)

    # print results

    # Create budget.json and store bills per paycheck
    pass


def view_budget():
    # check for budget.json

    # if file exists, load it in, else print statement

    # display budget

    pass


def gather_income() -> list:
    """
    Gather all income for the month, and stores data in /json/month/income.json
    Return: list of all income (list({'Amount': str(), 'Day': str()})
    """
    income = []

    num_of_paychecks = int(input("How many paychecks will you have for this month? -> "))

    for num in range(num_of_paychecks):
        amount = input(f"Amount for Paycheck #{num + 1} -> $")
        date = input(f"Day of Paycheck #{num + 1} -> ")
        income.append({"Amount": amount, "Day": date})

    # Store income data
    with open(os.path.dirname(__file__) + f"/json/month_{str(datetime.datetime.now().month)}/income.json",
              'w') as income_json:
        json.dump(income, income_json)

    return income


def calculate_bills_to_paycheck(bills: list, paychecks: list, expenses: list) -> list:
    num_of_paychecks = len(paychecks)

    # Sort lists based off of Day
    paychecks.sort(key=lambda x: int(x["Day"]))
    print(paychecks)


def verify_file_dir_exists(path: str, selection: str) -> bool:
    if selection == "file":
        if os.path.isfile(path):
            return True

    if selection == "dir":
        if os.path.isdir(path):
            return True

    return False
