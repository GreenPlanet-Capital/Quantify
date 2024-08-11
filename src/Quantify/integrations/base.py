from typing import List
from Quantify.positions.position import Position


class BaseIntegration:
    def __init__(self, strat_id: int) -> None:
        self.strat_id = strat_id
        self.authenticate()

    def authenticate(self) -> None:
        raise NotImplementedError

    def get_open_positions(self) -> List[Position]:
        raise NotImplementedError
