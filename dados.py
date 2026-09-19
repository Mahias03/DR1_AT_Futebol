import streamlit as st
from statsbombpy import sb

@st.cache_data
def carregar_competicoes():
    competicoes = sb.competitions()
    return competicoes

@st.cache_data
def carregar_partidas(competition_id, season_id):
    partidas = sb.matches(
        competition_id=competition_id,
        season_id=season_id
    )
    return partidas

@st.cache_data
def carregar_eventos(match_id):
    eventos = sb.events(match_id=match_id)
    return eventos