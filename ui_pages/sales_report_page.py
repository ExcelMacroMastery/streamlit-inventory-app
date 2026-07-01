import streamlit as st
import pandas as pd
import plotly.express as px
from data.sales_report_db import load_sales_by_day, load_sales_by_category

def draw_sales_by_day(df: pd.DataFrame):
    st.subheader("Revenue by Day")

    if df.empty:
        st.info("No sales data yet.")
        return

    df["day"] = pd.to_datetime(df["day"], format="%Y-%m-%d")

    fig = px.line(
        df,
        x="day",
        y="revenue",
        markers=True,
        labels={"day": "Date", "revenue": "Revenue ($)"},
    )
    fig.update_xaxes(
        tickformat="%b %d, %Y",
        dtick="D1",  # one tick per day
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Revenue ($)",
        yaxis_tickformat="$,.0f",
        hovermode="x unified",
        margin=dict(t=20),
    )
    fig.update_traces(
        hovertemplate="$%{y:,.2f}",
        line_color="#2563eb",
        marker_color="#2563eb",
    )

    st.plotly_chart(fig, use_container_width=True)


def draw_sales_by_category(df: pd.DataFrame):
    st.subheader("Revenue by Category")

    if df.empty:
        st.info("No sales data yet.")
        return

    fig = px.pie(
        df,
        names="category",
        values="revenue",
        hole=0.4,
    )
    fig.update_layout(margin=dict(t=20))
    fig.update_traces(
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>$%{value:,.2f}<extra></extra>",
    )
    st.plotly_chart(fig, use_container_width=True)


def render():
    st.header("Sales Reports")

    monthly_df  = load_sales_by_day()
    category_df = load_sales_by_category()

    draw_sales_by_day(monthly_df)

    st.divider()

    draw_sales_by_category(category_df)