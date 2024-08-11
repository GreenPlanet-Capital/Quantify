from typing import Dict, Tuple

import pandas as pd
from Quantify.constants.utils import find_loc
from Quantify.positions.position import Position
from DataManager.utils.timehandler import TimeHandler


class GraphHandler:
    @staticmethod
    def graph_positions(
        dict_of_dfs: Dict[str, pd.DataFrame],
        dict_score_dfs: Dict[str, Tuple[pd.DataFrame, Position]],
        min_start_index: int,
    ):
        for ticker, tuple_df_pos in dict_score_dfs.items():
            score_df, this_pos = tuple_df_pos
            to_graph = pd.concat(
                [
                    dict_of_dfs[ticker][["close", "timestamp"]][min_start_index - 1 :],
                    score_df[["score", "health_score"]],
                ],
                axis=1,
            )

            list_dates = [this_pos.timestamp, this_pos.exit_timestamp]
            list_dates = list(map(TimeHandler.get_string_from_datetime, list_dates))

            to_graph["graph_score"] = to_graph["score"] * 10 + to_graph["close"].mean()
            to_graph["graph_health_score"] = (
                to_graph["health_score"] * 10 + to_graph["close"].mean()
            )

            fig = to_graph.plot(
                x="timestamp",
                y=[
                    to_graph["graph_score"],
                    to_graph["close"],
                    to_graph["graph_health_score"],
                ],
                title=f"Stock Ticker: {ticker}",
            )

            to_graph["cleaned_timestamp"] = to_graph["timestamp"].apply(
                TimeHandler.get_clean_string_from_string
            )
            list_locs = find_loc(to_graph, list_dates)

            GraphHandler.add_graph_annotations(
                fig, to_graph.loc[list_locs[0]], this_pos, "Enter"
            )
            GraphHandler.add_graph_annotations(
                fig, to_graph.loc[list_locs[1]], this_pos, "Exit"
            )
            fig.update_layout(showlegend=False)
            fig.show()

    @staticmethod
    def add_graph_annotations(input_fig, list_locs, curr_position, position_do):
        input_fig.add_annotation(
            x=list_locs["timestamp"].iloc[0],
            y=list_locs["close"].iloc[0],
            text=f"{position_do} date (type: {curr_position.order_type})",
            showarrow=True,
            arrowhead=1,
        )
