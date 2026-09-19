# Football Analytics Dashboard

Dashboard interativo desenvolvido em Python e Streamlit para análise de partidas de futebol utilizando dados públicos da StatsBomb.

## Objetivo

O projeto permite explorar partidas, equipes e jogadores a partir de eventos registrados durante os jogos, facilitando a análise de passes, finalizações, gols e outras ações.

## Funcionalidades

- Seleção de competição, temporada e partida.
- Filtro por equipe e jogador.
- Métricas gerais da partida.
- Estatísticas individuais de jogadores.
- Mapa de chutes.
- Mapa de passes completos e incompletos.
- Comparação entre passes e finalizações dos jogadores.
- Filtros avançados de eventos por período, tipo e busca textual.
- Download dos eventos filtrados em formato CSV.
- Uso de cache para otimização do carregamento dos dados.
- Uso de Session State para controle dos filtros da aplicação.

## Tecnologias utilizadas

- Python
- Streamlit
- StatsBombPy
- mplsoccer
- Pandas
- Matplotlib
- Seaborn

## Fonte dos dados

Os dados utilizados são provenientes do conjunto de dados abertos disponibilizado pela StatsBomb e acessados através da biblioteca StatsBombPy.