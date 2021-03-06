import os
from typing import Any, List, Tuple
from uuid import uuid4

from pandas import DataFrame

from Quantify.positions.opportunity import Opportunity
from Quantify.constants.constant_defs import tracked_trades_path
import pickle


class Position(Opportunity):
    def __init__(self, op: Opportunity):
        self.__dict__.update(op.__dict__)
        self.is_active = True
        self.exit_timestamp = False
        self.exit_price = False
        self.uuid = uuid4().hex
        self.pickle_name = f"{self.ticker + self.uuid}"
        self.health_df = DataFrame()

    def pickle(self):
        with open(
            os.path.join(tracked_trades_path, f"{self.pickle_name}.pickle"), "wb"
        ) as file_to_store:
            pickle.dump(self, file_to_store)

    @staticmethod
    def depickle(trades_path, pickle_name):
        # TODO Show tracked has .pickle.pickle
        with open(
            os.path.join(trades_path, f"{pickle_name}.pickle"), "rb"
        ) as file_to_read:
            loaded_object = pickle.load(file_to_read)

        return loaded_object

    def get_rows(
        self,
        pre_entries: List[Tuple[str, Any]] = [],
        post_entries: List[Tuple[str, Any]] = [],
    ):
        pre_entries = pre_entries + [("uuid", self.uuid)]
        post_entries = (
            [
                ("is_active", self.is_active),
                ("exit_timestamp", self.exit_timestamp),
                ("exit_price", self.exit_price),
            ]
        ) + post_entries

        rows = super().get_rows(
            pre_entries=pre_entries,
            post_entries=post_entries,
        )
        return rows

    def __repr__(self):
        return super().__repr__()
