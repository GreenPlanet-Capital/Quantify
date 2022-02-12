from pandas import DataFrame


class BaseIndicator:
    def set_dataframe(self, dataframe: DataFrame):
        assert dataframe['close'].isna().sum()==0, "NaNError: There are NaN values in the Dataframe supplied"
        self._dataframe = dataframe

    def _zero_dataframe(self):
        self._dataframe = None

    def run(self) -> DataFrame:
        """
        Returns a dataframe with the results of the indicator
        """
        assert self._dataframe is not None, "DataNoneError: Indicator dataframe not set"