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
compact_frequency = {"Ponctuel": "p", "Hebdomadaire": "w", "Mensuel": "m"}

st.title("Ca[py]tal simulator")

st.subheader("Vue sur les comptes")
with st.sidebar:
    with st.expander("Ajouter des mouvements"):
        start = st.date_input(
            "Début de la période", value=datetime.now(), min_value=datetime.now()
        )
        frequency = st.selectbox(
            "Fréquence", options=("Ponctuel", "Hebdomadaire", "Mensuel")
        )
        frequency = compact_frequency[frequency]
        if frequency in ("m", "w"):
            end = st.date_input(
                "Fin de la période",
                value=datetime.now() + timedelta(weeks=1),
                min_value=datetime.now() + timedelta(weeks=1),
            )

        else:
            end = None
        amount = int(st.text_input("Montant", value="0"))
        label = st.text_input("Label")
        conditionnal = st.text_input("Hypothèse", value="base")
        button = st.button(
            "Ajouter",
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

    with st.expander("Selectionner des hypothèses"):
        selected_conditionnals = st.multiselect("Hypothèses", conditionnals)
    with st.expander("Epargne"):
        initial_savings = st.number_input("Epargne initiale", value=initial_savings)
        saving_threshold = st.number_input(
            "Montant minimal dans le compte courant", value=saving_threshold
        )




final_date = st.date_input(
    "Simuler jusqu'à ...",
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
    px.line(df, y=["Compte courant", "Epargne"], hover_data=["label", "Mouvement"])
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "Minimum dans le compte courant",
        df.loc[:, "Compte courant"].min(),
        delta=None,
        delta_color="normal",
        help=None,
    )
with col2:
    st.metric(
        "Minimum de capital total",
        df.loc[:, ["Compte courant", "Epargne"]].sum(axis=1).min(),
        delta=None,
        delta_color="normal",
        help=None,
    )

with col3:
    st.metric(
        "Montant moyen dans le compte courant",
        int(df.loc[:, "Compte courant"].mean()),
        delta=None,
        delta_color="normal",
        help=None,
    )


st.subheader("Dépenses")
df1 = df[df.label !='No Mouvement']
grouped_df = df1.groupby(by="label").sum()
st.plotly_chart(
    px.pie(
        values=grouped_df[grouped_df.movement < 0].movement.abs(),
        names=grouped_df[grouped_df.movement < 0].index,
    )
)
st.subheader("Rentrées")
st.plotly_chart(
    px.pie(
        values=grouped_df[grouped_df.movement > 0].movement.abs(),
        names=grouped_df[grouped_df.movement > 0].index,
    )
)

with st.expander("Montrer le dataframe"):
    df
