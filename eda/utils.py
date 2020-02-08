import colorlover as cl
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

_COLORS = cl.scales["11"]["div"]["Spectral"]
_TEMPLATE = "plotly_white"


def plot_series(df, title="", colors=_COLORS):
    """
    A simple plotly wrapper to plot time series.
    :param df: pd.DataFrame
    :param title: str
    :param colors: a list of colors
    """
    fig = go.Figure()
    x = df.index
    for i, var in enumerate(df.columns):
        fig.add_trace(
            go.Scatter(x=x, y=df[var].values, name=var, line=dict(color=colors[i]))
        )
    fig.update_layout(template=_TEMPLATE, title=title, legend_orientation="h")
    return fig


def plot_heatmap(df, title=""):
    """
    Plotly heatmap wrapper
    :param df: pd.DataFrame
    :param title: str
    """
    fig = go.Figure(
        data=go.Heatmap(z=df.values, x=df.columns, y=df.index, colorscale="RdBu")
    )
    fig.update_layout(template=_TEMPLATE, title=title, legend_orientation="h")
    return fig


def plot_bars(df, title=""):
    """
    Plotly express bar wrapper
    :param df: pd.DataFrame
    :param title: str
    :return:
    """
    fig = px.bar(
        df.reset_index().iloc[-30:, :],
        y="mean_coverage",
        x="country_code",
        color_discrete_sequence=[_COLORS[-2]],
    )
    fig.update_layout(template=_TEMPLATE, title=title, legend_orientation="h")
    return fig


def compute_coverage(df_num, df_denom):
    """
    Return a dataframe merged on ["country_code", "year"] and the share of families which have a
    full-text description
    :param df_num: pd.DataFrame
    :param df_denom: pd.DataFrame
    """
    df = pd.merge(
        df_num,
        df_denom,
        how="left",
        on=["country_code", "year"],
        suffixes=("_num", "_denom"),
    )
    df["coverage"] = df["count_num"] / df["count_denom"]

    df_c = (
        df[["country_code", "year", "coverage"]]
        .query("year>=1978")
        .pivot(index="country_code", columns="year")["coverage"]
    )
    df_c = df_c.fillna(0)
    df_c["mean_coverage"] = df_c.mean(axis=1)
    return df_c.sort_values("mean_coverage")
