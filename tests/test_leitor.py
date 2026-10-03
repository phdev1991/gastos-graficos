"""Testes do leitor: o bug mora aqui, nao no grafico."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from leitor import (  # noqa: E402
    ColunaNaoEncontrada,
    _achar_coluna,
    _parse_data,
    _parse_valor,
    rotular,
    somar_por_mes,
)


class TestParseData(unittest.TestCase):
    def test_iso(self):
        self.assertEqual(_parse_data("2026-01-15"), (2026, 1))

    def test_br(self):
        self.assertEqual(_parse_data("15/01/2026"), (2026, 1))

    def test_ano_curto(self):
        self.assertEqual(_parse_data("15-01-26"), (2026, 1))

    def test_com_horas(self):
        self.assertEqual(_parse_data("2026-01-15 14:30:00"), (2026, 1))

    def test_invalida(self):
        with self.assertRaises(ValueError):
            _parse_data("ontem")


class TestParseValor(unittest.TestCase):
    def test_ponto_decimal(self):
        self.assertEqual(_parse_valor("1234.56"), 1234.56)

    def test_virgula_decimal(self):
        self.assertEqual(_parse_valor("1.234,56"), 1234.56)

    def test_com_simbolo(self):
        self.assertEqual(_parse_valor("R$ 1.234,56"), 1234.56)

    def test_negativo(self):
        self.assertEqual(_parse_valor("-99,90"), -99.90)

    def test_inteiro(self):
        self.assertEqual(_parse_valor("100"), 100.0)


class TestAcharColuna(unittest.TestCase):
    def test_exato(self):
        self.assertEqual(_achar_coluna(["id", "data", "valor"], ["data"]), 1)

    def test_variacao_minusculas(self):
        self.assertEqual(_achar_coluna(["Data", "Valor"], ["data", "valor"]), 0)

    def test_prefixo(self):
        self.assertEqual(
            _achar_coluna(["Data de Movimentacao", "Valor Lancamento"], ["data", "valor"]),
            0,
        )

    def test_ausente(self):
        self.assertIsNone(_achar_coluna(["a", "b"], ["data"]))


class TestSomarPorMes(unittest.TestCase):
    def _csv(self, pasta, nome, conteudo):
        caminho = os.path.join(pasta, nome)
        with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
            arquivo.write(conteudo)
        return caminho

    def test_soma_e_agrupa(self):
        with tempfile.TemporaryDirectory() as pasta:
            self._csv(
                pasta,
                "a.csv",
                'Data,Valor\n2026-01-10,"100,00"\n2026-02-05,"50,50"\n2026-01-20,"25,00"\n',
            )
            totais = somar_por_mes(pasta)

        self.assertEqual(totais[(2026, 1)], 125.0)
        self.assertEqual(totais[(2026, 2)], 50.5)

    def test_soma_entre_arquivos(self):
        with tempfile.TemporaryDirectory() as pasta:
            self._csv(pasta, "a.csv", "Data;Valor\n2026-01-10;100,00\n")
            self._csv(pasta, "b.csv", "date;amount\n15/01/2026;25,00\n")
            totais = somar_por_mes(pasta)

        self.assertEqual(totais[(2026, 1)], 125.0)

    def test_ignora_linhas_sujas(self):
        with tempfile.TemporaryDirectory() as pasta:
            self._csv(
                pasta,
                "a.csv",
                "Data,Valor\n2026-01-10,10,00\ndata invalida,5,00\n2026-01-15,abc\n2026-02-01,7,00\n",
            )
            totais = somar_por_mes(pasta)

        self.assertEqual(totais[(2026, 1)], 10.0)
        self.assertEqual(totais[(2026, 2)], 7.0)

    def test_pasta_sem_csv(self):
        with tempfile.TemporaryDirectory() as pasta:
            with self.assertRaises(FileNotFoundError):
                somar_por_mes(pasta)

    def test_coluna_desconhecida(self):
        with tempfile.TemporaryDirectory() as pasta:
            self._csv(pasta, "a.csv", "coluna1,coluna2\nx,y\n")
            with self.assertRaises(ColunaNaoEncontrada):
                somar_por_mes(pasta)


class TestRotular(unittest.TestCase):
    def test_rotulo(self):
        self.assertEqual(rotular((2026, 3)), "mar/2026")


if __name__ == "__main__":
    unittest.main()
