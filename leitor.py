"""Leitura de CSVs de gastos e soma por mês.

Cada banco exports CSV com nomes de coluna diferentes, por isso este módulo
tenta descobrir sozinho qual coluna é a data e qual é o valor. Se não conseguir,
ele levanta um erro explicando o que esperava.
"""

import csv
import os
import re
from collections import defaultdict

NOMES_DATA = [
    "data", "date", "datamovimentacao", "data_movimentacao", "data movimentacao",
    "dtmovimento", "data lancamento", "data_lancamento", "data transacao",
    "data_transacao", "posted", "movementdate",
]

NOMES_VALOR = [
    "valor", "value", "amount", "montante", "quantia", "vl lancamento",
    "valor_lancamento", "vlr", "debito", "debit", "credito", "credit",
]

MESES = [
    "jan", "fev", "mar", "abr", "mai", "jun",
    "jul", "ago", "set", "out", "nov", "dez",
]


class ColunaNaoEncontrada(Exception):
    """Nao achou nenhuma coluna que pareca data ou valor."""


def _normalizar(nome):
    """'Data de Movimentacao' -> 'datademovimentacao'"""
    return re.sub(r"[^a-z0-9]", "", nome.lower())


def _achar_coluna(cabecalho, nomes):
    """Retorna o indice da primeira coluna cujo nome normalizado bate com a lista."""
    normalizados = [_normalizar(c) for c in cabecalho]
    for nome in nomes:
        alvo = _normalizar(nome)
        for i, col in enumerate(normalizados):
            if col == alvo or col.startswith(alvo):
                return i
    return None


def _parse_data(texto):
    """Converte '2026-01-15', '15/01/2026', '15-01-26' em (ano, mes)."""
    texto = texto.strip()

    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", texto)
    if m:
        return int(m.group(1)), int(m.group(2))

    m = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})$", texto)
    if m:
        dia, mes, ano = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if ano < 100:
            ano += 2000
        if mes > 12:  # formato dia/ano/mes, pouco comum mas acontece
            return ano, dia
        return ano, mes

    raise ValueError(f"data nao reconhecida: {texto!r}")


def _parse_valor(texto):
    """'1.234,56' -> 1234.56 ; 'R$ 1.234,56' -> 1234.56 ; 'R$ -99,90' -> -99.90"""
    texto = texto.strip()
    negativo = "-" in texto
    limpo = re.sub(r"[^\d,.]", "", texto)

    if "," in limpo:
        # vírgula é o decimal: ponto é separador de milhar
        limpo = limpo.replace(".", "").replace(",", ".")
    elif limpo.count(".") > 1 or re.search(r"\.\d{3}$", limpo):
        # '1.234' ou '1.234.567': ponto é separador de milhar
        limpo = limpo.replace(".", "")
    else:
        limpo = limpo.replace(",", ".")

    valor = float(limpo)
    return -valor if negativo else valor


def _detectar_separador(amostra):
    """Bancos brasileiros costumam exportar CSV com ';', outros com ','.

    Desempata pelo separador que aparece mais vezes na primeira linha.
    """
    return ";" if amostra.count(";") > amostra.count(",") else ","


def _totais_do_arquivo(caminho):
    """Le um CSV e devolve {(ano, mes): soma}."""
    with open(caminho, newline="", encoding="utf-8-sig") as arquivo:
        amostra = arquivo.readline()
        arquivo.seek(0)
        separador = _detectar_separador(amostra)
        try:
            cabecalho = next(csv.reader([amostra], delimiter=separador))
        except (StopIteration, csv.Error):
            return {}

        idx_data = _achar_coluna(cabecalho, NOMES_DATA)
        idx_valor = _achar_coluna(cabecalho, NOMES_VALOR)

        if idx_data is None or idx_valor is None:
            raise ColunaNaoEncontrada(
                f"{os.path.basename(caminho)}: colunas encontradas "
                f"{[c.strip() for c in cabecalho]}. "
                "Esperava uma coluna de data e uma de valor."
            )

        totais = defaultdict(float)
        for linha in csv.reader(arquivo, delimiter=separador):
            if len(linha) <= max(idx_data, idx_valor):
                continue
            try:
                ano, mes = _parse_data(linha[idx_data])
                valor = _parse_valor(linha[idx_valor])
            except (ValueError, IndexError):
                continue  # linha suja ou em outro formato: pula
            if mes < 1 or mes > 12:
                continue
            totais[(ano, mes)] += valor

        return dict(totais)


def somar_por_mes(pasta="."):
    """Le todos os .csv da pasta e devolve {(ano, mes): total}."""
    totais = defaultdict(float)
    arquivos = 0

    for nome in sorted(os.listdir(pasta)):
        if not nome.lower().endswith(".csv"):
            continue
        for chave, valor in _totais_do_arquivo(os.path.join(pasta, nome)).items():
            totais[chave] += valor
        arquivos += 1

    if arquivos == 0:
        raise FileNotFoundError(f"nenhum arquivo .csv encontrado em {pasta!r}")

    return dict(totais)


def rotular(chave):
    """(2026, 1) -> 'jan/2026'"""
    ano, mes = chave
    return f"{MESES[mes - 1]}/{ano}"