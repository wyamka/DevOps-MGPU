#!/usr/bin/env python3
"""
Визуализация факторов риска диабета с помощью Streamlit.

Савкина Мария. Вариант 25.
"""

import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import psycopg2


# Подключение к БД
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "diabetes")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")


@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    """Загрузка данных из PostgreSQL."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
    )

    df = pd.read_sql("SELECT * FROM diabetes_data;", conn)
    conn.close()
    return df


# Интерфейс
st.set_page_config(page_title="Diabetes Risk Analytics", layout="wide")

st.title("Аналитика факторов риска диабета")


# Загрузка данных
try:
    df = load_data()
except Exception as e:
    st.error(f"Не удалось подключиться к БД: {e}")
    st.info("Убедитесь, что контейнер loader завершил загрузку данных.")
    st.stop()


# Sidebar фильтры
st.sidebar.header("Фильтры")

age_range = st.sidebar.slider(
    "Возраст",
    int(df["age"].min()),
    int(df["age"].max()),
    (int(df["age"].min()), int(df["age"].max())),
)

df_filtered = df[(df["age"] >= age_range[0]) & (df["age"] <= age_range[1])]


# Основные метрики
col1, col2, col3, col4 = st.columns(4)

col1.metric("Всего пациентов", f"{len(df_filtered)}")
col2.metric("Средний возраст", f"{df_filtered['age'].mean():.1f}")
col3.metric("Средний ИМТ", f"{df_filtered['bmi'].mean():.1f}")
col4.metric("Диабет (доля)", f"{df_filtered['outcome'].mean()*100:.1f}%")


# Гистограмма глюкозы
st.subheader("Распределение уровня глюкозы")

fig_glucose = px.histogram(
    df_filtered,
    x="glucose",
    nbins=30,
    color="outcome",
    labels={"glucose": "Уровень глюкозы", "outcome": "Диабет"},
)

st.plotly_chart(fig_glucose, use_container_width=True)


# ИМТ и диабет
st.subheader("Связь ИМТ и диабета")

fig_bmi = px.box(
    df_filtered,
    x="outcome",
    y="bmi",
    labels={"outcome": "Диабет (0 = нет, 1 = да)", "bmi": "BMI"},
)

st.plotly_chart(fig_bmi, use_container_width=True)


# Связь возраста и уровня глюкозы
st.subheader("Возраст и уровень глюкозы")

fig_scatter = px.scatter(
    df_filtered,
    x="age",
    y="glucose",
    color="outcome",
    labels={"age": "Возраст", "glucose": "Глюкоза", "outcome": "Диабет"},
)

st.plotly_chart(fig_scatter, use_container_width=True)


# Корреляционная тепловая карта медицинских показателей
st.subheader("Корреляция медицинских показателей")

corr = df_filtered[
    [
        "pregnancies",
        "glucose",
        "blood_pressure",
        "skin_thickness",
        "insulin",
        "bmi",
        "diabetes_pedigree_function",
        "age",
        "outcome",
    ]
].corr()

fig_corr = go.Figure(
    data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale="RdBu",
        zmin=-1,
        zmax=1,
    )
)

st.plotly_chart(fig_corr, use_container_width=True)


st.caption(
    "Источник данных: diabetes dataset new • "
    "Streamlit + Plotly + PostgreSQL • Docker analytics project"
)
