from pandas import DataFrame


class BaseIndicator:
    def set_dataframe(self, dataframe: DataFrame):
        self.dataframe = dataframe

    def _zero_dataframe(self):
        self.dataframe = None

    def run(self):
        """
        Modifies the dataframe with the added column of the indicator
        """
        assert self.dataframe is not None, "DataNoneError: Indicator dataframe not set"