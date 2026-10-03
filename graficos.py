"""Geracao do grafico de barras de gastos por mes."""

import matplotlib

matplotlib.use("Agg")  # salva em arquivo em vez de abrir janela (funciona em servidor)

import matplotlib.pyplot as plt


def gerar_grafico(totais, saida="gastos.png", titulo="Gastos por mes"):
    """Desenha os totais em barras, uma por mes, e salva em `saida`.

    `totais` e um dicionario {(ano, mes): valor}.
    """
    from leitor import rotular

    chaves = sorted(totais)
    rotulos = [rotular(c) for c in chaves]
    valores = [totais[c] for c in chaves]

    figura, eixo = plt.subplots(figsize=(10, 5.5))

    barras = eixo.bar(rotulos, valores, color="#3b7dd8")
    eixo.bar_label(barras, fmt="R$ %.2f", padding=3, fontsize=9)

    eixo.set_title(titulo)
    eixo.set_ylabel("Total gasto")
    eixo.grid(axis="y", alpha=0.3)
    eixo.set_axisbelow(True)
    eixo.margins(y=0.15)

    figura.tight_layout()
    figura.savefig(saida, dpi=140)
    plt.close(figura)

    return saida
