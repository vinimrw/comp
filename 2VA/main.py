from lexer.scanner import Scanner
from parser.sintatico import Parser
from pprint import pprint

import sys

if __name__ == "__main__":
    caminho = "programa.txt"

    try:
        arquivo = open(caminho, "r")
        programa = "".join(arquivo.readlines())
        arquivo.close()
    except Exception:
        print("Error: caminho não informado")
        sys.exit(1)

    lexer = Scanner(programa)
    tabelaDeTokens = lexer.scan()

    parser = Parser(tabelaDeTokens)

    try:
        parser.start()
        print("\nTABELA DE SÍMBOLOS:")
        pprint(parser.tabelaDeSimbolos)
    except Exception as e:
        print(e)

else:
    print("me executou como um módulo")
