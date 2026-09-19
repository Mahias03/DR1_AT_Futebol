import matplotlib.pyplot as plt
import seaborn as sns
from mplsoccer import VerticalPitch


def mapa_chutes(chutes):

    pitch = VerticalPitch(
        pitch_type="statsbomb",
        half=True,
        pitch_color="#0E1117",
        line_color="white",
        linewidth=1
    )

    fig, ax = pitch.draw(figsize=(5, 6))

    fig.set_facecolor("#0E1117")

    chutes_normais = chutes[
        chutes["shot_outcome"] != "Goal"
    ]

    gols = chutes[
        chutes["shot_outcome"] == "Goal"
    ]

    pitch.scatter(
        chutes_normais["location"].apply(lambda x: x[0]),
        chutes_normais["location"].apply(lambda x: x[1]),
        s=55,
        alpha=0.7,
        ax=ax,
        label="Chute"
    )

    pitch.scatter(
        gols["location"].apply(lambda x: x[0]),
        gols["location"].apply(lambda x: x[1]),
        s=180,
        marker="*",
        ax=ax,
        label="Gol"
    )

    ax.legend(
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=False,
        labelcolor="white"
    )

    fig.subplots_adjust(right=0.82)

    ax.set_title(
        "Mapa de chutes",
        fontsize=15,
        color="white",
        pad=10
    )

    return fig

def mapa_passes(passes):

    pitch = VerticalPitch(
        pitch_type="statsbomb",
        pitch_color="#0E1117",
        line_color="white",
        linewidth=1
    )

    fig, ax = pitch.draw(figsize=(5, 7))
    fig.set_facecolor("#0E1117")

    # Garantir que o passe possui origem e destino
    passes_validos = passes[
        passes["location"].apply(lambda x: isinstance(x, list))
        &
        passes["pass_end_location"].apply(lambda x: isinstance(x, list))
    ].copy()

    passes_completos = passes_validos[
        passes_validos["pass_outcome"].isna()
    ]

    passes_incompletos = passes_validos[
        passes_validos["pass_outcome"].notna()
    ]

    if not passes_completos.empty:

        pitch.arrows(
            passes_completos["location"].apply(lambda x: x[0]),
            passes_completos["location"].apply(lambda x: x[1]),
            passes_completos["pass_end_location"].apply(lambda x: x[0]),
            passes_completos["pass_end_location"].apply(lambda x: x[1]),
            width=1.2,
            headwidth=4,
            headlength=4,
            alpha=0.75,
            color="#4DA3FF",
            ax=ax,
            label="Passe completo"
        )

    if not passes_incompletos.empty:

        pitch.arrows(
            passes_incompletos["location"].apply(lambda x: x[0]),
            passes_incompletos["location"].apply(lambda x: x[1]),
            passes_incompletos["pass_end_location"].apply(lambda x: x[0]),
            passes_incompletos["pass_end_location"].apply(lambda x: x[1]),
            width=1.2,
            headwidth=4,
            headlength=4,
            alpha=0.8,
            color="#FF6B6B",
            ax=ax,
            label="Passe incompleto"
        )

    ax.legend(
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=False,
        labelcolor="white"
    )

    fig.subplots_adjust(right=0.78)

    ax.set_title(
        "Mapa de passes",
        fontsize=15,
        color="white",
        pad=10
    )

    return fig

def grafico_passes_chutes(eventos):

    eventos_jogadores = eventos[
        eventos["player"].notna()
    ].copy()

    passes = (
        eventos_jogadores[
            eventos_jogadores["type"] == "Pass"
        ]
        .groupby(["player", "team"])
        .size()
        .reset_index(name="passes")
    )

    chutes = (
        eventos_jogadores[
            eventos_jogadores["type"] == "Shot"
        ]
        .groupby(["player", "team"])
        .size()
        .reset_index(name="chutes")
    )

    gols = (
        eventos_jogadores[
            (eventos_jogadores["type"] == "Shot")
            &
            (eventos_jogadores["shot_outcome"] == "Goal")
        ]
        .groupby(["player", "team"])
        .size()
        .reset_index(name="gols")
    )

    estatisticas = passes.merge(
        chutes,
        on=["player", "team"],
        how="outer"
    )

    estatisticas = estatisticas.merge(
        gols,
        on=["player", "team"],
        how="outer"
    )

    estatisticas[
        ["passes", "chutes", "gols"]
    ] = estatisticas[
        ["passes", "chutes", "gols"]
    ].fillna(0)

    fig, ax = plt.subplots(figsize=(7, 4))

    sns.scatterplot(
        data=estatisticas,
        x="passes",
        y="chutes",
        hue="team",
        size="gols",
        sizes=(60, 300),
        alpha=0.8,
        ax=ax
    )

    ax.legend(
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        borderaxespad=0
    )

    fig.tight_layout()

    ax.set_title(
        "Relação entre passes e chutes por jogador"
    )

    ax.set_xlabel("Quantidade de passes")
    ax.set_ylabel("Quantidade de chutes")

    ax.grid(
        alpha=0.2
    )

    return fig