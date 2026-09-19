import streamlit as st
from dados import carregar_competicoes, carregar_partidas, carregar_eventos
from graficos import mapa_chutes, mapa_passes, grafico_passes_chutes

st.set_page_config(
    page_title="Football Analytics",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Football Analytics Dashboard")

st.write(
    "Dashboard interativo para análise de partidas de futebol "
    "utilizando dados da StatsBomb."
)

# Carregar competições
competicoes = carregar_competicoes()

# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.header("Filtros")

# Criar lista de competições sem repetir temporadas
lista_competicoes = (
    competicoes[
        ["competition_id", "country_name", "competition_name"]
    ]
    .drop_duplicates()
    .sort_values(["country_name", "competition_name"])
)

lista_competicoes["nome_exibicao"] = (
    lista_competicoes["country_name"]
    + " - "
    + lista_competicoes["competition_name"]
)

competicao_escolhida = st.sidebar.selectbox(
    "Competição",
    lista_competicoes["nome_exibicao"],
    key="competicao_select"
)

# Descobrir ID da competição escolhida
competition_id = lista_competicoes.loc[
    lista_competicoes["nome_exibicao"] == competicao_escolhida,
    "competition_id"
].iloc[0]

# Filtrar temporadas dessa competição
temporadas = competicoes[
    competicoes["competition_id"] == competition_id
]

temporada_escolhida = st.sidebar.selectbox(
    "Temporada",
    temporadas["season_name"],
    key=f"temporada_select_{competition_id}"
)

# Descobrir ID da temporada escolhida
season_id = temporadas.loc[
    temporadas["season_name"] == temporada_escolhida,
    "season_id"
].iloc[0]

# Carregar partidas
partidas = carregar_partidas(
    competition_id,
    season_id
)

# Criar nome amigável para cada partida
partidas["partida"] = (
    partidas["home_team"]
    + " "
    + partidas["home_score"].astype(str)
    + " x "
    + partidas["away_score"].astype(str)
    + " "
    + partidas["away_team"]
)

partida_escolhida = st.sidebar.selectbox(
    "Partida",
    partidas["partida"],
    key=f"partida_select_{competition_id}_{season_id}"
)

# Encontrar a partida selecionada
partida = partidas[
    partidas["partida"] == partida_escolhida
].iloc[0]
match_id = partida["match_id"]

# -------------------------
# CONTEÚDO PRINCIPAL
# -------------------------

with st.container(border=True):
    st.subheader(partida_escolhida)

    info1, info2, info3 = st.columns(3)

    info1.markdown(f"**Competição:** {competicao_escolhida}")
    info2.markdown(f"**Temporada:** {temporada_escolhida}")
    info3.markdown(f"**Data:** {partida['match_date']}")

with st.spinner("Carregando eventos da partida..."):
    progresso = st.progress(0, text="Carregando eventos...")
    eventos = carregar_eventos(match_id)
    progresso.progress(60, text="Preparando dados da partida...")
    eventos_jogo = eventos[eventos["period"] != 5].copy() # Excluir disputa de pênaltis das estatísticas da partida
    progresso.progress(100, text="Dados carregados com sucesso.")

progresso.empty()

# -------------------------
# FILTROS DE EQUIPE E JOGADOR
# -------------------------

equipes = sorted(eventos["team"].dropna().unique())

equipe_escolhida = st.sidebar.selectbox(
    "Equipe",
    ["Todas"] + equipes,
    key=f"equipe_select_{match_id}"
)

eventos_filtrados = eventos_jogo.copy()

if equipe_escolhida != "Todas":
    eventos_filtrados = eventos_filtrados[
        eventos_filtrados["team"] == equipe_escolhida
    ]

jogadores = sorted(
    eventos_filtrados["player"]
    .dropna()
    .unique()
)

jogador_escolhido = st.sidebar.selectbox(
    "Jogador",
    ["Todos"] + jogadores,
    key=f"jogador_select_{match_id}_{equipe_escolhida}"
)

if jogador_escolhido != "Todos":
    eventos_filtrados = eventos_filtrados[
        eventos_filtrados["player"] == jogador_escolhido
    ]

st.session_state["filtros_atuais"] = {
    "competicao": competicao_escolhida,
    "temporada": temporada_escolhida,
    "partida": partida_escolhida,
    "match_id": int(match_id),
    "equipe": equipe_escolhida,
    "jogador": jogador_escolhido
}

# -------------------------
# MÉTRICAS DA PARTIDA
# -------------------------

passes = eventos_jogo[eventos_jogo["type"] == "Pass"]
chutes = eventos_jogo[eventos_jogo["type"] == "Shot"]
gols = chutes[chutes["shot_outcome"] == "Goal"]

total_passes = len(passes)
total_chutes = len(chutes)
total_gols = len(gols)

if total_chutes > 0:
    taxa_conversao = (total_gols / total_chutes) * 100
else:
    taxa_conversao = 0

with st.container(border=True):
    st.caption("Métricas gerais da partida — disputa de pênaltis não incluída")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("⚽ Gols", total_gols)
    col2.metric("🥅 Chutes", total_chutes)
    col3.metric("🎯 Passes", total_passes)
    col4.metric("📈 Conversão", f"{taxa_conversao:.1f}%")

# -------------------------
# MÉTRICAS DO JOGADOR
# -------------------------

if jogador_escolhido != "Todos":

    passes_jogador = eventos_filtrados[
        eventos_filtrados["type"] == "Pass"
    ]

    chutes_jogador = eventos_filtrados[
        eventos_filtrados["type"] == "Shot"
    ]

    gols_jogador = chutes_jogador[
        chutes_jogador["shot_outcome"] == "Goal"
    ]

    passes_completos_jogador = passes_jogador[
        passes_jogador["pass_outcome"].isna()
    ]

    total_passes_jogador = len(passes_jogador)
    total_passes_completos = len(passes_completos_jogador)
    total_chutes_jogador = len(chutes_jogador)
    total_gols_jogador = len(gols_jogador)

    if total_passes_jogador > 0:
        aproveitamento_passes = (
            total_passes_completos / total_passes_jogador
        ) * 100
    else:
        aproveitamento_passes = 0

    with st.container(border=True):
        st.subheader(f"Resumo de {jogador_escolhido}")

        jog1, jog2, jog3, jog4, jog5 = st.columns(5)

        jog1.metric("Passes tentados", total_passes_jogador)
        jog2.metric("Passes completos", total_passes_completos)
        jog3.metric("Aproveitamento", f"{aproveitamento_passes:.1f}%")
        jog4.metric("Chutes", total_chutes_jogador)
        jog5.metric("Gols", total_gols_jogador)

chutes_filtrados = eventos_filtrados[
    eventos_filtrados["type"] == "Shot"
]

passes_filtrados = eventos_filtrados[
    eventos_filtrados["type"] == "Pass"
]

tab_chutes, tab_passes, tab_analises, tab_eventos = st.tabs(
    [
        "⚽ Chutes",
        "↗️ Passes",
        "📊 Análises",
        "📋 Eventos"
    ]
)

with tab_chutes:

    if not chutes_filtrados.empty:

        fig_chutes = mapa_chutes(chutes_filtrados)

        col_esq, col_grafico, col_dir = st.columns([2, 3, 2])

        with col_grafico:
            st.pyplot(fig_chutes, width="content")

    else:
        st.info(
            "Nenhum chute encontrado para o filtro selecionado."
        )

with tab_passes:

    if not passes_filtrados.empty:

        fig_passes = mapa_passes(passes_filtrados)

        col_esq, col_grafico, col_dir = st.columns([2, 3, 2])

        with col_grafico:
            st.pyplot(fig_passes, width="content")

    else:
        st.info(
            "Nenhum passe encontrado para o filtro selecionado."
        )

with tab_analises:

    st.subheader("Relação entre passes e finalizações")

    fig_relacao = grafico_passes_chutes(eventos)

    col_esq, col_grafico, col_dir = st.columns([1, 4, 1])

    with col_grafico:
        st.pyplot(
            fig_relacao,
            width="content"
        )

    st.caption(
        "Cada ponto representa um jogador. "
        "O eixo horizontal mostra o número de passes, "
        "o eixo vertical mostra o número de chutes "
        "e o tamanho do ponto representa a quantidade de gols."
    )

with tab_eventos:

    st.subheader("Filtros avançados de eventos")

    minuto_maximo = int(eventos["minute"].max())

    tipos_eventos = sorted(
        eventos_filtrados["type"]
        .dropna()
        .unique()
    )

    with st.form("form_eventos"):

        intervalo_tempo = st.slider(
            "Intervalo da partida (minutos)",
            min_value=0,
            max_value=minuto_maximo,
            value=(0, minuto_maximo)
        )

        tipo_evento = st.selectbox(
            "Tipo de evento",
            ["Todos"] + tipos_eventos
        )

        busca = st.text_input(
            "Buscar jogador, equipe ou evento",
            placeholder="Ex.: Pass, Arsenal, Henry..."
        )

        somente_com_jogador = st.checkbox(
            "Mostrar somente eventos associados a jogadores"
        )

        ordenacao = st.radio(
            "Ordenação",
            ["Mais antigos primeiro", "Mais recentes primeiro"],
            horizontal=True
        )

        quantidade = st.number_input(
            "Quantidade máxima de eventos",
            min_value=10,
            max_value=500,
            value=100,
            step=10
        )

        st.form_submit_button("Aplicar filtros")

    # Criar cópia dos eventos selecionados anteriormente
    eventos_exibicao = eventos_filtrados.copy()

    # Filtro por intervalo de tempo
    eventos_exibicao = eventos_exibicao[
        eventos_exibicao["minute"].between(
            intervalo_tempo[0],
            intervalo_tempo[1]
        )
    ]

    # Filtro por tipo de evento
    if tipo_evento != "Todos":
        eventos_exibicao = eventos_exibicao[
            eventos_exibicao["type"] == tipo_evento
        ]

    # Mostrar somente eventos com jogador
    if somente_com_jogador:
        eventos_exibicao = eventos_exibicao[
            eventos_exibicao["player"].notna()
        ]

    # Busca por texto
    if busca:

        busca = busca.lower()

        filtro_busca = (
            eventos_exibicao["player"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.contains(busca)
            |
            eventos_exibicao["team"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.contains(busca)
            |
            eventos_exibicao["type"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.contains(busca)
        )

        eventos_exibicao = eventos_exibicao[
            filtro_busca
        ]

    # Ordenação
    if ordenacao == "Mais recentes primeiro":

        eventos_exibicao = eventos_exibicao.sort_values(
            ["minute", "second"],
            ascending=False
        )

    else:

        eventos_exibicao = eventos_exibicao.sort_values(
            ["minute", "second"],
            ascending=True
        )

    # Limitar quantidade de eventos exibidos
    eventos_exibicao = eventos_exibicao.head(
        int(quantidade)
    )

    # Colunas exibidas na tabela
    colunas_eventos = [
        "minute",
        "second",
        "team",
        "player",
        "type"
    ]

    tabela_eventos = eventos_exibicao[
        colunas_eventos
    ]

    st.write(
        f"Eventos encontrados: {len(eventos_exibicao)}"
    )

    st.dataframe(
        tabela_eventos,
        use_container_width=True
    )

    # Download em CSV
    csv = tabela_eventos.to_csv(
        index=False
    ).encode("utf-8")

    nome_arquivo = (
        partida_escolhida
        .replace(" ", "_")
        .replace("/", "-")
    )

    st.download_button(
        label="⬇️ Baixar eventos filtrados em CSV",
        data=csv,
        file_name=f"{nome_arquivo}_eventos.csv",
        mime="text/csv"
    )

    