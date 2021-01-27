import random
import sqlite3


class Bank:

    def __init__(self):
        self.id = 1
        self.acc_info = None
        self.balance = None
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.create_table()
        self.welcome_ui()

    def create_table(self):
        try:
            self.cur.execute("""CREATE TABLE card (
                    id integer,
                    number text,
                    pin text,
                    balance integer default 0
                    )""")
            self.conn.commit()
        except sqlite3.OperationalError:
            self.cur.execute('DROP TABLE card')
            self.create_table()

    def welcome_ui(self):
        wel_action = input("1. Create an account\n2. Log into account\n0. Exit\n")
        if wel_action == '1':
            self.create_acc()
        elif wel_action == '2':
            self.log_acc()
        else:
            print('\nBye!')
            pass

    def create_acc(self):
        card_no = '400000'
        pin_genr = str(random.choice(range(0, 9999)))
        for n in range(9):
            card_no += str(random.randint(0, 9))
        card_no += self.luhn_algorithm(card_no)
        pin = pin_genr.zfill(4)
        print(f"""\nYour card has been created
Your card number:
{card_no}
Your card PIN:
{pin}\n""")
        self.cur.execute("INSERT INTO card (id, number, pin) VALUES (?, ?, ?)", (self.id, card_no, pin))
        self.conn.commit()
        self.id += 1
        self.welcome_ui()

    @staticmethod
    def luhn_algorithm(card_no):
        card = [int(n) for n in card_no]
        for n in range(0, 16, 2):
            card[n] = card[n] * 2
            if card[n] > 9:
                card[n] += -9
        if sum(card) % 10 != 0:
            return str((10 - (sum(card) % 10)))
        else:
            return '0'

    def log_ui(self):
        action = input("""\n1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit\n""")
        if action == '1':
            self.get_balance()
            self.log_ui()
        elif action == '2':
            self.add_income()
            self.log_ui()
        elif action == '3':
            self.do_transfer()
            self.log_ui()
        elif action == '4':
            self.close_account()
            self.welcome_ui()
        elif action == '5':
            print('\nYou have successfully logged out!\n')
            self.welcome_ui()
        else:
            print('\nBye!')
            pass

    def log_acc(self):
        input_number = input('\nEnter your card number:\n')
        input_pin = input('Enter your PIN\n')
        self.check_number_and_pin(input_number, input_pin)

    def check_number_and_pin(self, number, pin):
        self.cur.execute(f"SELECT * from card where number= ? and pin= ?", (number, pin))
        self.acc_info = self.cur.fetchone()
        if self.acc_info:
            print('\nYou have successfully logged in!')
            self.balance = self.acc_info[-1]
            self.log_ui()
        else:
            print('\nWrong card number or PIN!\n')
            self.welcome_ui()

    def get_balance(self):
        print(f'Balance: {self.balance}')

    def add_income(self):
        income = int(input('\nEnter income:\n'))
        self.balance += income
        self.cur.execute(f'UPDATE card SET balance= {self.balance} WHERE number= {self.acc_info[1]}')
        self.conn.commit()

    def do_transfer(self):
        print('\nTransfer')
        transfer_no = input('Enter card number:\n')
        self.cur.execute(f'SELECT * FROM card WHERE number= {transfer_no}')
        transfer_acc = self.cur.fetchone()
        if len(transfer_no) < 16:
            print('Such a card does not exist.\n')
        elif transfer_no[-1] != self.luhn_algorithm(transfer_no[0:15]):
            print('\nProbably you made a mistake in the card number. Please try again!')
        elif transfer_acc[1] == self.acc_info[1]:
            print('You can\'t transfer money to the same account!\n')
        elif transfer_acc:
            transfer_money = int(input('Enter how much money you want to transfer:\n'))
            if int(self.balance) > transfer_money:
                balance = transfer_acc[-1] + transfer_money
                self.cur.execute(f'UPDATE card SET balance= {balance} WHERE number= {transfer_acc[1]}')
                self.balance += -transfer_money
                self.cur.execute(f'UPDATE card SET balance= {self.balance} WHERE number= {self.acc_info[1]}')
                print('Succes!\n')
                self.conn.commit()
            else:
                print('Not enough money!\n')
        else:
            print('Such a card does not exist.\n')

    def close_account(self):
        self.cur.execute(f"DELETE FROM card WHERE number= {self.acc_info[1]}")
        print('The account has been closed!')
        self.conn.commit()


program = Bank()
