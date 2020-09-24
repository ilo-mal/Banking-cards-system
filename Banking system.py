import random
import sqlite3

class BankingSystem:

    def __init__(self):
        self.my_conn()
        self.bank_database_table()
        self.card_no = 0
        self.card_pin = 0
        self.option = ''
        self.in_transfer = 0
        while self.option != '0':
            self.start_menu()
    
    def check_for_luhn(self, card_to_check):
        self.check_sum = []
        self.luhn_check = 0
        for i in str(card_to_check):
            self.check_sum.append(int(i))
        odd_check_sum = self.check_sum[0::2]
        doubled_odd = []
        for x in odd_check_sum:
            if x * 2 > 9:
                doubled_odd.append(x * 2 - 9)
            else:
                doubled_odd.append(x * 2)
        doubled_odd = sum(doubled_odd)
        add_check_sum = self.check_sum[1::2]
        add_check_sum = sum(add_check_sum)
        doubled_odd += add_check_sum
        if doubled_odd % 10 != 0:
            self.luhn_check = 10 - (doubled_odd % 10)
        return self.luhn_check
        
    def create_account(self):
        acc_identyfier= random.randint(400000000000000, 400000999999999)
        self.check_for_luhn(acc_identyfier)
        self.check_sum.append(self.luhn_check) # create card number
        self.check_sum = ''.join(list(map(str, self.check_sum)))
        card_no = int(self.check_sum)
        card_pin = random.randint(1000, 9999)
        print(f"Your card has been created\nYour card number:\n{card_no}")
        print(f"Your card PIN:\n{card_pin}\n")
        my_card = (card_no, card_pin)
        new_record = self.add_to_cards(my_card)

    def bank_database_table(self):
        cursor = self.my_connection.cursor()
        update_table ='''CREATE TABLE IF NOT EXISTS cards(
                        id INTEGER PRIMARY KEY,
                        card_no INTEGER NOT NULL,
                        pin INTEGER NOT NULL,
                        balance DEFAULT(0) )'''
        cursor.execute(update_table)
        self.my_connection.commit()
        cursor.close()

    def my_conn(self):
        try:
            self.my_connection = sqlite3.connect("bankingCards.db")
        except sqlite3.Error as error:
            print("connection failed")

    def add_to_cards(self, my_card):
        cursor = self.my_connection.cursor()
        add_card = '''INSERT INTO cards 
                        (card_no, pin)
                        VALUES(?, ?)'''
        cursor.execute(add_card, my_card)
        self.my_connection.commit()
        cursor.close()

    def log_in_accont(self):
        try:    
            entered_card_no = int(input("Enter your card number:\n"))
            entered_pin = int(input("Enter your PIN:\n"))
        except:
            print('Please put only numbers.\n')
            return
        cursor = self.my_connection.cursor()
        self.logged = 0
        cursor.execute('''SELECT card_no, pin FROM cards 
                        WHERE card_no = ? AND pin = ?''',
                       (entered_card_no, entered_pin))
        self.records = cursor.fetchall()
        cursor.close()
        for x in self.records:
            self.logged = 1
            print("You have successfully logged in!\n")
        new_log = self.log_in_options()

    def new_balance(self):
        cursor = self.my_connection.cursor()
        cursor.execute(('''SELECT balance FROM cards 
                        WHERE card_no = ? AND pin = ?'''),
                       (self.records[0][0], self.records[0][1]))
        acc_balance = cursor.fetchall()
        cursor.close()
        return acc_balance[0][0]
    
    def money_in_out(self, money, card_no):
        cursor = self.my_connection.cursor()
        money_query = '''UPDATE cards SET balance = ?
                        WHERE card_no = ?'''
        add_minus = (money, card_no)
        cursor.execute(money_query, add_minus)
        self.my_connection.commit()
        cursor.close()
   
    def add_income(self):
        try:
            to_add = int(input('Enter income:'))
        except:
            print('Please put only numbers.\n')
            return
        all_balance = to_add + self.new_balance()
        self.money_in_out(all_balance, self.records[0][0])
        print('Income was added!\n')
        
    def minus_income(self):
        money_out = (-self.in_transfer) + self.new_balance()
        self.money_in_out(money_out, self.records[0][0])
            
    def transfer(self):
        print('Transfer')
        try:
            destination = int(input('Enter card number:\n'))
        except:
            print('Please put only numbers.\n')
            return
        dest_to_check = destination // 10
        self.check_for_luhn(dest_to_check)
        luhn_to_check = destination % 10
        cursor = self.my_connection.cursor()
        cursor.execute('''SELECT card_no FROM cards 
                        WHERE card_no = ?''', (destination,))
        self.my_connection.commit()
        if_in = cursor.fetchall()
        cursor.close()
        if luhn_to_check == self.luhn_check:
            if len(if_in) >= 1 :
                try:
                    self.in_transfer = int(input("Enter how much money you want to transfer:"))
                except:
                    print('Please put only numbers.\n')
                    return
                if self.in_transfer <= self.new_balance():
                    print('Success!')
                    self.minus_income()
                    self.money_in_out(self.in_transfer, destination)
                else:
                    print('Not enough money!')
            else:
                print("Such a card does not exist.")
        else:
            print("Probably you made a mistake in the card number. Please try again!\n")

    def close_account(self):
        comfirm = input("Are you sure you want to proceed?:(y/n)")
        if comfirm == 'y':
            cursor = self.my_connection.cursor()
            cursor.execute(('''DELETE FROM cards 
                           WHERE card_no = ? AND pin = ?'''), 
                          (self.records[0][0], self.records[0][1]))
            self.my_connection.commit()
            cursor.close()
            print('The account has been closed!\n')
            return
        elif comfirm == 'n':
            self.log_in_options()
        elif comfirm != 'y' or comfirm != 'n':
                print("Please put y or n.\n")
                self.close_account()
                
    def log_in_options(self):
        if self.logged == 1:
            dif_option = input("1. Balance\n2. Add income\n3. Do transfer"
                               "\n4. Close account\n5. Log out\n0. Exit\n")
            while dif_option != '0':
                if dif_option == '1':
                    print("Balance:", self.new_balance(),'\n')
                elif dif_option == '2':
                    self.add_income()
                elif dif_option == '3':
                    self.transfer()
                elif dif_option == '4':
                    self.close_account()
                    return
                elif dif_option == '5':
                    print("You have successfully logged out!\n")
                    self.logged = 0
                    return
                dif_option = input("1. Balance\n2. Add income\n3. Do transfer"
                                   "\n4. Close account\n5. Log out\n0. Exit\n")
            else:
                self.option = '0'
                print("Bye!")
        else:
            print("Wrong card number or PIN!")
            
    def start_menu(self):
        self.option = input("1. Create an account \n2. Log into account \n0. Exit\n")
        if self.option == '1':
            return BankingSystem.create_account(self)
        elif self.option == '2':
            return BankingSystem.log_in_accont(self)
        elif self.option != "0":
            pass 
        elif self.option == '0':
            print("Bye!")
            return

BankingSystem()
