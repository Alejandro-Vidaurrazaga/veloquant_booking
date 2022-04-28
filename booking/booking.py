import numpy as np
import pandas as pd
# from matplotlib import pyplot as plt

PATH = 'C:/Users/Alejandro/Downloads/BookFGBL.csv'
NAMES = ['MessageType', 'Time', 'OrderId', 'Price', 'Quantity', 'Side']
CUSTOM_INPUT = None


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

    def print_book(self, operation=None):
        first_part = self.book[self.book['Ask'] != -1]
        second_part = self.book[self.book['Bid'] != -1]
        printed_book = pd.concat([first_part, second_part], axis=0, ignore_index=True)

        if operation is not None:
            print(operation)

        print(printed_book[['Bid', 'Price', 'Ask']], '\n')

    @staticmethod
    def _add(df, row_to_save):
        in_element = pd.DataFrame([row_to_save])
        # in_element = pd.DataFrame([{Booking.SIDE[side]: quantity, 'Price': price, Booking.SIDE[-side]: -1}])
        return pd.concat([df, in_element], axis=0, ignore_index=True)

    def add(self, row_to_manage):
        quantity = row_to_manage[self.quantity_field]
        price = row_to_manage[self.price_field]
        side = row_to_manage[self.side_field]
        order_id = row_to_manage[self.order_id_field]

        if self.book.shape[0] != 0:
            try:
                first_index = self.book[(self.book[self.price_field] == price) &
                                        (self.book[Booking.SIDE[side]] != -1)].index[0]
                self.book.loc[first_index, Booking.SIDE[side]] += quantity
            except IndexError:
                self.book = Booking._add(self.book, {Booking.SIDE[side]: quantity, 'Price': price,
                                                     Booking.SIDE[-side]: -1})
        else:
            self.book = Booking._add(self.book, {Booking.SIDE[side]: quantity, 'Price': price, Booking.SIDE[-side]: -1})

        self.historical = Booking._add(self.historical, {'Quantity': quantity, 'OrderId': order_id, 'Side': side,
                                                         'Price': price})
        self.print_book('Add')

    def remove(self, row_to_manage):
        order_id = row_to_manage[self.order_id_field]
        row = self.historical.loc[self.historical['OrderId'] == order_id, ['Quantity', 'Side', 'Price']]
        quantity = row.values[0][0]
        side = row.values[0][1]
        price = row.values[0][2]
        first_index = self.book[(self.book[self.price_field] == price) & (self.book[Booking.SIDE[side]] != -1)].index[0]
        self.book.loc[first_index, Booking.SIDE[side]] -= quantity

        if self.book.loc[first_index, Booking.SIDE[side]] == 0:
            self.book.drop(first_index, inplace=True)

        self.historical.drop(row.index[0], inplace=True)

        self.print_book('Remove')


def read_input(custom_input=None, *, path=None, names=None):
    if custom_input is None:
        return pd.read_csv(path, names=names)

    if isinstance(custom_input, dict):
        return pd.DataFrame([custom_input])

    if isinstance(custom_input, list):
        return pd.DataFrame(custom_input)

    return pd.DataFrame([])


if __name__ == '__main__':
    data = read_input(CUSTOM_INPUT, path=PATH, names=NAMES)
    booking = Booking('Price', 'Quantity', 'Side', 'OrderId')

    for index, row in data.iterrows():
        if row['MessageType'] == 'Add':
            booking.add(row)
        elif row['MessageType'] == 'Remove':
            booking.remove(row)
