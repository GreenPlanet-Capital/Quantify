from datetime import datetime

from positions.opportunity import Opportunity


class Position(Opportunity):
    def __new__(cls, op: Opportunity):
        op.__class__ = cls
        return op

    def __init__(self, op):
        self.is_active = True
        self.exit_timestamp = False
        self.exit_price = False

    def pickle_position(self):
        pass

    def get_rows(self):
        parent_rows = super().get_rows()
        parent_rows.extend(([
            ('is_active', self.is_active),
            ('exit_timestamp', self.exit_timestamp),
            ('exit_price', self.exit_price)
        ]))
        return parent_rows

    def __repr__(self):
        return super().__repr__()
