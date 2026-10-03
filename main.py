"""Ponto de entrada: le os CSVs da pasta e gera o grafico de gastos por mes.

Uso:
    python main.py                  # le os CSVs da pasta atual
    python main.py caminho/da/pasta  # le os CSVs de outra pasta
"""

import sys

from graficos import gerar_grafico
from leitor import ColunaNaoEncontrada, rotular, somar_por_mes


def main(pasta="."):
    try:
        import matplotlib  # noqa: F401
    except ImportError:
        print("Falta a biblioteca matplotlib. Rode: pip install -r requirements.txt")
        return 1

    try:
        totais = somar_por_mes(pasta)
    except FileNotFoundError as erro:
        print(f"Erro: {erro}")
        return 1
    except ColunaNaoEncontrada as erro:
        print(f"Erro: {erro}")
        return 1

    if not totais:
        print("Nenhum lancamento valido encontrado nos CSVs.")
        return 1

    for chave in sorted(totais):
        print(f"  {rotular(chave)}: R$ {totais[chave]:.2f}")

    saida = gerar_grafico(totais)
    print(f"\nGrafico salvo em: {saida}")
    return 0


if __name__ == "__main__":
    pasta = sys.argv[1] if len(sys.argv) > 1 else "."
    sys.exit(main(pasta))