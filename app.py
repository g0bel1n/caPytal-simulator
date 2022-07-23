from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from capytal import Accountant, MoneyFlow


def init_write(**kwargs):
    if kwargs["amount"] != 0:
        MoneyFlow(**kwargs).write()


conditionnals = list(pd.read_csv("logs/logs.csv").iloc[:, 3].unique())
conditionnals.remove("base")
selected_conditionnals = []
final_date = "2022-12-31"
initial_savings = 282
saving_threshold = 400


st.title("Ca[py]tal simulator")

st.subheader("Money in Bank")
with st.sidebar:
    with st.expander("Add Data"):
        start = st.date_input(
            "Start of period", value=datetime.now(), min_value=datetime.now()
        )
        frequency = st.selectbox("Frequency", options=("p", "w", "m"))
        if frequency in ("m", "w"):
            end = st.date_input(
                "End of period",
                value=datetime.now() + timedelta(weeks=1),
                min_value=datetime.now() + timedelta(weeks=1),
            )

        else:
            end = None
        amount = int(st.text_input("Amount", value="0"))
        label = st.text_input("Label")
        conditionnal = st.text_input("Conditionnal ? ", value="base")
        button = st.button(
            "Add",
            on_click=init_write,
            kwargs=dict(
                amount=amount,
                start=start,
                end=end,
                label=label,
                conditionnal=conditionnal,
                frequency=frequency,
            ),
        )

    with st.expander("Select situation"):
        selected_conditionnals = st.multiselect("Situations", conditionnals)
    with st.expander("Savings"):
        initial_savings = st.number_input("Initial savings", value=initial_savings)
        saving_threshold = st.number_input("Saving Threshold", value=saving_threshold)

final_date = st.date_input(
    "Simulate until ?",
    min_value=datetime.now(),
    value=datetime.strptime("2022-12-31", "%Y-%m-%d"),
)
df = Accountant(
    end=final_date,
    hypothesises=selected_conditionnals,
    initial_savings=initial_savings,
    threshold=saving_threshold,
)
df = df[df.label != "No movement"]

if button:
    df = Accountant(
        end=final_date,
        hypothesises=selected_conditionnals,
        initial_savings=initial_savings,
        threshold=saving_threshold,
    )
    df = df[df.label != "No movement"]

st.plotly_chart(
    px.line(df, y=["bank_account", "savings"], hover_data=["label", "movement"])
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "Minimum active money in bank",
        df.loc[:, "bank_account"].min(),
        delta=None,
        delta_color="normal",
        help=None,
    )
with col2:
    st.metric(
        "Minimum total money in bank",
        df.loc[:, ["bank_account", "savings"]].sum(axis=1).min(),
        delta=None,
        delta_color="normal",
        help=None,
    )

with col3:
    st.metric(
        "Average active money in bank",
        int(df.loc[:, "bank_account"].mean()),
        delta=None,
        delta_color="normal",
        help=None,
    )


st.subheader("Expenses")
grouped_df = df.groupby(by="label").sum()
st.plotly_chart(
    px.pie(
        values=grouped_df[grouped_df.movement < 0].movement.abs(),
        names=grouped_df[grouped_df.movement < 0].index,
    )
)
st.subheader("Gains")
st.plotly_chart(
    px.pie(
        values=grouped_df[grouped_df.movement > 0].movement.abs(),
        names=grouped_df[grouped_df.movement > 0].index,
    )
)

with st.expander("show df"):
    df
