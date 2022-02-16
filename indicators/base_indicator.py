from pandas import DataFrame, Series


class BaseIndicator:
    def run(self, input_dataframe: DataFrame):
        """
        Returns a dataframe with the results of the indicator
        """
        assert input_dataframe is not None, "DataNoneError: Indicator dataframe not set"

    def insert_all_into_df(self, input_df: DataFrame, contains_dataframe: DataFrame, list_columns: [str]):
        for i in range(len(list_columns)):
            input_df[list_columns[i]] = contains_dataframe[list_columns[i]]

    def graph(self, input_dataframe: DataFrame):
        assert input_dataframe is not None, "DataNoneError: Indicator dataframe not set"
