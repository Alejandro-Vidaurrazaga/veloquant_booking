import numpy as np
import pandas as pd
# from matplotlib import pyplot as plt

PATH = 'C:/Users/Alejandro/Downloads/BookFGBL.csv'
NAMES = ['MessageType', 'Time', 'OrderId', 'Price', 'Quantity', 'Side']
CUSTOM_INPUT = False


class Booking:
    SIDE = {
        -1: 'Ask',
        1: 'Bid'
    }

    def __init__(self, price_field, quantity_field, side_field):
        self.book = pd.DataFrame([], columns=['Bid', 'Price', 'Ask'])
        self.quantity_field = quantity_field
        self.price_field = price_field
        self.side_field = side_field

    def print_book(self):
        first_part = self.book[self.book['Ask'] != -1]
        second_part = self.book[self.book['Bid'] != -1]
        printed_book = pd.concat([first_part, second_part], axis=0, ignore_index=True)

        print(printed_book[['Bid', 'Price', 'Ask']], '\n')

    def add(self, row_to_add):
        quantity = row_to_add[self.quantity_field]
        price = row_to_add[self.price_field]
        side = row_to_add[self.side_field]

        if self.book.shape[0] == 0:
            self._add(price, quantity, side)
        else:
            try:
                first_index = self.book[(self.book[self.price_field] == price) &
                                        (self.book[Booking.SIDE[side]] != -1)].index[0]
                self.book.loc[first_index, Booking.SIDE[side]] += quantity
            except IndexError:
                self._add(price, quantity, side)

        self.print_book()

    def _add(self, price, quantity, side):
        in_element = pd.DataFrame([{Booking.SIDE[side]: quantity, 'Price': price, Booking.SIDE[-side]: -1}])
        self.book = pd.concat([self.book, in_element], axis=0, ignore_index=True)

    def remove(self, row_to_romove):
        pass


def read_input(custom_input=False, *, path=None, names=None):
    if not custom_input:
        return pd.read_csv(path, names=names)


if __name__ == '__main__':
    data = read_input(CUSTOM_INPUT, path=PATH, names=NAMES)
    booking = Booking('Price', 'Quantity', 'Side')

    for index, row in data.iterrows():
        if row['MessageType'] == 'Add':
            booking.add(row)
