from pprint import pprint

def arvoreExpressao(lista):
    if(lista == None or len(lista) == 0):
        return []
    else:
        listaPrimeiro = lista[0]
        if (len(lista) == 1):
            return [listaPrimeiro]

        listaSegundo = lista[1]
        listaTerceiro = arvoreExpressao(lista[2:])
        return ([listaPrimeiro] + [listaSegundo] + [listaTerceiro])

class Parser:
    def __init__(self, tabelaDeTokens):
        self.tabelaDeTokens = tabelaDeTokens
        self.indexDaTabelaDeTokens = 0
        self.indexLookAhead = 0
        self.indexEscopoAtual = -1
        self.tabelaDeSimbolos = []
        self.indexDaDeclaracaoDaVariavelAtual = -1
        self.indexEscopoAntesDaFuncao = 0
        self.tabelaDeTresEnderecos = []
        self.tempTresEnderecos = ''

    def tokenAtual(self):
        return self.tabelaDeTokens[self.indexDaTabelaDeTokens]

    def tokenLookAhead(self):
        self.indexLookAhead = self.indexDaTabelaDeTokens + 1
        return self.tabelaDeTokens[self.indexLookAhead]

    def start(self):
        escopoPai = self.indexEscopoAtual  
        self.indexEscopoAtual += 1
        self.statement_list()  
        return

    def statement_list(self):
        if self.tokenAtual().tipo == "END":
            return
        else:
            self.statement()
            self.statement_list()
            return

    def statement(self):
        if self.tokenAtual().tipo == "PROGRAM":
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "CLEFT":
                self.indexDaTabelaDeTokens += 1

                while self.tokenAtual().tipo != "CRIGHT":
                    self.block_statement()

                if self.tokenAtual().tipo == "CRIGHT":
                    self.indexDaTabelaDeTokens += 1

                    if self.tokenAtual().tipo == "END":
                        print("\nFIM DA ANÁLISE SINTÁTICA\n")
                        # Deu certo
                    else:
                        raise Exception(
                            "Erro sintatico: falta do END na linha "
                            + str(self.tokenAtual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sintatico: falta do CRIGHT na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do CLEFT na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: Código fora do padrão na linha "
                + str(self.tokenAtual().linha)
            )

    def block_statement(self):

        if self.tokenAtual().tipo == "INT" or self.tokenAtual().tipo == "BOOL":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.declaration_var_statement(temp)
            return temp

        if self.tokenAtual().tipo == "IF":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.if_statement(temp)
            return temp

        if self.tokenAtual().tipo == "ID":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            temp.append(self.tokenAtual().lexema)
            self.call_var_statement(temp)
            return temp

        else:
            return


    def declaration_var_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "ID":
            temp.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "ATB":  
                temp.append(self.tokenAtual().lexema)
                self.indexDaTabelaDeTokens += 1
                tempEndVar = []

                self.end_var_statement(tempEndVar)
                temp.append(tempEndVar)

                if self.tokenAtual().tipo == "SEMICOLON":
                    self.indexDaTabelaDeTokens += 1
                    self.tabelaDeSimbolos.append(temp)
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta da atribuição na linha "
                    + str(self.tokenAtual().linha)
                )


        else:
            raise Exception(
                "Erro sintatico: falta do ID na linha " +
                str(self.tokenAtual().linha)
            )

    def end_var_statement(self, tempEndVar):
    
        if self.tokenAtual().tipo == "CALL":
            tempEndVar.append(self.tokenAtual().tipo)
            self.indexDaTabelaDeTokens += 1
    
            if self.tokenAtual().tipo == "FUNC":
                tempEndVar.append(self.tokenAtual().tipo)
                self.call_func_statement(tempEndVar)
                return
            else:
                raise Exception(
                    "Erro sintatico: chamada de função erroneamente na linha "
                    + str(self.tokenAtual().linha)
                )

        if self.tokenAtual().tipo == "BOOLEAN":

            if (
                self.tokenAtual().lexema == "True"
                or self.tokenAtual().lexema == "False"
            ):
                tempEndVar.append(self.tokenAtual().lexema)
                self.indexDaTabelaDeTokens += 1
                return
            else:
                raise Exception(
                    "Erro sintatico: boolean atribuido erroneamente na linha "
                    + str(self.tokenAtual().linha)
                )

        if self.tokenAtual().tipo == "NUM":
            tempEndVar.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                self.tokenAtual().tipo == "ADD"
                or self.tokenAtual().tipo == "SUB"
                or self.tokenAtual().tipo == "MULT"
                or self.tokenAtual().tipo == "DIV"
            ):
                tempEndVar.append(self.tokenAtual().lexema)
                self.call_op_statement(tempEndVar)
                return
            else:
                return

        if self.tokenAtual().tipo == "ID":
            tempEndVar.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1

            if (
                self.tokenAtual().tipo == "ADD"
                or self.tokenAtual().tipo == "SUB"
                or self.tokenAtual().tipo == "MULT"
                or self.tokenAtual().tipo == "DIV"
            ):
                tempEndVar.append(self.tokenAtual().lexema)
                self.call_op_statement(tempEndVar)
                return
            else:
                return
        else:
            raise Exception(
                "Erro sintatico: atribuição de variavel erroneamente na linha "
                + str(self.tokenAtual().linha)
            )


    def call_var_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "ATB":  # atribuicao
            temp.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                (self.tokenAtual().tipo == "NUM")
                or (self.tokenAtual().tipo == "BOOLEAN")
                or (self.tokenAtual().tipo == "ID")
            ):
                temp.append(self.tokenAtual().lexema)
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "SEMICOLON":
                    self.indexDaTabelaDeTokens += 1
                    self.tabelaDeSimbolos.append(temp)
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e vírgula na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: variável não atribuída na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: símbolo de atribuição não encontrado na linha "
                + str(self.tokenAtual().linha)
            )

    def call_op_statement(self, tempEndVar):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "ID" or self.tokenAtual().tipo == "NUM":
            tempEndVar.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                self.tokenAtual().tipo == "ADD"
                or self.tokenAtual().tipo == "SUB"
                or self.tokenAtual().tipo == "MULT"
                or self.tokenAtual().tipo == "DIV"
            ):
                tempEndVar.append(self.tokenAtual().lexema)
                self.call_op_statement(tempEndVar)

            else:
                return
        else:
            raise Exception(
                "Erro sintatico: falta do ID na linha " +
                str(self.tokenAtual().linha)
            )

    def if_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "PLEFT":
            self.indexDaTabelaDeTokens += 1
            tempExpression = []
            # Expression
            tempExpression = self.expression_statement(tempExpression)
            temp.append(tempExpression)

            if self.tokenAtual().tipo == "PRIGHT":
                olhaAfrente = self.tokenLookAhead()
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "CLEFT" and olhaAfrente.tipo != "CRIGHT":
                    self.indexDaTabelaDeTokens += 1
                    self.indexEscopoAtual += 1
                    tempBlock = []
                    while (
                        self.tokenAtual().tipo != "CRIGHT"
                        and self.tokenLookAhead().tipo != "ENDIF"
                    ):
                        tempBlock.append(self.block3_statement())

                    temp.append(tempBlock)
                    if self.tokenAtual().tipo == "CRIGHT":
                        self.indexDaTabelaDeTokens += 1
                        if self.tokenAtual().tipo == "ENDIF":
                            temp.append(self.tokenAtual().tipo)
                            self.indexDaTabelaDeTokens += 1

                            tempElse = []
                            if self.tokenAtual().tipo == "ELSE":
                                tempElse.append(self.indexEscopoAtual)
                                tempElse.append(self.tokenAtual().tipo)
                                tempElse = self.else_part_statement(
                                    tempElse)  # ELSE

                                temp.append(tempElse)
                                self.tabelaDeSimbolos.append(temp)
                                self.indexEscopoAtual -= 1
                            else:
                                temp.append(tempElse)
                                self.tabelaDeSimbolos.append(temp)
                                self.indexEscopoAtual -= 1
                                return
                        else:
                            raise Exception(
                                "Erro sintatico: falta de ENDIF "
                                + str(self.tokenAtual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sintatico: falta do CRIGHT na linha "
                            + str(self.tokenAtual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sintatico: falta do CLEFT ou bloco vazio na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do Parentese direito na linha  "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do Parentese esquerdo na linha  "
                + str(self.tokenAtual().linha)
            )

    def else_part_statement(self, tempElse):
        olhaAfrente = self.tokenLookAhead()
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "CLEFT" and olhaAfrente.tipo != "CRIGHT":
            self.indexDaTabelaDeTokens += 1
            tempBlock = []
            while (
                self.tokenAtual().tipo != "CRIGHT"
                and self.tokenLookAhead().tipo != "ENDELSE"
            ):

                tempBlock.append(self.block3_statement())
            tempElse.append(tempBlock)
            if self.tokenAtual().tipo == "CRIGHT":
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "ENDELSE":
                    tempElse.append(self.tokenAtual().tipo)
                    self.indexDaTabelaDeTokens += 1
                    return tempElse
                else:
                    raise Exception(
                        "Erro sintatico: falta de ENDELSE na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do CRIGHT na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do CLEFT ou bloco vazio na linha "
                + str(self.tokenAtual().linha)
            )


    def expression_statement(self, tempExpression):
        if self.tokenAtual().tipo == "ID" or self.tokenAtual().tipo == "NUM":
            tempExpression.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                self.tokenAtual().tipo == "EQUAL"
                or self.tokenAtual().tipo == "DIFF"
                or self.tokenAtual().tipo == "LESSEQUAL"
                or self.tokenAtual().tipo == "LESS"
                or self.tokenAtual().tipo == "GREATEREQUAL"
                or self.tokenAtual().tipo == "GREATER"
            ):
                tempExpression.append(self.tokenAtual().lexema)
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "ID" or self.tokenAtual().tipo == "NUM":
                    tempExpression.append(self.tokenAtual().lexema)
                    self.indexDaTabelaDeTokens += 1
                    return tempExpression
                else:
                    raise Exception(
                        "Erro sintatico: falta do ID na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do operador booleano na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do ID na linha " +
                str(self.tokenAtual().linha)
            )

    def block3_statement(self):

        if self.tokenAtual().tipo == "INT" or self.tokenAtual().tipo == "BOOL":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.declaration_var_statement(temp)
            return temp

        if self.tokenAtual().tipo == "IF":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.if_statement(temp)
            return temp

        if self.tokenAtual().tipo == "ELSE":
            raise Exception(
                "Erro sintatico: ELSE adicionado de maneira incorreta "
                + str(self.tokenAtual().linha)
            )

        if self.tokenAtual().tipo == "ID":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            temp.append(self.tokenAtual().lexema)
            self.call_var_statement(temp)
            return temp

        else:
            raise Exception(
                "Erro sintatico: bloco vazio na linha " +
                str(self.tokenAtual().linha)
            )





