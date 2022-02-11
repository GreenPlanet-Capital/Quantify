from pandas import DataFrame


class BaseIndicator:
    def set_dataframe(self, dataframe: DataFrame):
        self._dataframe = dataframe

    def _zero_dataframe(self):
        self._dataframe = None

    def run(self) -> DataFrame:
        """
        Returns a dataframe with the results of the indicator
        """
        assert self._dataframe is not None, "DataNoneError: Indicator dataframe not set"