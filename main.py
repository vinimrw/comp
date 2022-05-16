import traceback
from lexer.lexica import Scanner
from parser.parser import Parser
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

    try:
        lexer = Scanner(programa)

        tabelaDeTokens = lexer.scan()

        parser = Parser(tabelaDeTokens)

        print("#============================#\n")
        print("#       TABELA DE TOKENS     #\n")
        for i in tabelaDeTokens:
            print(i)
        print("#============================#\n")
    
        parser.start()
        print("#============================#\n")
        print("#     TABELA DE SÍMBOLOS     #\n")
        pprint(parser.tabelaDeSimbolos)
        print("#============================#\n")
    
        print("#============================#\n")
        print("#       CODIGO 3 END         #\n")
        for i in parser.tabelaDeTresEnderecos:
            print(i)    
        print("#============================#\n")
        print("\n           FIM...           \n")
    except Exception as e:
        print("#============================#\n")
        print("#     TABELA DE SÍMBOLOS     #\n")
        traceback.print_exc()
        print(e)
        print("#============================#\n")