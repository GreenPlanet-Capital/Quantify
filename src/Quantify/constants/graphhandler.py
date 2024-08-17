from typing import Dict, Tuple

import pandas as pd
from Quantify.constants.utils import find_loc
from Quantify.positions.position import Position
from DataManager.utils.timehandler import TimeHandler
import plotly.subplots as sp
import plotly.graph_objects as go


class GraphHandler:
    @staticmethod
    def graph_positions(
        dict_of_dfs: Dict[str, pd.DataFrame],
        dict_score_dfs: Dict[str, Tuple[pd.DataFrame, Position]],
        min_start_index: int,
    ):
        for ticker, (df, position) in dict_score_dfs.items():
            fig = sp.make_subplots(
                rows=3,
                cols=1,
                shared_xaxes=True,
                subplot_titles=[f"{ticker} Stock Prices", "Technical Indicators"],
                vertical_spacing=0.1,
                row_heights=[0.7, 0.15, 0.15],
            )

            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                    name="Stock Prices",
                ),
                row=1,
                col=1,
            )

            req_df_cols = ["health_score", "score"]
            colors = ["green", "red", "blue", "orange", "purple", "black"]

            for i, col in enumerate(req_df_cols):
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[col],
                        mode="lines",
                        line=dict(color=colors[i % len(colors)]),
                        name=col,
                    ),
                    row=2 + i,
                    col=1,
                )

            fig.update_layout(
                xaxis_rangeslider_visible=False,
                template="plotly_white",
                title_text=f"{ticker} Stock Analysis",
                xaxis=dict(
                    type="category"
                ),  # Set x-axis type to category which removes the sat and sun gap
                xaxis_title_text="Date",
                yaxis_title_text="Price",
                yaxis2_title_text=req_df_cols[0],  # Add y-axis title for ATR subplot
                yaxis3_title_text=req_df_cols[1],  # Add y-axis title for RSI subplot
                height=800,  # Set the height of the figure
                width=1200,
            )  # Set the width of the figure

            fig.show()

    @staticmethod
    def graph_positions_legacy(
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
