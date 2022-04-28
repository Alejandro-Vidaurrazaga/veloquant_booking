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

    def __init__(self, price_field, quantity_field, side_field, order_id_field):
        self.book = pd.DataFrame([], columns=['Bid', 'Price', 'Ask'])
        self.historical = pd.DataFrame([], columns=['OrderId', 'Quantity', 'Side'])
        self.quantity_field = quantity_field
        self.price_field = price_field
        self.side_field = side_field
        self.order_id_field = order_id_field

    def print_book(self):
        first_part = self.book[self.book['Ask'] != -1]
        second_part = self.book[self.book['Bid'] != -1]
        printed_book = pd.concat([first_part, second_part], axis=0, ignore_index=True)

        print(printed_book[['Bid', 'Price', 'Ask']], '\n')

    def add(self, row_to_add):
        quantity = row_to_add[self.quantity_field]
        price = row_to_add[self.price_field]
        side = row_to_add[self.side_field]
        order_id = row_to_add[self.order_id_field]

        if self.book.shape[0] == 0:
            self.book = Booking._add(self.book, {Booking.SIDE[side]: quantity, 'Price': price, Booking.SIDE[-side]: -1})
        else:
            try:
                first_index = self.book[(self.book[self.price_field] == price) &
                                        (self.book[Booking.SIDE[side]] != -1)].index[0]
                self.book.loc[first_index, Booking.SIDE[side]] += quantity
            except IndexError:
                self.book = Booking._add(self.book, {Booking.SIDE[side]: quantity, 'Price': price,
                                                     Booking.SIDE[-side]: -1})

        self.historical = Booking._add(self.historical, {'Quantity': quantity, 'OrderId': order_id, 'Side': side})
        self.print_book()

    @staticmethod
    def _add(df, row_to_save):
        in_element = pd.DataFrame([row_to_save])
        # in_element = pd.DataFrame([{Booking.SIDE[side]: quantity, 'Price': price, Booking.SIDE[-side]: -1}])
        return pd.concat([df, in_element], axis=0, ignore_index=True)

    def remove(self, row_to_remove):
        pass


def read_input(custom_input=False, *, path=None, names=None):
    if not custom_input:
        return pd.read_csv(path, names=names)


if __name__ == '__main__':
    data = read_input(CUSTOM_INPUT, path=PATH, names=NAMES)
    booking = Booking('Price', 'Quantity', 'Side', 'OrderId')

    for index, row in data.iterrows():
        if row['MessageType'] == 'Add':
            booking.add(row)
        elif row['MessageType'] == 'Remove':
            booking.remove(row)
