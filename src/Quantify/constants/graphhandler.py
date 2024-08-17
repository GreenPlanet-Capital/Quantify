from typing import Dict, Tuple

import numpy as np
import pandas as pd
from Quantify.constants.utils import find_loc
from Quantify.positions.position import Position
from DataManager.utils.timehandler import TimeHandler
import plotly.subplots as sp
import plotly.graph_objects as go


class GraphHandler:
    @staticmethod
    def graph_positions(dict_score_dfs: Dict[str, Tuple[pd.DataFrame, Position]]):
        for ticker, (df, position) in dict_score_dfs.items():
            req_df_cols = ["rsi", "health_score", "score"]

            fig = sp.make_subplots(
                rows=1 + len(req_df_cols),
                cols=1,
                shared_xaxes=True,
                subplot_titles=[f"{ticker} Stock Price", "Technical Indicators"],
                vertical_spacing=0.1,
                row_heights=[0.7, 0.15, 0.15, 0.15],
            )

            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                    name="Stock Price",
                ),
                row=1,
                col=1,
            )

            list_dates = [position.timestamp, position.exit_timestamp]
            list_dates = list(map(TimeHandler.get_string_from_datetime, list_dates))

            df["cleaned_timestamp"] = df["timestamp"].apply(
                TimeHandler.get_clean_string_from_string
            )
            list_locs = find_loc(df, list_dates)

            if not df.loc[list_locs[0]].empty:
                GraphHandler.add_graph_annotations(
                    fig, df.loc[list_locs[0]], position, "Enter", df.index[0]
                )
            if not df.loc[list_locs[1]].empty:
                GraphHandler.add_graph_annotations(
                    fig, df.loc[list_locs[1]], position, "Exit", df.index[0]
                )

            # Add MACD subplot with dynamic colors and smaller marker dots
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["macd"],
                    mode="lines",
                    marker=dict(color="red", size=3),  # Set the size of the marker dots
                    name="MACD Line",
                ),
                row=1,
                col=1,
            )

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["macd signal line"],
                    mode="lines",
                    marker=dict(
                        color="green", size=3
                    ),  # Set the size of the marker dots
                    name="MACD Signal Line",
                ),
                row=1,
                col=1,
            )

            # Moving Average
            fig.add_trace(
                go.Scatter(x=df.index, y=df["sma_bb"], line_color="black", name="sma"),
                row=1,
                col=1,
            )

            # Upper Bound
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["upper_bb"],
                    line_color="gray",
                    line={"dash": "dash"},
                    name="upper band",
                    opacity=0.01,
                ),
                row=1,
                col=1,
            )

            # Lower Bound fill in between with parameter 'fill': 'tonexty'
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["lower_bb"],
                    line_color="gray",
                    line={"dash": "dash"},
                    fill="tonexty",
                    name="lower band",
                    opacity=0.01,
                ),
                row=1,
                col=1,
            )

            import pdb

            pdb.set_trace()

            colors = ["blue", "purple", "orange"]

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
                yaxis2_title_text=req_df_cols[0],
                yaxis3_title_text=req_df_cols[1],
                yaxis4_title_text=req_df_cols[2],
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
    def add_graph_annotations(input_fig, list_locs, position, post_type, start_index=0):
        input_fig.add_annotation(
            x=list_locs["timestamp"].index[0] - start_index,
            y=list_locs["close"].iloc[0],
            text=f"{post_type} date (type: {position.order_type})",
            showarrow=True,
            arrowhead=1,
        )
