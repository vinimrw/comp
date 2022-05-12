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


def expressaoTresEnderecos(lista):
    listaTresEnd = []

    if(lista == None or len(lista) == 0):
        return listaTresEnd

    primeiraVariavel = lista[0]
    if (len(lista) == 1):
        listaTresEnd.append(('mov', 'temp', primeiraVariavel))

    else:
        operacao = lista[1]
        resto = expressaoTresEnderecos(lista[2])
        listaTresEnd.extend(resto)

        if(operacao == "+"):
            listaTresEnd.append(('token101_+', 'temp', primeiraVariavel))

        if(operacao == "*"):
            listaTresEnd.append(('mul', 'temp', primeiraVariavel))

    return listaTresEnd




























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

        #for linha in self.tabelaDeTresEnderecos:
        #    pprint(linha)
        #print('\n')

        self.checkSemantica()
        return

    def statement_list(self):
        if self.tokenAtual().tipo == "token601_end":
            return
        else:
            self.statement()
            self.statement_list()
            return

    def statement(self):
        if self.tokenAtual().tipo == "token600_main":
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "token204_{":
                self.indexDaTabelaDeTokens += 1

                while self.tokenAtual().tipo != "token205_}":
                    self.block_statement()

                if self.tokenAtual().tipo == "token205_}":
                    self.indexDaTabelaDeTokens += 1

                    if self.tokenAtual().tipo == "token601_end":
                        print("#============================#\n")
                        print("#  FIM DA ANÁLISE SINTÁTICA  #\n")
                        print("#  FINALIZADO SEM PROBLEMAS  #\n")
                        print("#============================#\n")                        
                    else:
                        raise Exception(
                            "Erro sintatico: falta do token601_end na linha "
                            + str(self.tokenAtual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sintatico: falta do token205_} na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do token204_{ na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: Código fora do padrão na linha "
                + str(self.tokenAtual().linha)
            )

    def block_statement(self):
        if self.tokenAtual().tipo == "token609_int" or self.tokenAtual().tipo == "token610_bool":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.declaration_var_statement(temp)
            return temp

        if self.tokenAtual().tipo == "token602_func":

            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)

            self.declaration_func_statement(temp)
            return temp


        if self.tokenAtual().tipo == "token615_proc":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            temp = self.declaration_proc_statement(temp)
            self.tabelaDeSimbolos.append(temp)

            nomeDaFuncao = temp[3]
            paramsDaFuncao = temp[4]

            self.tabelaDeTresEnderecos.append(('label', nomeDaFuncao, 'null'))

            for param in paramsDaFuncao:
                self.tabelaDeTresEnderecos.append(('pop', param[2], 'null'))

            self.tabelaDeTresEnderecos.append(('ret', 'null', 'null'))

            return temp

        if self.tokenAtual().tipo == "token604_call":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.indexDaTabelaDeTokens += 1

            if self.tokenAtual().tipo == "token602_func":
                temp.append(self.tokenAtual().tipo)
                temp = self.call_func_statement(temp)
                if self.tokenAtual().tipo == "token200_;":
                    self.indexDaTabelaDeTokens += 1
                    self.tabelaDeSimbolos.append(temp)
                    return temp
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.tokenAtual().linha)
                    )

            elif self.tokenAtual().tipo == "token615_proc":
                temp.append(self.tokenAtual().tipo)
                temp = self.call_proc_statement(temp)
        
                if self.tokenAtual().tipo == "token200_;":
                    self.indexDaTabelaDeTokens += 1
                    self.tabelaDeSimbolos.append(temp)
                    return temp
                else:
                    raise Exception(
                        "aErro sintatico: falta do ponto e virgula na linha "
                        + str(self.tokenAtual().linha)
                    )

            else:
                raise Exception(
                    "Erro sintatico: falta de token615_proc ou token602_func"
                    + str(self.tokenAtual().linha)
                )


        if self.tokenAtual().tipo == "token608_print":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.print_statement(temp)
            return temp


        if self.tokenAtual().tipo == "token605_if":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.if_statement(temp)
            return temp


        if self.tokenAtual().tipo == "token607_while":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.while_statement(temp)
            return temp


        if self.tokenAtual().tipo == "token500_Id":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            temp.append(self.tokenAtual().lexema)
            self.call_var_statement(temp)
            return temp

        else:
            return

    # block2 é o bloco que contém break/continue que só pode ser chamado dentro de um while
    def block2_statement(self):

        if self.tokenAtual().tipo == "token609_int" or self.tokenAtual().tipo == "token610_bool":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.declaration_var_statement(temp)
            return temp


        if self.tokenAtual().tipo == "token604_call":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.indexDaTabelaDeTokens += 1

            if self.tokenAtual().tipo == "token602_func":
                temp.append(self.tokenAtual().tipo)
                temp = self.call_func_statement(temp)
                if self.tokenAtual().tipo == "token200_;":
                    self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return temp
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.tokenAtual().linha)
                    )

            elif self.tokenAtual().tipo == "token615_proc":
                temp.append(self.tokenAtual().tipo)
                temp = self.call_proc_statement(temp)
                if self.tokenAtual().tipo == "token200_;":
                    self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return temp
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta de token615_proc ou token602_func"
                    + str(self.tokenAtual().linha)
                )


        if self.tokenAtual().tipo == "token608_print":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.print_statement(temp)
            return temp


        if self.tokenAtual().tipo == "token605_if":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.if_statement2(temp)
            return temp


        if self.tokenAtual().tipo == "token606_else":
            raise Exception(
                "Erro sintatico: token606_else adicionado de maneira incorreta "
                + str(self.tokenAtual().linha)
            )


        if self.tokenAtual().tipo == "token607_while":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.while_statement(temp)
            return temp


        if self.tokenAtual().tipo == "token500_Id":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            temp.append(self.tokenAtual().lexema)
            self.call_var_statement(temp)
            return temp

 
        if self.tokenAtual().tipo == "token613_break" or self.tokenAtual().tipo == "token614_cont":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.unconditional_branch_statement()
            return temp

        else:
            raise Exception(
                "Erro sintatico: bloco vazio na linha " +
                str(self.tokenAtual().linha)
            )

    def block3_statement(self):

        if self.tokenAtual().tipo == "token609_int" or self.tokenAtual().tipo == "token610_bool":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.declaration_var_statement(temp)
            return temp


        if self.tokenAtual().tipo == "token604_call":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.indexDaTabelaDeTokens += 1

            if self.tokenAtual().tipo == "token602_func":
                temp.append(self.tokenAtual().tipo)
                temp = self.call_func_statement(temp)
                if self.tokenAtual().tipo == "token200_;":
                    self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return temp
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.tokenAtual().linha)
                    )

            elif self.tokenAtual().tipo == "token615_proc":
                temp.append(self.tokenAtual().tipo)
                temp = self.call_proc_statement(temp)
                if self.tokenAtual().tipo == "token200_;":
                    self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return temp
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta de token615_proc ou token602_func"
                    + str(self.tokenAtual().linha)
                )


        if self.tokenAtual().tipo == "token608_print":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.print_statement(temp)
            return temp


        if self.tokenAtual().tipo == "token605_if":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.if_statement(temp)
            return temp

        if self.tokenAtual().tipo == "token606_else":
            raise Exception(
                "Erro sintatico: token606_else adicionado de maneira incorreta "
                + str(self.tokenAtual().linha)
            )

        if self.tokenAtual().tipo == "token607_while":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.while_statement(temp)
            return temp

  
        if self.tokenAtual().tipo == "token500_Id":
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

    def declaration_var_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "token500_Id":
            temp.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "token111_=":  
                temp.append(self.tokenAtual().lexema)
                self.indexDaTabelaDeTokens += 1
                tempEndVar = []
                self.end_var_statement(tempEndVar)
                temp.append(tempEndVar)

                if self.tokenAtual().tipo == "token200_;":
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


            self.tabelaDeTresEnderecos.append(('mov', temp[3], 'temp'))
        else:
            raise Exception(
                "Erro sintatico: falta do token500_Id na linha " +
                str(self.tokenAtual().linha)
            )


    def end_var_statement(self, tempEndVar):
        if self.tokenAtual().tipo == "token604_call":
            tempEndVar.append(self.tokenAtual().tipo)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "token602_func":
                tempEndVar.append(self.tokenAtual().tipo)
                self.call_func_statement(tempEndVar)
                return
            else:
                raise Exception(
                    "Erro sintatico: chamada de função erroneamente na linha "
                    + str(self.tokenAtual().linha)
                )

        if self.tokenAtual().tipo == "token611_boolValue":

            if (
                self.tokenAtual().lexema == "True"
                or self.tokenAtual().lexema == "False"
            ):
                tempEndVar.append(self.tokenAtual().lexema)
                self.indexDaTabelaDeTokens += 1
                return
            else:
                raise Exception(
                    "Erro sintatico: token611_boolValue atribuido erroneamente na linha "
                    + str(self.tokenAtual().linha)
                )
        if self.tokenAtual().tipo == "token300_Num":
            tempEndVar.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                self.tokenAtual().tipo == "token101_+"
                or self.tokenAtual().tipo == "token102_-"
                or self.tokenAtual().tipo == "token103_*"
                or self.tokenAtual().tipo == "token104_/"
            ):
                tempEndVar.append(self.tokenAtual().lexema)
                self.call_op_statement(tempEndVar)
                return
            else:
                return

        if self.tokenAtual().tipo == "token500_Id":
            tempEndVar.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                self.tokenAtual().tipo == "token101_+"
                or self.tokenAtual().tipo == "token102_-"
                or self.tokenAtual().tipo == "token103_*"
                or self.tokenAtual().tipo == "token104_/"
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
        if self.tokenAtual().tipo == "token111_=":  
            temp.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                (self.tokenAtual().tipo == "token300_Num")
                or (self.tokenAtual().tipo == "token611_boolValue")
                or (self.tokenAtual().tipo == "token500_Id")
            ):
                temp.append(self.tokenAtual().lexema)
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "token200_;":
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


    def declaration_func_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "token609_int" or self.tokenAtual().tipo == "token610_bool":  
            temp.append(self.tokenAtual().tipo)
            self.indexDaTabelaDeTokens += 1
  
            if self.tokenAtual().tipo == "token500_Id":
        
                temp.append(self.tokenAtual().lexema)
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "token202_(":

                    tempParenteses = []
                    self.indexDaTabelaDeTokens += 1
                    if (
                        self.tokenAtual().tipo == "token609_int"
                        or self.tokenAtual().tipo == "token610_bool"
                    ):
                        tempParentesesParamAtual = []

                        tempParentesesParamAtual.append(
                            self.indexEscopoAtual + 1)

  
                        tempParentesesParamAtual.append(self.tokenAtual().tipo)

                        self.indexDaTabelaDeTokens += 1
                        if self.tokenAtual().tipo == "token500_Id":
                   
                            tempParentesesParamAtual.append(
                                self.tokenAtual().lexema)
        
                            tempParenteses.append(tempParentesesParamAtual)
                 
                            self.indexDaTabelaDeTokens += 1
                            if self.tokenAtual().tipo == "token201_,":
                    
                                tempParenteses.append(
                                    self.params_statement(tempParenteses)
                                )
                                tempParenteses.pop()  
                                temp.append(tempParenteses)
                                if self.tokenAtual().tipo == "token203_)":
                                    self.indexDaTabelaDeTokens += 1

             
                                    nomeDaFuncao = temp[4]
                                    paramsDaFuncao = temp[5]

                                    self.tabelaDeTresEnderecos.append(
                                        ('label', nomeDaFuncao, 'null'))

                                    for param in paramsDaFuncao:
                                        self.tabelaDeTresEnderecos.append(
                                            ('pop', param[2], 'null'))

                                    if self.tokenAtual().tipo == "token204_{":
                            
                                        self.indexEscopoAntesDaFuncao = (
                                            self.indexEscopoAtual
                                        )
                                        self.indexEscopoAtual += 1
                                        self.indexDaTabelaDeTokens += 1

                                        tempBlock = []
                         
                                        while self.tokenAtual().tipo != "token603_return":
                                            tempBlock.append(
                                                self.block_statement())

                                        temp.append(tempBlock)
                                        tempReturn = []
                                        if self.tokenAtual().tipo == "token603_return":
                                            tempReturn.append(
                                                self.indexEscopoAtual)
                                            tempReturn.append(
                                                self.tokenAtual().tipo)
                         
                                            tempReturnParams = []
                                            tempReturnParams = self.return_statement(
                                                tempReturnParams
                                            )
                                            tempReturn.append(tempReturnParams)
                                            temp.append(tempReturn)
                                            if self.tokenAtual().tipo == "token205_}":
                                         
                                                self.indexEscopoAtual = (
                                                    self.indexEscopoAntesDaFuncao
                                                )
                                                self.indexDaTabelaDeTokens += 1

                                                if (
                                                    self.tokenAtual().tipo
                                                    == "token200_;"
                                                ):
                                                    self.indexDaTabelaDeTokens += 1
                                             
                                                    self.tabelaDeSimbolos.append(
                                                        temp)
                                                    self.tabelaDeTresEnderecos.append(
                                                        ('push', self.tempTresEnderecos, 'null'))
                                                    self.tabelaDeTresEnderecos.append(
                                                        ('ret', 'null', 'null'))
                                                else:
                                                    raise Exception(
                                                        "Erro sintatico: falta do ponto e vírgula na linha "
                                                        + str(self.tokenAtual().linha)
                                                    )
                                            else:
                                                raise Exception(
                                                    "Erro sintatico: falta da chave direita na linha "
                                                    + str(self.tokenAtual().linha)
                                                )
                                        else:
                                            raise Exception(
                                                "Erro sintatico: falta do retorno na linha "
                                                + str(self.tokenAtual().linha)
                                            )

                                    else:
                                        raise Exception(
                                            "Erro sintatico: falta da chave esquerda na linha "
                                            + str(self.tokenAtual().linha)
                                        )
                                else:
                                    raise Exception(
                                        "Erro sintatico: falta do parentese direito na linha "
                                        + str(self.tokenAtual().linha)
                                    )

                            elif self.tokenAtual().tipo == "token203_)":

                                temp.append(tempParenteses)
                                if self.tokenAtual().tipo == "token203_)":
                                    self.indexDaTabelaDeTokens += 1
                                    if self.tokenAtual().tipo == "token204_{":
                                        self.indexEscopoAntesDaFuncao = (
                                            self.indexEscopoAtual
                                        )
                                        self.indexEscopoAtual += 1
                                        self.indexDaTabelaDeTokens += 1
                                        tempBlock = []
                                        while self.tokenAtual().tipo != "token603_return":
                                            tempBlock.append(
                                                self.block_statement())

                                        temp.append(tempBlock)
                                        tempReturn = []
                                        if self.tokenAtual().tipo == "token603_return":
                                            tempReturn.append(
                                                self.indexEscopoAtual)
                                            tempReturn.append(
                                                self.tokenAtual().tipo)
                                            tempReturnParms = []
                                            tempReturnParms = self.return_statement(
                                                tempReturnParms
                                            )
                                            tempReturn.append(tempReturnParms)
                                            temp.append(tempReturn)
                                            if self.tokenAtual().tipo == "token205_}":
                                                self.indexEscopoAtual = (
                                                    self.indexEscopoAntesDaFuncao
                                                )
                                                self.indexDaTabelaDeTokens += 1
                                                if (
                                                    self.tokenAtual().tipo
                                                    == "token200_;"
                                                ):
                                                    self.indexDaTabelaDeTokens += 1
                                                    self.tabelaDeSimbolos.append(
                                                        temp)
                                                else:
                                                    raise Exception(
                                                        "Erro sintatico: falta do ponto e vírgula na linha "
                                                        + str(self.tokenAtual().linha)
                                                    )
                                            else:
                                                raise Exception(
                                                    "Erro sintatico: falta da chave direita na linha "
                                                    + str(self.tokenAtual().linha)
                                                )
                                        else:
                                            raise Exception(
                                                "Erro sintatico: falta do retorno na linha "
                                                + str(self.tokenAtual().linha)
                                            )
                                    else:
                                        raise Exception(
                                            "Erro sintatico: falta da chave esquerda na linha "
                                            + str(self.tokenAtual().linha)
                                        )
                                else:
                                    raise Exception(
                                        "Erro sintatico: falta do parentese direito na linha "
                                        + str(self.tokenAtual().linha)
                                    )
                            else:
                           
                                raise Exception(
                                    "Erro sintatico: falta da virgula na linha "
                                    + str(self.tokenAtual().linha)
                                )
                        else:
                            raise Exception(
                                "Erro sintatico: falta o token500_Id na linha "
                                + str(self.tokenAtual().linha)
                            )

                    else:
                        if self.tokenAtual().tipo == "token203_)":
                            temp.append(tempParenteses)
                            self.indexDaTabelaDeTokens += 1

                            exit(0)

                            nomeDaFuncao = temp[4]
                            paramsDaFuncao = temp[5]

                            self.tabelaDeTresEnderecos.append(
                                ('label', nomeDaFuncao, 'null'))

                            for param in paramsDaFuncao:
                                self.tabelaDeTresEnderecos.append(
                                    ('pop', param[2], 'null'))

                            self.tabelaDeTresEnderecos.append(
                                ('push', self.tempTresEnderecos, 'null'))
                            self.tabelaDeTresEnderecos.append(
                                ('ret', 'null', 'null'))

                            if self.tokenAtual().tipo == "token204_{":
                                self.indexEscopoAntesDaFuncao = self.indexEscopoAtual
                                self.indexEscopoAtual += 1
                                self.indexDaTabelaDeTokens += 1

                                tempBlock = []
              
                                while self.tokenAtual().tipo != "token603_return":
                                    tempBlock.append(self.block_statement())

                                temp.append(tempBlock)

                                tempReturn = []
                    
                                if self.tokenAtual().tipo == "token603_return":
                                    tempReturn.append(self.indexEscopoAtual)
                                    tempReturn.append(self.tokenAtual().tipo)
                          
                                    tempReturnParms = []
                                    tempReturnParms = self.return_statement(
                                        tempReturnParms
                                    )

                                    tempReturn.append(tempReturnParms)
                                    temp.append(tempReturn)
                                    if self.tokenAtual().tipo == "token205_}":
                                        self.indexEscopoAtual = (
                                            self.indexEscopoAntesDaFuncao
                                        )
                                        self.indexDaTabelaDeTokens += 1
                                        if self.tokenAtual().tipo == "token200_;":
                                            self.indexDaTabelaDeTokens += 1
                            
                                            self.tabelaDeSimbolos.append(temp)
                                        else:
                                            raise Exception(
                                                "Erro sintatico: falta do ponto e vírgula na linha "
                                                + str(self.tokenAtual().linha)
                                            )
                                    else:
                                        raise Exception(
                                            "Erro sintatico: falta da chave direita na linha "
                                            + str(self.tokenAtual().linha)
                                        )
                                else:
                                    raise Exception(
                                        "Erro sintatico: falta do retorno na linha "
                                        + str(self.tokenAtual().linha)
                                    )

                            else:
                                raise Exception(
                                    "Erro sintatico: falta da chave esquerda na linha "
                                    + str(self.tokenAtual().linha)
                                )
                        else:
                            raise Exception(
                                "Erro sintatico: falta do parentese direito na linha "
                                + str(self.tokenAtual().linha)
                            )
                else:
                    raise Exception(
                        "Erro sintatico: falta do parentese esquerdo na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do token500_Id na linha "
                    + str(self.tokenAtual().linha)
                )


    def return_statement(self, tempReturnParams):
        self.indexDaTabelaDeTokens += 1

  
        if self.tokenAtual().tipo == "token604_call":
            tempReturnParams.append(self.tokenAtual().tipo)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "token602_func":
                tempReturnParams.append(self.tokenAtual().tipo)
                self.call_func_statement(tempReturnParams)
                self.indexDaTabelaDeTokens += 1
                return tempReturnParams
            else:
                raise Exception(
                    "Erro sintatico: Erro de chamada, só é permitido chamada de funções na linha "
                    + str(self.tokenAtual().linha)
                )


        if (
            (self.tokenAtual().tipo == "token300_Num")
            or (self.tokenAtual().tipo == "token611_boolValue")
            or (self.tokenAtual().tipo == "token500_Id")
        ):
            tempReturnParams.append(self.tokenAtual().lexema)
     
            self.tempTresEnderecos = tempReturnParams[0]
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "token200_;":
                self.indexDaTabelaDeTokens += 1
                return tempReturnParams
            else:
                raise Exception(
                    "Erro sintatico: falta do ponto e virgula na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: Retorno errado na linha "
                + str(self.tokenAtual().linha)
            )


    def params_statement(self, tempParenteses):
    
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "token609_int" or self.tokenAtual().tipo == "token610_bool":
            tempParentesesParamAtual = []
            tempParentesesParamAtual.append(self.indexEscopoAtual + 1)
            tempParentesesParamAtual.append(self.tokenAtual().tipo)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "token500_Id":
                tempParentesesParamAtual.append(self.tokenAtual().lexema)
                tempParenteses.append(tempParentesesParamAtual)
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "token201_,":
                    self.params_statement(tempParenteses)
                elif (
                    self.tokenAtual().tipo == "token609_int" or self.tokenAtual().tipo == "token610_bool"
                ):
                    raise Exception(
                        "Erro sintatico: falta vírgula na linha "
                        + str(self.tokenAtual().linha)
                    )
                else:
                    return tempParenteses
            else:
                raise Exception(
                    "Erro sintatico: é necessário informar alguma váriavel na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: é necessário informar um tipo na linha "
                + str(self.tokenAtual().linha)
            )


    def declaration_proc_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "token500_Id":
            temp.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "token202_(":
                tempParenteses = []
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "token609_int" or self.tokenAtual().tipo == "token610_bool":
                    tempParentesesParamAtual = []
                    tempParentesesParamAtual.append(self.indexEscopoAtual + 1)
                    tempParentesesParamAtual.append(self.tokenAtual().tipo)
                    self.indexDaTabelaDeTokens += 1
                    if self.tokenAtual().tipo == "token500_Id":
                        tempParentesesParamAtual.append(
                            self.tokenAtual().lexema)
                        tempParenteses.append(tempParentesesParamAtual)
                        self.indexDaTabelaDeTokens += 1
                        if self.tokenAtual().tipo == "token201_,":
                            tempParenteses.append(
                                self.params_statement(tempParenteses))
                            tempParenteses.pop()
                            temp.append(tempParenteses)
                            if self.tokenAtual().tipo == "token203_)":
                                self.indexDaTabelaDeTokens += 1
                                if self.tokenAtual().tipo == "token204_{":

                                    self.indexEscopoAntesDaFuncao = (
                                        self.indexEscopoAtual
                                    )

                                    self.indexEscopoAtual += 1
                                    self.indexDaTabelaDeTokens += 1

                                    tempBlock = []
                  
                                    while (
                                        self.tokenAtual().tipo != "token205_}"
                                        and self.tokenLookAhead().tipo != "token200_;"
                                    ):
                                        tempBlock.append(
                                            self.block_statement())

                                    temp.append(tempBlock)

                                    if self.tokenAtual().tipo == "token205_}":
                                        self.indexEscopoAtual = (
                                            self.indexEscopoAntesDaFuncao
                                        )
                                        self.indexDaTabelaDeTokens += 1
                                        if self.tokenAtual().tipo == "token200_;":
                                            self.indexDaTabelaDeTokens += 1
                                            return temp
                                        else:
                                            raise Exception(
                                                "Erro sintatico: falta do ponto e vírgula na linha "
                                                + str(self.tokenAtual().linha)
                                            )
                                    else:
                                        raise Exception(
                                            "Erro sintatico: falta da chave direito na linha "
                                            + str(self.tokenAtual().linha)
                                        )
                                else:
                                    raise Exception(
                                        "Erro sintatico: falta da chave esquerda na linha "
                                        + str(self.tokenAtual().linha)
                                    )
                            else:
                                raise Exception(
                                    "Erro sintatico: falta do parentese direito na linha "
                                    + str(self.tokenAtual().linha)
                                )

                        elif self.tokenAtual().tipo == "token203_)":
                            temp.append(tempParenteses)
                            if self.tokenAtual().tipo == "token203_)":
                                self.indexDaTabelaDeTokens += 1
                                if self.tokenAtual().tipo == "token204_{":

                                    self.indexEscopoAntesDaFuncao = (
                                        self.indexEscopoAtual
                                    )
                                    self.indexEscopoAtual += 1
                                    self.indexDaTabelaDeTokens += 1
                                    tempBlock = []
                   
                                    while (
                                        self.tokenAtual().tipo != "token205_}"
                                        and self.tokenLookAhead().tipo != "token200_;"
                                    ):
                                        tempBlock.append(
                                            self.block_statement())

                                    temp.append(tempBlock)
                                    if self.tokenAtual().tipo == "token205_}":
                                        self.indexEscopoAtual = (
                                            self.indexEscopoAntesDaFuncao
                                        )
                                        self.indexDaTabelaDeTokens += 1
                                        if self.tokenAtual().tipo == "token200_;":
                                            self.indexDaTabelaDeTokens += 1
                                            return temp
                                        else:
                                            raise Exception(
                                                "Erro sintatico: falta do ponto e vírgula na linha "
                                                + str(self.tokenAtual().linha)
                                            )
                                    else:
                                        raise Exception(
                                            "Erro sintatico: falta da chave direito na linha "
                                            + str(self.tokenAtual().linha)
                                        )
                                else:
                                    raise Exception(
                                        "Erro sintatico: falta da chave esquerda na linha "
                                        + str(self.tokenAtual().linha)
                                    )
                            else:
                                raise Exception(
                                    "Erro sintatico: falta do parentese direito na linha "
                                    + str(self.tokenAtual().linha)
                                )
                        else:
                 
                            raise Exception(
                                "Erro sintatico: falta da virgula na linha "
                                + str(self.tokenAtual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sintatico: falta o token500_Id na linha "
                            + str(self.tokenAtual().linha)
                        )
                else:
                    if self.tokenAtual().tipo == "token203_)":
                        temp.append(tempParenteses)
                        self.indexDaTabelaDeTokens += 1
                        if self.tokenAtual().tipo == "token204_{":
                            self.indexEscopoAntesDaFuncao = self.indexEscopoAtual
                            self.indexEscopoAtual += 1
                            self.indexDaTabelaDeTokens += 1
                            tempBlock = []
                            while (
                                self.tokenAtual().tipo != "token205_}"
                                and self.tokenLookAhead().tipo != "token200_;"
                            ):
                                tempBlock.append(self.block_statement())

                            temp.append(tempBlock)
                            if self.tokenAtual().tipo == "token205_}":
                                self.indexEscopoAtual = self.indexEscopoAntesDaFuncao
                                self.indexDaTabelaDeTokens += 1
                                if self.tokenAtual().tipo == "token200_;":
                                    self.indexDaTabelaDeTokens += 1
                                    return temp
                                else:
                                    raise Exception(
                                        "Erro sintatico: falta do ponto e vírgula na linha "
                                        + str(self.tokenAtual().linha)
                                    )
                            else:
                                raise Exception(
                                    "Erro sintatico: falta da chave direito na linha "
                                    + str(self.tokenAtual().linha)
                                )

                        else:
                            raise Exception(
                                "Erro sintatico: falta da chave esquerda na linha "
                                + str(self.tokenAtual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sintatico: falta do parentese direito na linha "
                            + str(self.tokenAtual().linha)
                        )
            else:
                raise Exception(
                    "Erro sintatico: falta do parentese esquerdo na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do token500_Id na linha " +
                str(self.tokenAtual().linha)
            )


    def call_proc_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "token500_Id":
            temp.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "token202_(":
                self.indexDaTabelaDeTokens += 1
                tempParams = []
                if (
                    self.tokenAtual().tipo == "token500_Id"
                    or self.tokenAtual().lexema == "True"
                    or self.tokenAtual().lexema == "False"
                ):
                    tempParams.append(self.tokenAtual().lexema)
                    self.indexDaTabelaDeTokens += 1
                    if self.tokenAtual().tipo == "token201_,":
                        tempParams.append(
                            self.params_call_statement(tempParams))
                        tempParams.pop()
                        temp.append(tempParams)

                        if self.tokenAtual().tipo == "token203_)":
                            self.indexDaTabelaDeTokens += 1
                            temp.append(tempParams)
                            return temp

                    elif self.tokenAtual().tipo == "token203_)":
                        self.indexDaTabelaDeTokens += 1
                        temp.append(tempParams)
                        return temp
                    else:
                        raise Exception(
                            "Erro sintatico: falta da virgula na linha "
                            + str(self.tokenAtual().linha)
                        )
                else:
                    temp.append(tempParams)
                    if self.tokenAtual().tipo == "token203_)":

                        self.indexDaTabelaDeTokens += 1
                        return temp
                    else:
                        raise Exception(
                            "Erro sintatico: falta do parentese direito na linha "
                            + str(self.tokenAtual().linha)
                        )
            else:
                raise Exception(
                    "Erro sintatico: falta do parentese esquerdo na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do token500_Id na linha " +
                str(self.tokenAtual().linha)
            )


    def call_func_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "token500_Id":
            temp.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "token202_(":
                self.indexDaTabelaDeTokens += 1
                tempParams = []
                if (
                    self.tokenAtual().tipo == "token500_Id"
                    or self.tokenAtual().lexema == "True"
                    or self.tokenAtual().lexema == "False"
                ):
                    tempParams.append(self.tokenAtual().lexema)
                    self.indexDaTabelaDeTokens += 1
                    if self.tokenAtual().tipo == "token201_,":
                        tempParams.append(
                            self.params_call_statement(tempParams))
                        tempParams.pop()
                        if self.tokenAtual().tipo == "token203_)":
                            self.indexDaTabelaDeTokens += 1
                            temp.append(tempParams)
                            return temp
                        else:
                            raise Exception(
                                "Erro sintatico: falta do parentese direito na linha "
                                + str(self.tokenAtual().linha)
                            )
                    elif self.tokenAtual().tipo == "token203_)":
                        self.indexDaTabelaDeTokens += 1
                        temp.append(tempParams)
                        return temp
                    else:
                        raise Exception(
                            "Erro sintatico: falta do parentese direito na linha "
                            + str(self.tokenAtual().linha)
                        )

                else:
                    temp.append(tempParams)
                    if self.tokenAtual().tipo == "token203_)":
                        self.indexDaTabelaDeTokens += 1

                        return temp
                    else:
                        raise Exception(
                            "Erro sintatico: falta do parentese direito na linha "
                            + str(self.tokenAtual().linha)
                        )
            else:
                raise Exception(
                    "Erro sintatico: falta do parentese esquerdo na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do token500_Id na linha " +
                str(self.tokenAtual().linha)
            )

    def params_call_statement(self, tempParams):
        self.indexDaTabelaDeTokens += 1
        if (
            self.tokenAtual().tipo == "token500_Id"
            or self.tokenAtual().lexema == "True"
            or self.tokenAtual().lexema == "False"
        ):
            tempParams.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "token201_,":
                self.params_call_statement(tempParams)
            elif (
                self.tokenAtual().tipo == "token500_Id"
                or self.tokenAtual().lexema == "True"
                or self.tokenAtual().lexema == "False"
            ):
                raise Exception(
                    "Erro sintatico: falta vírgula na linha "
                    + str(self.tokenAtual().linha)
                )
            else:

                return tempParams
        else:
            raise Exception(
                "Erro sintatico: é necessário informar alguma váriavel na linha "
                + str(self.tokenAtual().linha)
            )


    def print_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "token202_(":
            tempParams = []
            temp.append(self.params_print_statement(tempParams))


            self.tabelaDeTresEnderecos.append(
                ('print', self.tempTresEnderecos, 'null'))
            if self.tokenAtual().tipo == "token203_)":
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "token200_;":
                    self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return
                else:

                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do Parentese direito na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do Parentese esquerdo na linha  "
                + str(self.tokenAtual().linha)
            )


    def params_print_statement(self, tempParams):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "token604_call":
            tempParams.append(self.tokenAtual().tipo)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "token602_func":
                tempParams.append(self.tokenAtual().tipo)
                tempParams = self.call_func_statement(tempParams)
                return tempParams
            elif self.tokenAtual().tipo == "token615_proc":
                raise Exception(
                    "Erro sintatico: Procedimento não tem retorno na linha "
                    + str(self.tokenAtual().linha)
                )
            else:
                raise Exception(
                    "Erro sintatico: chamada incorreta de função na linha "
                    + str(self.tokenAtual().linha)
                )

        elif (
            (self.tokenAtual().tipo == "token300_Num")
            or (self.tokenAtual().tipo == "token611_boolValue")
            or (self.tokenAtual().tipo == "token500_Id")
        ):
            tempParams.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                self.tokenAtual().tipo == "token101_+"
                or self.tokenAtual().tipo == "token102_-"
                or self.tokenAtual().tipo == "token103_*"
                or self.tokenAtual().tipo == "token104_/"
            ):
                tempParams.append(self.tokenAtual().lexema)
                self.call_op_statement(tempParams)
                return tempParams
            else:
                return tempParams
        else:
            raise Exception(
                "Erro sintatico: uso incorreto dos parametros na linha "
                + str(self.tokenAtual().linha)
            )


    def if_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "token202_(":
            self.indexDaTabelaDeTokens += 1
            tempExpression = []
            tempExpression = self.expression_statement(tempExpression)
            temp.append(tempExpression)

            if self.tokenAtual().tipo == "token203_)":
                olhaAfrente = self.tokenLookAhead()
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "token204_{" and olhaAfrente.tipo != "token205_}":
                    self.indexDaTabelaDeTokens += 1
                    self.indexEscopoAtual += 1
                    tempBlock = []
                    while (
                        self.tokenAtual().tipo != "token205_}"
                        and self.tokenLookAhead().tipo != "token605_endif"
                    ):
                        tempBlock.append(self.block3_statement())

                    temp.append(tempBlock)
                    if self.tokenAtual().tipo == "token205_}":
                        self.indexDaTabelaDeTokens += 1
                        if self.tokenAtual().tipo == "token605_endif":
                            temp.append(self.tokenAtual().tipo)
                            self.indexDaTabelaDeTokens += 1

                            tempElse = []
                            if self.tokenAtual().tipo == "token606_else":
                                tempElse.append(self.indexEscopoAtual)
                                tempElse.append(self.tokenAtual().tipo)
                                tempElse = self.else_part_statement(
                                    tempElse)  

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
                                "Erro sintatico: falta de token605_endif "
                                + str(self.tokenAtual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sintatico: falta do token205_} na linha "
                            + str(self.tokenAtual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sintatico: falta do token204_{ ou bloco vazio na linha "
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
        if self.tokenAtual().tipo == "token204_{" and olhaAfrente.tipo != "token205_}":
            self.indexDaTabelaDeTokens += 1
            tempBlock = []
            while (
                self.tokenAtual().tipo != "token205_}"
                and self.tokenLookAhead().tipo != "token606_endelse"
            ):
                tempBlock.append(self.block3_statement())
            tempElse.append(tempBlock)
            if self.tokenAtual().tipo == "token205_}":
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "token606_endelse":
                    tempElse.append(self.tokenAtual().tipo)
                    self.indexDaTabelaDeTokens += 1
                    return tempElse
                else:
                    raise Exception(
                        "Erro sintatico: falta de token606_endelse na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do token205_} na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do token204_{ ou bloco vazio na linha "
                + str(self.tokenAtual().linha)
            )


    def if_statement2(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "token202_(":
            self.indexDaTabelaDeTokens += 1
            tempExpression = []
            tempExpression = self.expression_statement(tempExpression)
            temp.append(tempExpression)
            if self.tokenAtual().tipo == "token203_)":
                olhaAfrente = self.tokenLookAhead()
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "token204_{" and olhaAfrente.tipo != "token205_}":
                    self.indexDaTabelaDeTokens += 1
                    self.indexEscopoAtual += 1
                    tempBlock = []
                    while (
                        self.tokenAtual().tipo != "token205_}"
                        and self.tokenLookAhead().tipo != "token605_endif"
                    ):
                        tempBlock.append(self.block2_statement())
                    temp.append(tempBlock)
                    if self.tokenAtual().tipo == "token205_}":
                        self.indexDaTabelaDeTokens += 1
                        if self.tokenAtual().tipo == "token605_endif":
                            temp.append(self.tokenAtual().tipo)
                            self.indexDaTabelaDeTokens += 1
                            tempElse = []
                            if self.tokenAtual().tipo == "token606_else":
                                tempElse.append(self.indexEscopoAtual)
                                tempElse.append(self.tokenAtual().tipo)
                                tempElse = self.else_part_statement2(
                                    tempElse)  

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
                                "Erro sintatico: falta de token605_endif "
                                + str(self.tokenAtual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sintatico: falta do token205_} na linha "
                            + str(self.tokenAtual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sintatico: falta do token204_{ ou Bloco vazio na linha "
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


    def else_part_statement2(self, tempElse):
        olhaAfrente = self.tokenLookAhead()
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "token204_{" and olhaAfrente.tipo != "token205_}":
            self.indexDaTabelaDeTokens += 1
            tempBlock = []
            while (
                self.tokenAtual().tipo != "token205_}"
                and self.tokenLookAhead().tipo != "token606_endelse"
            ):
                tempBlock.append(self.block2_statement())
            tempElse.append(tempBlock)
            if self.tokenAtual().tipo == "token205_}":
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "token606_endelse":
                    tempElse.append(self.tokenAtual().tipo)
                    self.indexDaTabelaDeTokens += 1
                    return tempElse
                else:
                    raise Exception(
                        "Erro sintatico: falta de token606_endelse na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do token205_} na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do token204_{ ou bloco vazio na linha "
                + str(self.tokenAtual().linha)
            )


    def while_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "token202_(":
            self.indexDaTabelaDeTokens += 1
            tempExpression = []
            tempExpression = self.expression_statement(tempExpression)
            temp.append(tempExpression)
            if self.tokenAtual().tipo == "token203_)":
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "token204_{":
                    self.indexDaTabelaDeTokens += 1
                    self.indexEscopoAtual += 1
                    tempBlock = []
                    while (
                        self.tokenAtual().tipo != "token205_}"
                        and self.tokenLookAhead().tipo != "token607_endwhile"
                    ):
                        tempBlock.append(self.block2_statement())

                    temp.append(tempBlock)

                    if self.tokenAtual().tipo == "token205_}":
                        self.indexDaTabelaDeTokens += 1
                        if self.tokenAtual().tipo == "token607_endwhile":
                            temp.append(self.tokenAtual().tipo)
                            self.indexDaTabelaDeTokens += 1
                            self.tabelaDeSimbolos.append(temp)
                            self.indexEscopoAtual -= 1
                        else:
                            raise Exception(
                                "Erro sintatico: falta de token607_endwhile na linha "
                                + str(self.tokenAtual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sintatico: falta do token205_} na linha "
                            + str(self.tokenAtual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sintatico: falta do token204_{ na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do token203_) na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do token202_( na linha "
                + str(self.tokenAtual().linha)
            )


    def unconditional_branch_statement(self):
        if self.tokenAtual().tipo == "token614_cont":
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "token200_;":
                self.indexDaTabelaDeTokens += 1
            else:
                raise Exception(
                    "Erro sintatico: falta do ponto e virgula na linha "
                    + str(self.tokenAtual().linha)
                )

        if self.tokenAtual().tipo == "token613_break":
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "token200_;":
                self.indexDaTabelaDeTokens += 1
            else:
                raise Exception(
                    "Erro sintatico: falta do ponto e virgula na linha "
                    + str(self.tokenAtual().linha)
                )


    def expression_statement(self, tempExpression):
        if self.tokenAtual().tipo == "token500_Id" or self.tokenAtual().tipo == "token300_Num":
            tempExpression.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                self.tokenAtual().tipo == "token105_=="
                or self.tokenAtual().tipo == "token106_!="
                or self.tokenAtual().tipo == "token110<="
                or self.tokenAtual().tipo == "token109_<"
                or self.tokenAtual().tipo == "token108_>="
                or self.tokenAtual().tipo == "token107_>"
            ):
                tempExpression.append(self.tokenAtual().lexema)
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "token500_Id" or self.tokenAtual().tipo == "token300_Num":
                    tempExpression.append(self.tokenAtual().lexema)
                    self.indexDaTabelaDeTokens += 1
                    return tempExpression
                else:
                    raise Exception(
                        "Erro sintatico: falta do token500_Id na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do operador booleano na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do token500_Id na linha " +
                str(self.tokenAtual().linha)
            )


    def call_op_statement(self, tempEndVar):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "token500_Id" or self.tokenAtual().tipo == "token300_Num":
            tempEndVar.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                self.tokenAtual().tipo == "token101_+"
                or self.tokenAtual().tipo == "token102_-"
                or self.tokenAtual().tipo == "token103_*"
                or self.tokenAtual().tipo == "token104_/"
            ):
                tempEndVar.append(self.tokenAtual().lexema)
                self.call_op_statement(tempEndVar)

                expressaoTratada = arvoreExpressao(tempEndVar)

                var = expressaoTresEnderecos(expressaoTratada)

                self.tabelaDeTresEnderecos.extend(var)


            else:
                return
        else:
            raise Exception(
                "Erro sintatico: falta do token500_Id na linha " +
                str(self.tokenAtual().linha)
            )





























































    """

 Análise Semântica

    """

    # Não finalizado

    def checkSemantica(self):
        for k in range(len(self.tabelaDeSimbolos)):
            simbolo = self.tabelaDeSimbolos[k][2]
            if simbolo == "token602_func":
                self.declaration_func_semantico(self.tabelaDeSimbolos[k])

            if simbolo == "token615_proc":
                self.declaration_proc_semantico(self.tabelaDeSimbolos[k])

            if simbolo == "token604_call":
                if self.tabelaDeSimbolos[k][3] == "token602_func":
                    self.call_func_semantico(
                        self.tabelaDeSimbolos[k],
                        4,
                        self.tabelaDeSimbolos[k][0],
                        5,
                        self.tabelaDeSimbolos[k][1],
                    )
                if self.tabelaDeSimbolos[k][3] == "token615_proc":
                    self.call_proc_semantico(
                        self.tabelaDeSimbolos[k], 5, self.tabelaDeSimbolos[k][1]
                    )

            if simbolo == "token609_int" or simbolo == "token610_bool":
                self.declaration_var_semantico(self.tabelaDeSimbolos[k])

            if simbolo == "token605_if":
                self.expression_semantico(self.tabelaDeSimbolos[k])

            if simbolo == "token607_while":
                self.expression_semantico(self.tabelaDeSimbolos[k])

            if simbolo == "token500_Id":
                self.call_var_semantico(self.tabelaDeSimbolos[k])

        print("#============================#\n")
        print("#  FIM DA ANÁLISE SEMÂNTICA  #\n")
        print("#  FINALIZADO SEM PROBLEMAS  #\n")
        print("#============================#\n")
        
    def buscarNaTabelaDeSimbolos(self, simbolo, indice):
        for k in range(len(self.tabelaDeSimbolos)):
            if self.tabelaDeSimbolos[k][indice] == simbolo:
                return self.tabelaDeSimbolos[k]


    def declaration_var_semantico(self, tabelaNoIndiceAtual):
        if tabelaNoIndiceAtual[2] == "token609_int":
            simbolo = tabelaNoIndiceAtual[5][0]
            if simbolo.isnumeric():
                return True


            if simbolo == "token604_call":
                if tabelaNoIndiceAtual[5][1] == "token602_func":
                    for k in range(len(self.tabelaDeSimbolos)):
                        if self.tabelaDeSimbolos[k][2] == "token602_func":
                            if self.tabelaDeSimbolos[k][4] == tabelaNoIndiceAtual[5][2]:
                                if (
                                    self.tabelaDeSimbolos[k][0]
                                    <= tabelaNoIndiceAtual[0]
                                ) and (
                                    self.tabelaDeSimbolos[k][1]
                                    <= tabelaNoIndiceAtual[1]
                                ):
                                    if len(self.tabelaDeSimbolos[k][5]) == len(
                                        tabelaNoIndiceAtual[5][3]
                                    ):
                                        for n in range(len(tabelaNoIndiceAtual[5][3])):
                                            varDeclaradaNaTabela = self.buscarNaTabelaDeSimbolos(
                                                tabelaNoIndiceAtual[5][3][n], 3)
                                            if(varDeclaradaNaTabela != None):
                                                if (varDeclaradaNaTabela[0] <= tabelaNoIndiceAtual[0]
                                                    ) and (varDeclaradaNaTabela[1] <= tabelaNoIndiceAtual[1]):
                                                    if(varDeclaradaNaTabela[2] == self.tabelaDeSimbolos[k][5][n][1]):
                                                        if self.tabelaDeSimbolos[k][3] == "token609_int":
                                                            return True
                                                        else:
                                                            raise Exception(
                                                                "Erro Semântico: token609_int não recebe token609_int na linha: "
                                                                + str(tabelaNoIndiceAtual[1])
                                                            )
                                                    else:
                                                        raise Exception(
                                                            "Erro Semântico: tipo de variáveis incompativéis nos parametros na linha: "
                                                            + str(tabelaNoIndiceAtual[1])
                                                        )
                                                else:
                                                    raise Exception(
                                                        "Erro Semântico: variável não declarada nos parametros na linha: "
                                                        + str(tabelaNoIndiceAtual[1])
                                                    )
                                            else:
                                                raise Exception(
                                                    "Erro Semântico: variável não declarada nos parametros na linha: "
                                                    + str(tabelaNoIndiceAtual[1])
                                                )
                                    else:
                                        raise Exception(
                                            "Erro Semântico: quantidade de parametros inválida na linha: "
                                            + str(tabelaNoIndiceAtual[1])
                                        )
                                else:
                                    raise Exception(
                                        "Erro Semântico: função não declarada na linha: "
                                        + str(tabelaNoIndiceAtual[1])
                                    )

                            else:
                                raise Exception(
                                    "Erro Semântico: função não declarada na linha: "
                                    + str(tabelaNoIndiceAtual[1])
                                )
                else:
                    raise Exception(
                        "Erro Semântico: variável não pode receber procedimento na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )

            if simbolo.isalpha() and simbolo != 'True' and simbolo != 'False':
                varDeclarada = self.buscarNaTabelaDeSimbolos(
                    tabelaNoIndiceAtual[5][0], 3
                )
                if varDeclarada != None:
                    if (
                        varDeclarada[0] <= tabelaNoIndiceAtual[0]
                        and varDeclarada[1] <= tabelaNoIndiceAtual[1]
                    ):
                        if varDeclarada[2] == "token609_int":
                            return True
                        else:
                            raise Exception(
                                "Erro Semântico: variável do tipo token609_int não recebe token609_int na linha: "
                                + str(tabelaNoIndiceAtual[1])
                            )
                    else:
                        raise Exception(
                            "Erro Semântico: variavel não declarada na linha: "
                            + str(tabelaNoIndiceAtual[1])
                        )
                else:
                    raise Exception(
                        "Erro Semântico: variavel não declarada na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )
            else:
                raise Exception(
                    "Erro Semântico: variável do tipo inteiro não recebe inteiro na linha: "
                    + str(tabelaNoIndiceAtual[1])
                )

        if tabelaNoIndiceAtual[2] == "token610_bool":

   
            simbolo = tabelaNoIndiceAtual[5][0]
            if simbolo == "True" or simbolo == "False":
                return True

            if simbolo.isnumeric():
                raise Exception(
                    "Erro Semântico: variável do tipo token611_boolValue não recebe token611_boolValue na linha: "
                    + str(tabelaNoIndiceAtual[1])
                )

            if simbolo == "token604_call":

                if tabelaNoIndiceAtual[5][1] == "token602_func":
                    for k in range(len(self.tabelaDeSimbolos)):
                        if self.tabelaDeSimbolos[k][2] == "token602_func":
                            if self.tabelaDeSimbolos[k][4] == tabelaNoIndiceAtual[5][2]:
                                if (
                                    self.tabelaDeSimbolos[k][0]
                                    <= tabelaNoIndiceAtual[0]
                                ) and (
                                    self.tabelaDeSimbolos[k][1]
                                    <= tabelaNoIndiceAtual[1]
                                ):
                                    if len(self.tabelaDeSimbolos[k][5]) == len(
                                        tabelaNoIndiceAtual[5][3]
                                    ):
                                        for n in range(len(tabelaNoIndiceAtual[5][3])):
                                            varDeclaradaNaTabela = self.buscarNaTabelaDeSimbolos(
                                                tabelaNoIndiceAtual[5][3][n], 3)
                                            if(varDeclaradaNaTabela != None):
                                                if (varDeclaradaNaTabela[0] <= tabelaNoIndiceAtual[0]
                                                    ) and (varDeclaradaNaTabela[1] <= tabelaNoIndiceAtual[1]):
                                                    if(varDeclaradaNaTabela[2] == self.tabelaDeSimbolos[k][5][n][1]):
                                                        if self.tabelaDeSimbolos[k][3] == "token610_bool":
                                                            return True
                                                        else:
                                                            raise Exception(
                                                                "Erro Semântico: token611_boolValue não recebe token611_boolValue na linha: "
                                                                + str(tabelaNoIndiceAtual[1])
                                                            )
                                                    else:
                                                        raise Exception(
                                                            "Erro Semântico: tipo de variáveis incompativéis nos parametros na linha: "
                                                            + str(tabelaNoIndiceAtual[1])
                                                        )
                                                else:
                                                    raise Exception(
                                                        "Erro Semântico: variável não declarada nos parametros na linha: "
                                                        + str(tabelaNoIndiceAtual[1])
                                                    )
                                            else:
                                                raise Exception(
                                                    "Erro Semântico: variável não declarada nos parametros na linha: "
                                                    + str(tabelaNoIndiceAtual[1])
                                                )
                                    else:
                                        raise Exception(
                                            "Erro Semântico: quantidade de parametros inválida na linha: "
                                            + str(tabelaNoIndiceAtual[1])
                                        )
                                else:
                                    raise Exception(
                                        "Erro Semântico: função não declarada na linha: "
                                        + str(tabelaNoIndiceAtual[1])
                                    )

                            else:
                                raise Exception(
                                    "Erro Semântico: função não declarada na linha: "
                                    + str(tabelaNoIndiceAtual[1])
                                )
                else:
                    raise Exception(
                        "Erro Semântico: variável não pode receber procedimento na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )


            if simbolo.isalpha() and simbolo != 'True' and simbolo != 'False':
                varDeclarada = self.buscarNaTabelaDeSimbolos(
                    tabelaNoIndiceAtual[5][0], 3
                )
                if varDeclarada != None:
                    if (
                        varDeclarada[0] <= tabelaNoIndiceAtual[0]
                        and varDeclarada[1] <= tabelaNoIndiceAtual[1]
                    ):
                        if varDeclarada[2] == "token610_bool":
                            if (varDeclarada[5][0] == 'True' or varDeclarada[5][0] == 'False'):
                                return True
                            else:
                                raise Exception(
                                    "Erro Semântico: variável do tipo token611_boolValue não recebe token611_boolValue na linha: "
                                    + str(tabelaNoIndiceAtual[1])
                                )
                        else:
                            raise Exception(
                                "Erro Semântico: variável do tipo token611_boolValue não recebe token611_boolValue na linha: "
                                + str(tabelaNoIndiceAtual[1])
                            )
                    else:
                        raise Exception(
                            "Erro Semântico: variavel não declarada na linha: "
                            + str(tabelaNoIndiceAtual[1])
                        )
                else:
                    raise Exception(
                        "Erro Semântico: variavel não declarada na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )

            else:
                raise Exception(
                    "Erro Semântico: variável do tipo token611_boolValue não recebe token611_boolValue na linha: "
                    + str(tabelaNoIndiceAtual[1])
                )


    def call_var_semantico(self, simbolo):
        flag = False
        for k in range(len(self.tabelaDeSimbolos)):
            if (
                self.tabelaDeSimbolos[k][2] == "token609_int"
                or self.tabelaDeSimbolos[k][2] == "token610_bool"
            ):
                if self.tabelaDeSimbolos[k][3] == simbolo[3]:
       
                    if self.tabelaDeSimbolos[k][0] <= simbolo[0]:
                        if self.tabelaDeSimbolos[k][1] <= simbolo[1]:
                            flag = True  
                            self.verificarTipoCallVar(
                                self.tabelaDeSimbolos[k], simbolo)
                            break

            elif self.buscarParamsProc(simbolo) == True:
                flag = True
                break

            elif self.buscarParamsFunc(simbolo, 3) == True:
                flag = True
                break

        if flag == False:
            raise Exception(
                "Erro Semântico: variável não declarada na linha: " +
                str(simbolo[1])
            )

    def buscarParamsProc(self, simbolo):
        paramsProc = self.buscarNaTabelaDeSimbolos("token615_proc", 2)
        if paramsProc != None:
            paramsProc = paramsProc[4]
            for k in range(len(paramsProc)):
                if simbolo[3] == paramsProc[k][2]:
                    if paramsProc[k][1] == "token609_int":
                        if simbolo[5].isnumeric():
                            return True
                        if not simbolo[5].isnumeric():
                            raise Exception(
                                "Erro Semântico: variável do tipo token609_int não recebe token609_int na linha: "
                                + str(simbolo[1])
                            )
                    if paramsProc[k][1] == "token610_bool":
                        if simbolo[5] == "True" or simbolo[5] == "False":
                            return True
                        else:
                            raise Exception(
                                "Erro Semântico: variável do tipo booleano não recebe booleano na linha: "
                                + str(simbolo[1])
                            )
                    break
        else:
            return False

    def buscarParamsFunc(self, simbolo, n):
        paramsFunc = self.buscarNaTabelaDeSimbolos("token602_func", 2)
        if paramsFunc != None:
            paramsFunc = paramsFunc[5]
            for k in range(len(paramsFunc)):
                if simbolo[n] == paramsFunc[k][2]:
                    if paramsFunc[k][1] == "token609_int":
                        if simbolo[5].isnumeric():
                            return True
                        if not simbolo[5].isnumeric():
                            raise Exception(
                                "Erro Semântico: variável do tipo token609_int não recebe token609_int na linha: "
                                + str(simbolo[1])
                            )
                    if paramsFunc[k][1] == "token610_bool":
                        if simbolo[5] == "True" or simbolo[5] == "False":
                            return True
                        else:
                            raise Exception(
                                "Erro Semântico: variável do tipo booleano não recebe booleano na linha: "
                                + str(simbolo[1])
                            )
                    break
        else:
            return False

    def verificarTipoCallVar(self, simboloDeclaradoNaTabela, simbolo):
        if simboloDeclaradoNaTabela[2] == "token609_int":
            if not simbolo[5].isnumeric():
                raise Exception(
                    "Erro Semântico: variável do tipo token609_int não recebe token609_int na linha: "
                    + str(simbolo[1])
                )
        if simboloDeclaradoNaTabela[2] == "token610_bool":
            if simbolo[5] == "True" or simbolo[5] == "False":
                return True
            else:
                raise Exception(
                    "Erro Semântico: variável do tipo booleano não recebe booleano na linha: "
                    + str(simbolo[1])
                )

    def declaration_func_semantico(self, tabelaNoIndiceAtual):
        if tabelaNoIndiceAtual[3] == "token609_int":
            if not tabelaNoIndiceAtual[7][2][0].isnumeric():
                raise Exception(
                    "Erro Semântico: O retorno espera um inteiro na linha: "
                    + str(tabelaNoIndiceAtual[1])
                )

        if tabelaNoIndiceAtual[3] == "token610_bool":
            if (
                tabelaNoIndiceAtual[7][2][0] == "True"
                or tabelaNoIndiceAtual[7][2][0] == "False"
            ) is False:
                raise Exception(
                    "Erro Semântico: O retorno espera um token611_boolValue na linha: "
                    + str(tabelaNoIndiceAtual[1])
                )

    def call_func_semantico(self, tabelaNoIndiceAtual, n, escopo, m, linha):
        flag = False
        for k in range(len(self.tabelaDeSimbolos)):
            if self.tabelaDeSimbolos[k][2] == "token602_func":
                if self.tabelaDeSimbolos[k][4] == tabelaNoIndiceAtual[n]:
                    if self.tabelaDeSimbolos[k][0] <= escopo:
                        flag = True
                        self.verificarParams(
                            self.tabelaDeSimbolos[k],
                            tabelaNoIndiceAtual,
                            5,
                            "token602_func",
                            m,
                            linha,
                            escopo,
                        )
                        return True
                        break

        if flag == False:
            raise Exception(
                "Erro Semântico: função não declarada na linha: "
                + str(tabelaNoIndiceAtual[1])
            )

    def verificarParams(
        self, simboloDeclaradoNaTabela, simbolo, n, tipo, m, linha, escopo
    ):
        # PASSO A PASSO:
        # 1º -> Verificar quantidade de parametros de acordo com a declaração
        # 2º -> Se for > 0
        # Devemos percorrer cada variavel dos parametros, então verificar em cada um o seguinte:
        # 1º -> Verificar se já foi declarada no escopo visível ok
        # 2º -> Verificar se o tipo na chamada é o mesmo da declaração ok
        # 3º -> Se for sem params, prosseguir

        flag = 0
        if len(simboloDeclaradoNaTabela[n]) == len(simbolo[m]):
            if len(simbolo[m]) > 0:
                for k in range(len(simbolo[m])):
                    for i in range(len(self.tabelaDeSimbolos)):
                        if self.tabelaDeSimbolos[i][3] == simbolo[m][k]:
                            if (self.tabelaDeSimbolos[i][0] <= escopo) and (
                                self.tabelaDeSimbolos[i][1] <= linha
                            ):
                                if (
                                    self.tabelaDeSimbolos[i][2] == "token609_int"
                                    or self.tabelaDeSimbolos[i][2] == "token610_bool"
                                ):
                                    flag += 1
                                    self.comparaTipoChamadaComDeclaracao(
                                        self.tabelaDeSimbolos[i], simbolo, tipo, n
                                    )
                                break

            else:
                return True
        else:
            raise Exception(
                "Erro Semântico: quantidade de parâmetros inválido na linha: "
                + str(linha)
            )

        if flag != len(simboloDeclaradoNaTabela[n]):
            raise Exception(
                "Erro Semântico: variável do parâmetro não declarada na linha: "
                + str(linha)
            )
        else:
            return True

    def comparaTipoChamadaComDeclaracao(
        self, declaracaoVarNaTabela, callFuncTabela, tipo, n
    ):
        declaracaoFuncNaTabela = self.buscarNaTabelaDeSimbolos(tipo, 2)
        flag = False
        for k in range(len(declaracaoFuncNaTabela[n])):
            if declaracaoFuncNaTabela[n][k][1] == declaracaoVarNaTabela[2]:
                flag = True
                break


            elif declaracaoVarNaTabela[2] == "token500_Id":
                tipoDeclaracaoDoID = self.buscarNaTabelaDeSimbolos("token500_Id", 2)
                varDeclarada = self.buscarNaTabelaDeSimbolos(
                    tipoDeclaracaoDoID[3], 3)
                if declaracaoFuncNaTabela[n][k][1] == varDeclarada[2]:
                    flag = True
                    break

        if flag == False:
            raise Exception(
                "Erro Semântico: tipo do parâmetro inválido na linha: "
                + str(callFuncTabela[1])
            )

    def declaration_proc_semantico(self, tabelaNoIndiceAtual):


        flag = False
        cont = 0
        for k in range(len(self.tabelaDeSimbolos)):
            for i in range(len(tabelaNoIndiceAtual[5])):
                if (
                    self.tabelaDeSimbolos[k][2] == "token610_bool"
                    or self.tabelaDeSimbolos[k][2] == "token609_int"
                ):
                    if tabelaNoIndiceAtual[5][i] == self.tabelaDeSimbolos[k][3]:
                        if (
                            self.tabelaDeSimbolos[k][0] <= tabelaNoIndiceAtual[0]
                            and self.tabelaDeSimbolos[k][1] <= tabelaNoIndiceAtual[1]
                        ):
   
                            if self.tabelaDeSimbolos[k][2] == "token609_int":
                                if not tabelaNoIndiceAtual[5][i][5].isnumeric():
                                    raise Exception(
                                        "Erro Semântico: variável do tipo token609_int não recebe token609_int na linha: "
                                        + str(tabelaNoIndiceAtual[1])
                                    )
                                else:
                                    cont += 1
                                    flag = True
                                    break
                                    return True

                            elif self.tabelaDeSimbolos[k][2] == "token610_bool":
                                if (
                                    tabelaNoIndiceAtual[5][i][5] == "True"
                                    or tabelaNoIndiceAtual[5][i][5] == "False"
                                ):
                                    cont += 1
                                    flag = True
                                    break
                                    return True
                                else:
                                    raise Exception(
                                        "Erro Semântico: variável do tipo booleano não recebe booleano na linha: "
                                        + str(tabelaNoIndiceAtual[1])
                                    )

                    else:
                        for m in range(len(tabelaNoIndiceAtual[5])):
                            for n in range(len(tabelaNoIndiceAtual[4])):
                                if (
                                    tabelaNoIndiceAtual[5][m][3]
                                    == tabelaNoIndiceAtual[4][n][2]
                                ):
                                    if tabelaNoIndiceAtual[4][n][1] == "token609_int":
                                        if not tabelaNoIndiceAtual[5][m][5].isnumeric():
                                            raise Exception(
                                                "Erro Semântico: variável do tipo token609_int não recebe token609_int na linha: "
                                                + str(tabelaNoIndiceAtual[1])
                                            )
                                        else:
                                            cont += 1
                                            flag = True
                                            break
                                            return True

                                    if tabelaNoIndiceAtual[4][n][1] == "token610_bool":
                                        if (
                                            tabelaNoIndiceAtual[5][i][5] == "True"
                                            or tabelaNoIndiceAtual[5][i][5] == "False"
                                        ):
                                            cont += 1
                                            flag = True
                                            break
                                            return True
                                        else:
                                            raise Exception(
                                                "Erro Semântico: variável do tipo booleano não recebe booleano na linha: "
                                                + str(tabelaNoIndiceAtual[1])
                                            )
                else:
                    for m in range(len(tabelaNoIndiceAtual[5])):
                        for n in range(len(tabelaNoIndiceAtual[4])):
                            if (
                                tabelaNoIndiceAtual[5][m][3]
                                == tabelaNoIndiceAtual[4][n][2]
                            ):
                                if tabelaNoIndiceAtual[4][n][1] == "token609_int":
                                    if not tabelaNoIndiceAtual[5][m][5].isnumeric():
                                        raise Exception(
                                            "Erro Semântico: variável do tipo token609_int não recebe token609_int na linha: "
                                            + str(tabelaNoIndiceAtual[1])
                                        )
                                    else:
                                        cont += 1
                                        flag = True
                                        break
                                        return True

                                if tabelaNoIndiceAtual[4][n][1] == "token610_bool":
                                    if (
                                        tabelaNoIndiceAtual[5][i][5] == "True"
                                        or tabelaNoIndiceAtual[5][i][5] == "False"
                                    ):
                                        cont += 1
                                        flag = True
                                        break
                                        return True
                                    else:
                                        raise Exception(
                                            "Erro Semântico: variável do tipo booleano não recebe booleano na linha: "
                                            + str(tabelaNoIndiceAtual[1])
                                        )

        if flag == False and (cont != len(tabelaNoIndiceAtual[4])):
            raise Exception(
                "Erro Semântico: variável não declarada na linha: "
                + str(tabelaNoIndiceAtual[1])
            )

    def call_proc_semantico(self, tabelaNoIndiceAtual, m, linha):

        flag = False
        for k in range(len(self.tabelaDeSimbolos)):
            if self.tabelaDeSimbolos[k][2] == "token615_proc":
                if self.tabelaDeSimbolos[k][3] == tabelaNoIndiceAtual[4]:
                    if self.tabelaDeSimbolos[k][0] <= tabelaNoIndiceAtual[0]:
                        flag = True
                        self.verificarParams(
                            self.tabelaDeSimbolos[k],
                            tabelaNoIndiceAtual,
                            4,
                            "token615_proc",
                            m,
                            linha,
                            tabelaNoIndiceAtual[0],
                        )
                        break

        if flag == False:
            raise Exception(
                "Erro Semântico: procedimento não declarado na linha: "
                + str(tabelaNoIndiceAtual[1])
            )

    def expression_semantico(self, tabelaNoIndiceAtual):
        buscaParam1 = self.buscarNaTabelaDeSimbolos(
            tabelaNoIndiceAtual[3][0], 3)
        buscaParam2 = self.buscarNaTabelaDeSimbolos(
            tabelaNoIndiceAtual[3][2], 3)

        if (tabelaNoIndiceAtual[3][0]).isnumeric() and (
            tabelaNoIndiceAtual[3][2]
        ).isnumeric():
            return True

        elif (
            tabelaNoIndiceAtual[3][0].isalpha(
            ) and tabelaNoIndiceAtual[3][2].isalpha()
        ):
            if buscaParam1 != None and buscaParam2 != None:
                if buscaParam1[2] == "token609_int" and buscaParam2[2] != "token609_int":
                    raise Exception(
                        "Erro Semântico: Não é possível comparar dois tipos diferentes na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )
                if buscaParam2[2] == "token609_int" and buscaParam1[2] != "token609_int":
                    raise Exception(
                        "Erro Semântico: Não é possível comparar dois tipos diferentes na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )

                if buscaParam2[2] == "token609_int" and buscaParam1[2] == "token609_int":
                    if (buscaParam1[0] <= tabelaNoIndiceAtual[0]) and (
                        buscaParam2[0] <= tabelaNoIndiceAtual[0]
                    ):
                        return True
                    else:
                        raise Exception(
                            "Erro Semântico: Variável não declarada na linha: "
                            + str(tabelaNoIndiceAtual[1])
                        )
                if buscaParam2[2] == "token610_bool" and buscaParam1[2] == "token610_bool":
                    if (buscaParam1[0] <= tabelaNoIndiceAtual[0]) and (
                        buscaParam2[0] <= tabelaNoIndiceAtual[0]
                    ):
                        if (
                            tabelaNoIndiceAtual[3][1] == "=="
                            or tabelaNoIndiceAtual[3][1] == "!="
                        ):
                            return True
                        else:
                            raise Exception(
                                "Erro Semântico: Não é possível fazer este tipo de comparação com token611_boolValue na linha: "
                                + str(tabelaNoIndiceAtual[1])
                            )
                    else:
                        raise Exception(
                            "Erro Semântico: Variável não declarada na linha: "
                            + str(tabelaNoIndiceAtual[1])
                        )

                if buscaParam2[2] == "token609_int" and buscaParam1[2] != "token610_bool":
                    raise Exception(
                        "Erro Semântico: Não é possível comparar dois tipos diferentes na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )
                if buscaParam2[2] == "token610_bool" and buscaParam1[2] != "token609_int":
                    raise Exception(
                        "Erro Semântico: Não é possível comparar dois tipos diferentes na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )
            else:
                raise Exception(
                    "Erro Semântico: variavel não declarada na linha: "
                    + str(tabelaNoIndiceAtual[1])
                )

        elif (
            tabelaNoIndiceAtual[3][0].isalpha()
            and (tabelaNoIndiceAtual[3][2]).isnumeric()
        ):
            if buscaParam1 != None:
                if buscaParam1[2] != "token609_int":
                    raise Exception(
                        "Erro Semântico: Não é possível comparar dois tipos diferentes na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )
                else:
                    if buscaParam1[0] <= tabelaNoIndiceAtual[0]:
                        return True
                    else:
                        raise Exception(
                            "Erro Semântico: Variável não declarada na linha: "
                            + str(tabelaNoIndiceAtual[1])
                        )
            else:
                raise Exception(
                    "Erro Semântico: variavel não declarada na linha: "
                    + str(tabelaNoIndiceAtual[1])
                )

        elif (tabelaNoIndiceAtual[3][0]).isnumeric() and tabelaNoIndiceAtual[3][
            2
        ].isalpha():
            if buscaParam2 != None:
                if buscaParam2[2] != "token609_int":
                    raise Exception(
                        "Erro Semântico: Não é possível comparar dois tipos diferentes na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )
                else:
                    if buscaParam2[0] <= tabelaNoIndiceAtual[0]:
                        return True
                    else:
                        raise Exception(
                            "Erro Semântico: Variável não declarada na linha: "
                            + str(tabelaNoIndiceAtual[1])
                        )
            else:
                raise Exception(
                    "Erro Semântico: variavel não declarada na linha: "
                    + str(tabelaNoIndiceAtual[1])
                )

        else:
            raise Exception(
                "Erro Semântico: parametros inválidos na linha: "
                + str(tabelaNoIndiceAtual[1])
            )
