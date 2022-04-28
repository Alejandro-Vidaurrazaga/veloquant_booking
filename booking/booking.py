import pandas as pd

PATH = 'C:/Users/Alejandro/Downloads/BookFGBL.csv'
NAMES = ['MessageType', 'Time', 'OrderId', 'Price', 'Quantity', 'Side']
CUSTOM_INPUT = [
    {'MessageType': 'Add', 'Time': 15002.63, 'OrderId': 15002, 'Price': 157.5, 'Quantity': 7, 'Side': 1},
    {'MessageType': 'Add', 'Time': 15003.05, 'OrderId': 15003, 'Price': 157.6, 'Quantity': 13, 'Side': -1},
    {'MessageType': 'Add', 'Time': 15003.07, 'OrderId': 15004, 'Price': 157.6, 'Quantity': 5, 'Side': -1},
    {'MessageType': 'Add', 'Time': 1500.12, 'OrderId': 15005, 'Price': 157.4, 'Quantity': 22, 'Side': 1},
    {'MessageType': 'Remove', 'Time': 15003.17, 'OrderId': 15003, 'Price': None, 'Quantity': None, 'Side': None},
    # {'MessageType': 'Add', 'Time': 15003.18, 'OrderId': 15015, 'Price': 157.5, 'Quantity': 3, 'Side': 1},
    {'MessageType': 'Trade', 'Time': 15003.19, 'OrderId': None, 'Price': 157.5, 'Quantity': 5, 'Side': None},
    {'MessageType': 'Reduce', 'Time': 15004.01, 'OrderId': 15005, 'Price': None, 'Quantity': 10, 'Side': None},
]
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
        printed_book = pd.concat([first_part.sort_values('Price', axis=0, ascending=False)[:5],
                                  second_part.sort_values('Price', axis=0, ascending=False)[:5]],
                                 axis=0, ignore_index=True)

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

    def reduce(self, row_to_manage):
        order_id = row_to_manage[self.order_id_field]
        row = self.historical.loc[self.historical['OrderId'] == order_id, ['Quantity', 'Side', 'Price']]
        quantity = row_to_manage[self.quantity_field]
        side = row.values[0][1]
        price = row.values[0][2]
        first_index = self.book[(self.book[self.price_field] == price) & (self.book[Booking.SIDE[side]] != -1)].index[0]
        self.book.loc[first_index, Booking.SIDE[side]] = quantity
        self.historical.loc[row.index[0], 'Quantity'] = quantity

    def remove(self, row_to_manage):
        order_id = row_to_manage[self.order_id_field]
        row = self.historical.loc[self.historical['OrderId'] == order_id, ['Quantity', 'Side', 'Price']]
        quantity = row.values[0][0]
        side = row.values[0][1]
        price = row.values[0][2]
        first_index = self.book[(self.book[self.price_field] == price) & (self.book[Booking.SIDE[side]] != -1)].index[0]
        self.book.loc[first_index, Booking.SIDE[side]] -= quantity

        if self.book.loc[first_index, Booking.SIDE[side]] <= 0:
            self.book.drop(first_index, inplace=True)

        self.historical.drop(row.index[0], inplace=True)

    def trade(self, row_to_manage):
        price = row_to_manage[self.price_field]
        quantity = row_to_manage[self.quantity_field]
        rows = self.historical.loc[self.historical['Price'] == price, ['Side', 'OrderId']]
        deleted = False

        for index, val in zip(rows.index, rows.values):
            side = val[0]
            historical_quantity = self.historical.loc[index, 'Quantity']

            if not deleted:
                deleted = True
                first_index = self.book[(self.book[self.price_field] == price) &
                                        (self.book[Booking.SIDE[side]] != -1)].index[0]
                self.book.loc[first_index, Booking.SIDE[side]] -= quantity

                if self.book.loc[first_index, Booking.SIDE[side]] <= 0:
                    self.book.drop(first_index, inplace=True)

            new_quantity = abs(quantity - historical_quantity)
            self.historical.loc[index, 'Quantity'] -= quantity
            quantity = new_quantity

            if self.historical.loc[index, 'Quantity'] <= 0:
                self.historical.drop(index, inplace=True)
            else:
                break


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
        elif row['MessageType'] == 'Reduce':
            booking.reduce(row)
        elif row['MessageType'] == 'Remove':
            booking.remove(row)
        else:
            booking.trade(row)

        booking.print_book(row['MessageType'])
