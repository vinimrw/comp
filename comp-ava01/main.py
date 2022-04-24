from lexica import AnalisadorLexico
from sintatica import AnalisadorSintatico


analisador_lexico = AnalisadorLexico()
analisador_lexico.analisa()

sintatico = AnalisadorSintatico()
sintatico.syntax()