from pprint import pprint
from lexemas import LEX_DIFERENTE, LEX_DIV, LEX_FALSE, LEX_IGUAL, LEX_MAIOR, LEX_MAIORIGUAL, LEX_MENOR, LEX_MENORIGUAL, LEX_MULT, LEX_SOMA, LEX_SUB, LEX_TRUE

from tokens import TOKEN_ABRE_PARENTESES, TOKEN_BOOL, TOKEN_BREAK, TOKEN_CALL, TOKEN_CONTINUE, TOKEN_DIFERENTE, TOKEN_DIV, TOKEN_FECHA_CHAVES, TOKEN_FECHA_PARENTESES, TOKEN_ID, TOKEN_IGUAL, TOKEN_INT, TOKEN_MAIOR, TOKEN_MAIORIGUAL, TOKEN_MENOR, TOKEN_MENORIGUAL, TOKEN_MULT, TOKEN_NUM, TOKEN_PONTOVIRGULA, TOKEN_PROC, TOKEN_SOMA, TOKEN_SUB, TOKEN_TRUEFALSE, TOKEN_WHILE


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
        self.indexTresEnderecos = 1
        self.tempAtualTresEnd = 0

    def token_atual(self):
        return self.tabelaDeTokens[self.indexDaTabelaDeTokens]

    def token_look_ahead(self):
        self.indexLookAhead = self.indexDaTabelaDeTokens + 1
        return self.tabelaDeTokens[self.indexLookAhead]

    def start(self):
        escopoPai = self.indexEscopoAtual  
        self.indexEscopoAtual += 1
        self.statement_list()  

        for linha in self.tabelaDeTresEnderecos:
           pprint(linha)
        print('\n')

        self.checkSemantica()
        return

    def statement_list(self):
        if self.token_atual().tipo == "token601_end":
            return
        else:
            self.statement()
            self.statement_list()
            return

    def statement(self):
        if self.token_atual().tipo == "token600_main":
            self.indexDaTabelaDeTokens += 1
            if self.token_atual().tipo == "token204_{":
                self.indexDaTabelaDeTokens += 1

                while self.token_atual().tipo != "token205_}":
                    self.block_statement()

                if self.token_atual().tipo == "token205_}":
                    self.indexDaTabelaDeTokens += 1

                    if self.token_atual().tipo == "token601_end":
                        print("#============================#\n")
                        print("#  FIM DA ANÁLISE SINTÁTICA  #\n")
                        print("#  FINALIZADO SEM PROBLEMAS  #\n")
                        print("#============================#\n")   
                        self.tabelaDeTresEnderecos.append(
                            '$'
                        )                     
                    else:
                        raise Exception(
                            "Erro sintatico: falta do token601_end na linha "
                            + str(self.token_atual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sintatico: falta do token205_} na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do token204_{ na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: Código fora do padrão na linha "
                + str(self.token_atual().linha)
            )

    def block_statement(self, context = False, is_while: bool = False, is_if: bool = False, is_proc: bool = False):
        if self.token_atual().tipo == "token609_int" or self.token_atual().tipo == "token610_bool":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.declaration_var_statement(temp, context=context)
            return temp

        if self.token_atual().tipo == "token602_func":

            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.declaration_func_statement(temp)
            return temp

        if self.token_atual().tipo == "token615_proc":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.declaration_proc_statement(temp)
            return temp

        if self.token_atual().tipo == "token604_call":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.indexDaTabelaDeTokens += 1
            temp = self.call_proc_statement(temp)
    
            if self.token_atual().tipo == "token200_;":
                self.salvar_call_proc_tres_enderecos(temp)
                self.indexDaTabelaDeTokens += 1
                if not context:
                    self.tabelaDeSimbolos.append(temp)
                return temp
            else:
                raise Exception(
                    "aErro sintatico: falta do ponto e virgula na linha "
                    + str(self.token_atual().linha)
                )

        if self.token_atual().tipo == "token608_print":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.print_statement(temp)
            return temp


        if self.token_atual().tipo == "token605_if":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            if is_while:
                self.ifStatementWhile(temp, is_proc)

                condicao = temp[3]
                params = ''
                for param in condicao:
                    params += param + ", "
                params = params[:-2]  
                self.tabelaDeTresEnderecos.append("temp"+str(self.tempAtualTresEnd)+" := "+params)
                self.tabelaDeTresEnderecos.append("if false temp"+str(self.tempAtualTresEnd)+" go to fimIf"+str(self.tempAtualIfTresEnd))
                self.tabelaDeTresEnderecos.append("fimIf"+str(self.tempAtualIfTresEnd)+":")
                self.tempAtualTresEnd += 1
                self.tempAtualIfTresEnd += 1
                return temp
            else:
                self.if_statement(temp)
                self.salvar_if_tres_enderecos(temp)
                return temp


        if self.token_atual().tipo == "token607_while":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.while_statement(temp)
            self.salvar_while_tres_enderecos(temp)
            return temp


        if self.token_atual().tipo == "token500_Id": # Tratar aqui assim como é tratado quando ele acha Int ou bool
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            # temp.append(self.token_atual().lexema)
            self.declaration_var_statement(temp, is_attribution=True, context=context)
            # self.call_var_statement(temp)
            return temp

        else:
            raise Exception(
                f'Erro sintático: Token {self.token_atual().lexema} não é válido no escopo atual'
            )

    # block2 é o bloco que contém break/continue que só pode ser chamado dentro de um while
    def block2_statement(self, context = True):

        if self.token_atual().tipo == "token609_int" or self.token_atual().tipo == "token610_bool":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.declaration_var_statement(temp)
            return temp


        if self.token_atual().tipo == "token604_call":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.indexDaTabelaDeTokens += 1

            if self.token_atual().tipo == "token602_func":
                temp.append(self.token_atual().tipo)
                temp = self.call_func_statement(temp)
                if self.token_atual().tipo == "token200_;":
                    if not context:
                        self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return temp
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.token_atual().linha)
                    )

            elif self.token_atual().tipo == "token615_proc":
                temp.append(self.token_atual().tipo)
                temp = self.call_proc_statement(temp)
                if self.token_atual().tipo == "token200_;":
                    if not context:
                        self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return temp
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta de token615_proc ou token602_func"
                    + str(self.token_atual().linha)
                )


        if self.token_atual().tipo == "token608_print":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.print_statement(temp)
            return temp


        if self.token_atual().tipo == "token605_if":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.if_statement2(temp, context)
            return temp


        if self.token_atual().tipo == "token606_else":
            raise Exception(
                "Erro sintatico: token606_else adicionado de maneira incorreta "
                + str(self.token_atual().linha)
            )


        if self.token_atual().tipo == "token607_while":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.while_statement(temp)
            return temp


        if self.token_atual().tipo == "token500_Id":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            temp.append(self.token_atual().lexema)
            self.call_var_statement(temp)
            return temp

 
        if self.token_atual().tipo == "token613_break" or self.token_atual().tipo == "token614_cont":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.unconditional_branch_statement()
            return temp

        else:
            raise Exception(
                f'Erro sintático: Token {self.token_atual().lexema} não é válido no escopo atual'
            )

    # block2 é o que só pode ser chamado dentro de um if
    def block3_statement(self, context=False):

        if self.token_atual().tipo == "token609_int" or self.token_atual().tipo == "token610_bool":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.declaration_var_statement(temp)
            return temp


        if self.token_atual().tipo == "token604_call":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.indexDaTabelaDeTokens += 1

            if self.token_atual().tipo == "token602_func":
                temp.append(self.token_atual().tipo)
                temp = self.call_func_statement(temp)
                if self.token_atual().tipo == "token200_;":
                    if not context:
                        self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return temp
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.token_atual().linha)
                    )

            elif self.token_atual().tipo == "token615_proc":
                temp.append(self.token_atual().tipo)
                temp = self.call_proc_statement(temp)
                if self.token_atual().tipo == "token200_;":
                    if not context:
                        self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return temp
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta de token615_proc ou token602_func"
                    + str(self.token_atual().linha)
                )


        if self.token_atual().tipo == "token608_print":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.print_statement(temp)
            return temp


        if self.token_atual().tipo == "token605_if":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.if_statement(temp, context=True)
            return temp

        if self.token_atual().tipo == "token606_else":
            raise Exception(
                "Erro sintatico: token606_else adicionado de maneira incorreta "
                + str(self.token_atual().linha)
            )

        if self.token_atual().tipo == "token607_while":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.while_statement(temp)
            return temp

  
        if self.token_atual().tipo == "token500_Id":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            temp.append(self.token_atual().lexema)
            self.call_var_statement(temp, context=True)
            return temp

        else:
            raise Exception(
                f'Erro sintático: Token {self.token_atual().lexema} não é válido no escopo atual'
            )

    def declaration_var_statement(self, temp, is_attribution = False, context = False):
        if not is_attribution:
            self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token500_Id":
            temp.append(self.token_atual().lexema)
            self.indexDaTabelaDeTokens += 1
            if self.token_atual().tipo == "token111_=" and is_attribution:  # Tratar aqui para não permitir ou permitir atribuicao na declaracao
                temp.append(self.token_atual().lexema)
                self.indexDaTabelaDeTokens += 1
                temp.append([])
                self.end_var_statement(temp)

                if self.token_atual().tipo == "token200_;":
                    self.indexDaTabelaDeTokens += 1
                    if not context:
                        self.tabelaDeSimbolos.append(temp)
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.token_atual().linha)
                    )                
            elif self.token_atual().tipo == "token200_;":
                self.indexDaTabelaDeTokens += 1
                if not context:
                    self.tabelaDeSimbolos.append(temp)
            else:
                raise Exception(
                    f"Erro sintatico: token {self.token_atual().lexema} não é permitido em declaração de variável, linha "
                    + str(self.token_atual().linha)
                )
        elif self.token_atual().tipo == TOKEN_CALL:
            proc_dec = self.buscar_proc_decl()
        else:
            raise Exception(
                "Erro sintatico: nome da variável precisa ser declarado na linha " +
                str(self.token_atual().linha)
            )

    def buscar_func_decl_semantica(self, dados):
        for i in self.tabelaDeSimbolos:
            if (i[2] == 'token602_func'
                and i[4] == dados[5][1]
                and i[0] <= dados[0]
                and i[1] <= dados[1]
            ):
                if (len(i[5]) == len(dados[5][2])):
                    for index, param in enumerate(i[5]):
                        if (i[5][index][1] == 'token609_int'):
                            if not dados[5][2][index].isnumeric():
                                var_decl = self.call_buscar_var_decl(dados, dados[5][2][index])
                                if var_decl:
                                    continue
                                raise Exception(
                                    f'Erro semântico: Valor "{dados[5][2][index]}" não suportado no {index+1}º parâmetro da função {i[4]}, linha '
                                )
                        elif (i[5][index][1] == TOKEN_BOOL):
                            if (dados[5][2][index] != 'True'
                                and dados[5][2][index] != 'False'):
                                var_decl = self.call_buscar_var_decl(dados, dados[5][2][index])
                                if var_decl:
                                    continue
                                raise Exception(
                                    f'Erro semântico: Valor "{dados[5][2][index]}" não suportado no {index+1}º parâmetro da função {i[4]}, linha '
                                )
                    return i

    def buscar_proc_decl_semantica(self, dados):
        for i in self.tabelaDeSimbolos:
            if (i[2] == TOKEN_PROC
                and i[4] == dados[3]
                and i[0] <= dados[0]
                and i[1] <= dados[1]
            ):
                if (len(i[5]) == len(dados[4])):
                    for index, param in enumerate(i[5]):
                        if (i[5][index][1] == 'token609_int'):
                            if not dados[4][index].isnumeric():
                                var_decl = self.call_buscar_var_decl(dados, dados[4][index])
                                if var_decl:
                                    continue
                                raise Exception(
                                    f'Erro semântico: Valor "{dados[4][index]}" não suportado no {index+1}º parâmetro da função {i[4]}, linha '
                                )
                        elif (i[5][index][1] == TOKEN_BOOL):
                            if (dados[4][index] != 'True'
                                and dados[4][index] != 'False'):
                                var_decl = self.call_buscar_var_decl(dados, dados[4][index])
                                if var_decl:
                                    continue
                                raise Exception(
                                    f'Erro semântico: Valor "{dados[4][index]}" não suportado no {index+1}º parâmetro da função {i[4]}, linha '
                                )
                    return i

    def buscar_func_decl(self, dados, semantica = False):
        for i in self.tabelaDeSimbolos:
            if (i[2] == 'token602_func'
                and i[4] == dados[5][1]
                and i[0] <= dados[0]
                and i[1] <= dados[1]
            ):
                if (len(i[5]) == len(dados[5][2])):
                    for index, param in enumerate(i[5]):
                        if (i[5][index][1] == 'token609_int'):
                            if not dados[5][2][index].isnumeric():
                                if semantica:
                                    raise Exception(
                                        f'Erro semântico: tipo de parâmentro inválido na linha {self.token_atual().linha}'
                                    )
                                return []
                        elif (i[5][index][1] == 'token611_boolValue'):
                            if (dados[5][2][index] != 'True'
                                and dados[5][2][index] != 'False'):
                                if semantica:
                                    raise Exception(
                                        f'Erro semântico: tipo de parâmentro inválido na linha {self.token_atual().linha}'
                                    )
                                return []
                    params_names = [param[2] for param in i[5]]
                    return params_names

    def buscar_proc_decl(self, dados, semantica = False):
        for i in self.tabelaDeSimbolos:
            if (i[2] == TOKEN_PROC
                and i[4] == dados[5][1]
                and i[0] <= dados[0]
                and i[1] <= dados[1]
            ):
                if (len(i[5]) == len(dados[5][2])):
                    for index, param in enumerate(i[5]):
                        if (i[5][index][1] == 'token609_int'):
                            if not dados[5][2][index].isnumeric():
                                if semantica:
                                    raise Exception(
                                        f'Erro semântico: tipo de parâmentro inválido na linha {self.token_atual().linha}'
                                    )
                                return []
                        elif (i[5][index][1] == 'token611_boolValue'):
                            if (dados[5][2][index] != 'True'
                                and dados[5][2][index] != 'False'):
                                if semantica:
                                    raise Exception(
                                        f'Erro semântico: tipo de parâmentro inválido na linha {self.token_atual().linha}'
                                    )
                                return []
                    params_names = [param[2] for param in i[5]]
                    return params_names

    def buscar_var_decl_atrib(self, dados, var_index, func_context=False):
        tabela = self.tabelaDeSimbolos if not func_context else func_context
        for i in tabela:
            if (i[2] in (TOKEN_INT, TOKEN_BOOL)
                and i[3] == dados[5][var_index]
                and i[0] <= dados[0]
                and i[1] <= dados[1]
            ):
                buscar_atr = [j for j in tabela 
                    if (j[2] == TOKEN_ID
                        and j[3] == dados[5][var_index]
                        and j[0] <= dados[0]
                        and j[1] < dados[1]
                    )]
                if buscar_atr:
                    return i

    def buscar_var_decl(self, dados, func_context=False, func_params=False):
        context = []
        if func_context:
            if not func_params:
                func_params = []
            context = [param for param in func_params]
            for token in func_context:
                context.append(token)
        tabela = self.tabelaDeSimbolos if not context else context
        for i in tabela:
            if (i[2] in (TOKEN_INT, TOKEN_BOOL)
                and i[3] == dados[3]
                and i[0] <= dados[0]
                and i[1] < dados[1]
            ):
                return i

    def call_buscar_var_decl(self, dados, var):
        tabela = self.tabelaDeSimbolos
        for i in tabela:
            if (i[2] in (TOKEN_INT, TOKEN_BOOL)
                and i[3] == var
                and i[0] <= dados[0]
                and i[1] <= dados[1]
            ):
                buscar_atr = [j for j in tabela 
                    if (j[2] == TOKEN_ID
                        and j[3] == var
                        and j[0] <= dados[0]
                        and j[1] < dados[1]
                    )]
                if buscar_atr:
                    return i


    def buscar_var_decl_atrib_return(self, dados, func_context=False, func_params=False):
        context = [param for param in func_params]
        for token in func_context:
            context.append(token)
        if context:
            for i in context:
                if (i[2] in (TOKEN_INT, TOKEN_BOOL)
                    and i[3] == dados[7][3][0]
                    and i[0] <= dados[7][0]
                    and i[1] <= dados[7][1]
                ):
                    buscar_atr = [j for j in context 
                        if (j[2] == TOKEN_ID
                            and j[3] == dados[7][3][0]
                            and j[0] <= dados[7][0]
                            and j[1] < dados[7][1]
                        )]
                    if buscar_atr:
                        return i

    def buscar_var_decl_atrib_params(self, dados, param_index, func_context=False):
        for i in func_context:
            if (i[2] in (TOKEN_INT, TOKEN_BOOL)
                and i[3] == dados[5][param_index][2]
                and i[0] <= dados[0]
                and i[1] <= dados[1]
            ):
                buscar_atr = [j for j in func_context
                    if (j[2] == TOKEN_ID
                        and j[3] == dados[5][param_index][2]
                        and j[0] <= dados[0]
                        and j[1] < dados[1]
                    )]
                if buscar_atr:
                    return i

    def salvar_while_tres_enderecos(self, dados):
        self.tabelaDeTresEnderecos.append((
            f'temp{self.tempAtualTresEnd}: if {dados[3][0]} {self.inverter_relacional(dados[3][1])} {dados[3][2]}'
            + f' goto temp{self.tempAtualTresEnd+1}'
        ))

        while_name = self.tempAtualTresEnd
        self.tempAtualTresEnd += 1
        endwhile_name = self.tempAtualTresEnd

        for i in dados[4]:
            if (i[2] == TOKEN_ID
                or i[2] == TOKEN_TRUEFALSE
                or i[2] == TOKEN_NUM):
                self.salvar_variaveis_tres_endereco(i)
            elif (i[2] == TOKEN_WHILE):
                self.salvar_while_tres_enderecos(i)
            elif (i[2] == TOKEN_BREAK):
                self.tabelaDeTresEnderecos.append(
                    f'goto temp{endwhile_name}'
                )
            elif (i[2] == TOKEN_CONTINUE):
                 self.tabelaDeTresEnderecos.append(
                    f'goto temp{while_name}'
                )
            else:
                self.tempAtualTresEnd += 1
                self.salvar_if_tres_enderecos(i, is_while=True, whilename=while_name, endwhilename=endwhile_name)

        self.tabelaDeTresEnderecos.append(
            f'goto temp{while_name}'
        )
        self.tempAtualTresEnd += 1

        self.tabelaDeTresEnderecos.append(
            f'temp{endwhile_name}:'
        )

    def salvar_call_proc_tres_enderecos(self, dados):
        for param in dados[4]:
            self.tabelaDeTresEnderecos.append(
                f'param {param}'
            )
            
        self.tabelaDeTresEnderecos.append(
            f'call {dados[3]}, {len(dados[4])}'
        )

    def salvar_if_tres_enderecos(self, dados, is_while=False, whilename=False, endwhilename = False):
        self.tabelaDeTresEnderecos.append((
            f'temp{self.tempAtualTresEnd}: if {dados[3][0]} {self.inverter_relacional(dados[3][1])} {dados[3][2]}'
            + f' goto temp{self.tempAtualTresEnd+1}'
        ))
        self.tempAtualTresEnd += 1

        if_name = self.tempAtualTresEnd
        for i in dados[4]:
            if (i[2] == TOKEN_ID
                or i[2] == TOKEN_TRUEFALSE
                or i[2] == TOKEN_NUM):
                self.salvar_variaveis_tres_endereco(i)
            elif (i[2] == TOKEN_WHILE):
                self.salvar_while_tres_enderecos(i)
            elif (is_while and i[2] == TOKEN_BREAK):
                self.tabelaDeTresEnderecos.append(
                    f'goto temp{endwhilename}'
                )
            elif (is_while and i[2] == TOKEN_CONTINUE):
                 self.tabelaDeTresEnderecos.append(
                    f'goto temp{whilename}'
                )
            else:
                self.tempAtualTresEnd += 1
                self.salvar_if_tres_enderecos(i)

        self.tabelaDeTresEnderecos.append(
            f'temp{if_name}:'
        )
        self.tempAtualTresEnd += 1

    def salvar_variaveis_tres_endereco(self, dados):
        if(len(dados[5]) > 1):
            if(len(dados[5]) == 3):
                if dados[5][0] != 'token604_call':
                    self.tabelaDeTresEnderecos.append((dados[3]+ ' := ' + dados[5][0] + dados[5][1] + dados[5][2]))
                    self.tempAtualTresEnd += 1
                else:
                    n_params = len(dados[5][2])
                    func_declaration = self.buscar_func_decl(dados)
                    if not func_declaration:
                        # raise Exception(
                        #     f'Erro semântico: Chamada de função não declarada na linha {self.token_atual().linha}'
                        # )
                        func_declaration = []
                    for func_param in func_declaration:
                        self.tabelaDeTresEnderecos.append(f'param {func_param}')
                    self.tabelaDeTresEnderecos.append((dados[3] + ' := call ' + dados[5][1] + ',' + str(n_params)))
            else:
                lista = dados[5][::-1]
                contador = 0    
                self.tabelaDeTresEnderecos.append(("temp"+str(self.tempAtualTresEnd) + " := " + lista[contador+2] + lista[contador+1] + lista[contador]))
                contador += 3
                self.tempAtualTresEnd += 1
                if(contador < len(lista)):
                    self.salvarValores(lista, contador)
                self.tabelaDeTresEnderecos.append((dados[3] + ' := ' + "temp"+str(self.tempAtualTresEnd-1)))
        else:
            self.tabelaDeTresEnderecos.append((dados[3] + ' := ' + dados[5][0]))


    def end_var_statement(self, temp):
        tempEndVar = temp[5]
        if self.token_atual().tipo == "token604_call":
            tempEndVar.append(self.token_atual().tipo)
            self.call_func_statement(tempEndVar)
            self.salvar_variaveis_tres_endereco(temp)
            return

        if self.token_atual().tipo == "token611_boolValue":

            if (
                self.token_atual().lexema == "True"
                or self.token_atual().lexema == "False"
            ):
                tempEndVar.append(self.token_atual().lexema)
                self.indexDaTabelaDeTokens += 1
                self.salvar_variaveis_tres_endereco(temp)
                return
            else:
                raise Exception(
                    "Erro sintatico: token611_boolValue atribuido erroneamente na linha "
                    + str(self.token_atual().linha)
                )
        if self.token_atual().tipo == "token300_Num":
            tempEndVar.append(self.token_atual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                self.token_atual().tipo == "token101_+"
                or self.token_atual().tipo == "token102_-"
                or self.token_atual().tipo == "token103_*"
                or self.token_atual().tipo == "token104_/"
            ):
                tempEndVar.append(self.token_atual().lexema)
                self.call_op_statement(tempEndVar)
                self.salvar_variaveis_tres_endereco(temp)
            elif self.token_atual().tipo == TOKEN_PONTOVIRGULA:
                self.salvar_variaveis_tres_endereco(temp)
            return

        if self.token_atual().tipo == "token500_Id":
            tempEndVar.append(self.token_atual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                self.token_atual().tipo == "token101_+"
                or self.token_atual().tipo == "token102_-"
                or self.token_atual().tipo == "token103_*"
                or self.token_atual().tipo == "token104_/"
            ):
                tempEndVar.append(self.token_atual().lexema)
                self.call_op_statement(tempEndVar)
                self.salvar_variaveis_tres_endereco(temp)
                return
            elif self.token_atual().tipo == TOKEN_PONTOVIRGULA:
                self.salvar_variaveis_tres_endereco(temp)
                return
        else:
            raise Exception(
                "Erro sintatico: atribuição de variavel inválida na linha "
                + str(self.token_atual().linha)
            )


    def call_var_statement(self, temp, context = False):
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token111_=":  
            temp.append(self.token_atual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                (self.token_atual().tipo == "token300_Num")
                or (self.token_atual().tipo == "token611_boolValue")
                or (self.token_atual().tipo == "token500_Id")
            ):
                temp.append(self.token_atual().lexema)
                self.indexDaTabelaDeTokens += 1
                if self.token_atual().tipo == "token200_;": # Adicionar operação aritmetica aqui
                    self.indexDaTabelaDeTokens += 1
                    if not context:
                        self.tabelaDeSimbolos.append(temp)
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e vírgula na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: variável não atribuída na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: símbolo de atribuição não encontrado na linha "
                + str(self.token_atual().linha)
            )


    def declaration_func_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token609_int" or self.token_atual().tipo == "token610_bool":  
            temp.append(self.token_atual().tipo)
            self.indexDaTabelaDeTokens += 1
  
            if self.token_atual().tipo == "token500_Id":
        
                temp.append(self.token_atual().lexema)
                self.indexDaTabelaDeTokens += 1
                if self.token_atual().tipo == "token202_(":

                    tempParenteses = []
                    self.indexDaTabelaDeTokens += 1
                    if (
                        self.token_atual().tipo == "token609_int"
                        or self.token_atual().tipo == "token610_bool"
                    ):
                        tempParentesesParamAtual = []

                        tempParentesesParamAtual.append(
                            self.indexEscopoAtual + 1)

  
                        tempParentesesParamAtual.append(self.token_atual().tipo)

                        self.indexDaTabelaDeTokens += 1
                        if self.token_atual().tipo == "token500_Id":
                   
                            tempParentesesParamAtual.append(
                                self.token_atual().lexema)
        
                            tempParenteses.append(tempParentesesParamAtual)
                 
                            self.indexDaTabelaDeTokens += 1
                            if self.token_atual().tipo == "token201_,":
                    
                                self.params_statement(tempParenteses)  
                                temp.append(tempParenteses)
                                if self.token_atual().tipo == "token203_)":
                                    self.indexDaTabelaDeTokens += 1

             
                                    nomeDaFuncao = temp[4]
                                    paramsDaFuncao = temp[5]

                                    self.tabelaDeTresEnderecos.append(
                                        f'{nomeDaFuncao}:')
                                    self.tabelaDeTresEnderecos.append(
                                        f'BeginFunc'
                                    )

                                    if self.token_atual().tipo == "token204_{":
                            
                                        self.indexEscopoAntesDaFuncao = (
                                            self.indexEscopoAtual
                                        )
                                        self.indexEscopoAtual += 1
                                        self.indexDaTabelaDeTokens += 1

                                        tempBlock = []
                         
                                        while self.token_atual().tipo != "token603_return":
                                            tempBlock.append(
                                                self.block_statement(context=True))

                                        temp.append(tempBlock)
                                        tempReturn = []
                                        if self.token_atual().tipo == "token603_return":
                                            tempReturn.append(
                                                self.indexEscopoAtual)
                                            tempReturn.append(
                                                self.token_atual().linha
                                            )
                                            tempReturn.append(
                                                self.token_atual().tipo)
                         
                                            tempReturnParams = []
                                            tempReturnParams = self.return_statement(
                                                tempReturnParams
                                            )
                                            tempReturn.append(tempReturnParams)
                                            temp.append(tempReturn)

                                            if (len(tempReturn[3]) > 1):
                                                if (len(tempReturn[3]) == 3):
                                                    if tempReturn[3][0][0] != 'token604_call':
                                                        self.tabelaDeTresEnderecos.append(('return := ' + tempReturn[2][0][0] + tempReturn[2][0][1] + tempReturn[2][0][2]))
                                                    else:
                                                        raise Exception(
                                                            f'Erro semântico: Chamada de função não suportada no retorno {self.token_atual().linha}'
                                                        )
                                                else:
                                                    lista = tempReturn[3][::-1]
                                                    contador = 0    
                                                    self.tabelaDeTresEnderecos.append(("temp"+str(self.tempAtualTresEnd) + " := " + lista[contador+2] + lista[contador+1] + lista[contador]))
                                                    contador += 3
                                                    self.tempAtualTresEnd += 1
                                                    if(contador < len(lista)):
                                                        self.salvarValores(lista, contador)
                                                    self.tabelaDeTresEnderecos.append(('return := ' + "temp"+str(self.tempAtualTresEnd-1)))
                                            else:
                                                self.tabelaDeTresEnderecos.append(('return := ' + tempReturn[3][0][0]))
                                            if self.token_atual().tipo == "token205_}":
                                                self.tabelaDeTresEnderecos.append(('EndFunc'))
                                                self.indexEscopoAtual = (
                                                    self.indexEscopoAntesDaFuncao
                                                )
                                                self.indexDaTabelaDeTokens += 1

                                                if (
                                                    self.token_atual().tipo
                                                    == "token200_;"
                                                ):
                                                    self.indexDaTabelaDeTokens += 1
                                                    self.tabelaDeSimbolos.append(temp)
                                                else:
                                                    raise Exception(
                                                        "Erro sintatico: falta do ponto e vírgula na linha "
                                                        + str(self.token_atual().linha)
                                                    )
                                            else:
                                                raise Exception(
                                                    "Erro sintatico: falta da chave direita na linha "
                                                    + str(self.token_atual().linha)
                                                )
                                        else:
                                            raise Exception(
                                                "Erro sintatico: falta do retorno na linha "
                                                + str(self.token_atual().linha)
                                            )

                                    else:
                                        raise Exception(
                                            "Erro sintatico: falta da chave esquerda na linha "
                                            + str(self.token_atual().linha)
                                        )
                                else:
                                    raise Exception(
                                        "Erro sintatico: falta do parentese direito na linha "
                                        + str(self.token_atual().linha)
                                    )

                            elif self.token_atual().tipo == "token203_)":

                                temp.append(tempParenteses)
                                if self.token_atual().tipo == "token203_)":
                                    self.indexDaTabelaDeTokens += 1
                                    if self.token_atual().tipo == "token204_{":
                                        self.indexEscopoAntesDaFuncao = (
                                            self.indexEscopoAtual
                                        )
                                        self.indexEscopoAtual += 1
                                        self.indexDaTabelaDeTokens += 1
                                        tempBlock = []
                                        while self.token_atual().tipo != "token603_return":
                                            tempBlock.append(
                                                self.block_statement())

                                        temp.append(tempBlock)
                                        tempReturn = []
                                        if self.token_atual().tipo == "token603_return":
                                            tempReturn.append(
                                                self.indexEscopoAtual)
                                            tempReturn.append(
                                                self.token_atual().tipo)
                                            tempReturnParms = []
                                            tempReturnParms = self.return_statement(
                                                tempReturnParms
                                            )
                                            tempReturn.append(tempReturnParms)
                                            temp.append(tempReturn)
                                            if self.token_atual().tipo == "token205_}":
                                                self.indexEscopoAtual = (
                                                    self.indexEscopoAntesDaFuncao
                                                )
                                                self.indexDaTabelaDeTokens += 1
                                                if (
                                                    self.token_atual().tipo
                                                    == "token200_;"
                                                ):
                                                    self.indexDaTabelaDeTokens += 1
                                                    self.tabelaDeSimbolos.append(
                                                        temp)
                                                else:
                                                    raise Exception(
                                                        "Erro sintatico: falta do ponto e vírgula na linha "
                                                        + str(self.token_atual().linha)
                                                    )
                                            else:
                                                raise Exception(
                                                    "Erro sintatico: falta da chave direita na linha "
                                                    + str(self.token_atual().linha)
                                                )
                                        else:
                                            raise Exception(
                                                "Erro sintatico: falta do retorno na linha "
                                                + str(self.token_atual().linha)
                                            )
                                    else:
                                        raise Exception(
                                            "Erro sintatico: falta da chave esquerda na linha "
                                            + str(self.token_atual().linha)
                                        )
                                else:
                                    raise Exception(
                                        "Erro sintatico: falta do parentese direito na linha "
                                        + str(self.token_atual().linha)
                                    )
                            else:
                           
                                raise Exception(
                                    "Erro sintatico: falta da virgula na linha "
                                    + str(self.token_atual().linha)
                                )
                        else:
                            raise Exception(
                                "Erro sintatico: falta o token500_Id na linha "
                                + str(self.token_atual().linha)
                            )

                    else:
                        if self.token_atual().tipo == "token203_)":
                            temp.append(tempParenteses)
                            self.indexDaTabelaDeTokens += 1

                            # exit(0)

                            # nomeDaFuncao = temp[4]
                            # paramsDaFuncao = temp[5]

                            # self.tabelaDeTresEnderecos.append(
                            #     ('label', nomeDaFuncao, 'null'))

                            # for param in paramsDaFuncao:
                            #     self.tabelaDeTresEnderecos.append(
                            #         ('pop', param[2], 'null'))

                            # self.tabelaDeTresEnderecos.append(
                            #     ('push', self.tempTresEnderecos, 'null'))
                            # self.tabelaDeTresEnderecos.append(
                            #     ('ret', 'null', 'null'))

                            if self.token_atual().tipo == "token204_{":
                                self.indexEscopoAntesDaFuncao = self.indexEscopoAtual
                                self.indexEscopoAtual += 1
                                self.indexDaTabelaDeTokens += 1

                                tempBlock = []
              
                                while self.token_atual().tipo != "token603_return":
                                    tempBlock.append(self.block_statement())

                                temp.append(tempBlock)

                                tempReturn = []
                    
                                if self.token_atual().tipo == "token603_return":
                                    tempReturn.append(self.indexEscopoAtual)
                                    tempReturn.append(self.token_atual().tipo)
                          
                                    tempReturnParms = []
                                    tempReturnParms = self.return_statement(
                                        tempReturnParms
                                    )

                                    tempReturn.append(tempReturnParms)
                                    temp.append(tempReturn)
                                    if self.token_atual().tipo == "token205_}":
                                        self.indexEscopoAtual = (
                                            self.indexEscopoAntesDaFuncao
                                        )
                                        self.indexDaTabelaDeTokens += 1
                                        if self.token_atual().tipo == "token200_;":
                                            self.indexDaTabelaDeTokens += 1
                            
                                            self.tabelaDeSimbolos.append(temp)
                                        else:
                                            raise Exception(
                                                "Erro sintatico: falta do ponto e vírgula na linha "
                                                + str(self.token_atual().linha)
                                            )
                                    else:
                                        raise Exception(
                                            "Erro sintatico: falta da chave direita na linha "
                                            + str(self.token_atual().linha)
                                        )
                                else:
                                    raise Exception(
                                        "Erro sintatico: falta do retorno na linha "
                                        + str(self.token_atual().linha)
                                    )

                            else:
                                raise Exception(
                                    "Erro sintatico: falta da chave esquerda na linha "
                                    + str(self.token_atual().linha)
                                )
                        else:
                            raise Exception(
                                "Erro sintatico: falta do parentese direito na linha "
                                + str(self.token_atual().linha)
                            )
                else:
                    raise Exception(
                        "Erro sintatico: falta do parentese esquerdo na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do token500_Id na linha "
                    + str(self.token_atual().linha)
                )


    def return_statement(self, tempReturnParams):
        self.indexDaTabelaDeTokens += 1

  
        if self.token_atual().tipo == "token604_call":
            tempReturnParams.append(self.token_atual().tipo)
            self.indexDaTabelaDeTokens += 1
            if self.token_atual().tipo == "token602_func":
                tempReturnParams.append(self.token_atual().tipo)
                self.call_func_statement(tempReturnParams)
                self.indexDaTabelaDeTokens += 1
                return tempReturnParams
            else:
                raise Exception(
                    "Erro sintatico: Erro de chamada, só é permitido chamada de funções na linha "
                    + str(self.token_atual().linha)
                )


        if (
            (self.token_atual().tipo == "token300_Num")
            or (self.token_atual().tipo == "token611_boolValue")
            or (self.token_atual().tipo == "token500_Id")
        ):
            tempReturnParams.append(self.token_atual().lexema)
     
            self.tempTresEnderecos = tempReturnParams[0]
            self.indexDaTabelaDeTokens += 1
            if self.token_atual().tipo == "token200_;":
                self.indexDaTabelaDeTokens += 1
                return tempReturnParams
            else:
                raise Exception(
                    "Erro sintatico: falta do ponto e virgula na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: Retorno errado na linha "
                + str(self.token_atual().linha)
            )


    def params_statement(self, tempParenteses):
    
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token609_int" or self.token_atual().tipo == "token610_bool":
            tempParentesesParamAtual = []
            tempParentesesParamAtual.append(self.indexEscopoAtual + 1)
            tempParentesesParamAtual.append(self.token_atual().tipo)
            self.indexDaTabelaDeTokens += 1
            if self.token_atual().tipo == "token500_Id":
                tempParentesesParamAtual.append(self.token_atual().lexema)
                tempParenteses.append(tempParentesesParamAtual)
                self.indexDaTabelaDeTokens += 1
                if self.token_atual().tipo == "token201_,":
                    self.params_statement(tempParenteses)
                elif (
                    self.token_atual().tipo == "token609_int" or self.token_atual().tipo == "token610_bool"
                ):
                    raise Exception(
                        "Erro sintatico: falta vírgula na linha "
                        + str(self.token_atual().linha)
                    )
                else:
                    return tempParenteses
            else:
                raise Exception(
                    "Erro sintatico: é necessário informar alguma váriavel na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: é necessário informar um tipo na linha "
                + str(self.token_atual().linha)
            )


    def declaration_proc_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == TOKEN_ID:
            temp.append('void')
            temp.append(self.token_atual().lexema)
            self.indexDaTabelaDeTokens += 1

            if self.token_atual().tipo == "token202_(":

                tempParenteses = []
                self.indexDaTabelaDeTokens += 1
                if (
                    self.token_atual().tipo == "token609_int"
                    or self.token_atual().tipo == "token610_bool"
                ):
                    tempParentesesParamAtual = []

                    tempParentesesParamAtual.append(
                        self.indexEscopoAtual + 1)


                    tempParentesesParamAtual.append(self.token_atual().tipo)

                    self.indexDaTabelaDeTokens += 1
                    if self.token_atual().tipo == "token500_Id":
                
                        tempParentesesParamAtual.append(
                            self.token_atual().lexema)
    
                        tempParenteses.append(tempParentesesParamAtual)
                
                        self.indexDaTabelaDeTokens += 1
                        if self.token_atual().tipo == "token201_,":
                
                            self.params_statement(tempParenteses)  
                            temp.append(tempParenteses)
                            if self.token_atual().tipo == "token203_)":
                                self.indexDaTabelaDeTokens += 1

            
                                nomeDaFuncao = temp[4]
                                paramsDaFuncao = temp[5]

                                self.tabelaDeTresEnderecos.append(
                                    f'{nomeDaFuncao}:')
                                self.tabelaDeTresEnderecos.append(
                                    f'BeginFunc'
                                )

                                if self.token_atual().tipo == "token204_{":
                        
                                    self.indexEscopoAntesDaFuncao = (
                                        self.indexEscopoAtual
                                    )
                                    self.indexEscopoAtual += 1
                                    self.indexDaTabelaDeTokens += 1

                                    tempBlock = []
                        
                                    while self.token_atual().tipo != TOKEN_FECHA_CHAVES:
                                        tempBlock.append(
                                            self.block_statement(context=True))

                                    temp.append(tempBlock)
                                    if self.token_atual().tipo == "token205_}":
                                        self.tabelaDeTresEnderecos.append(('EndFunc'))
                                        self.indexEscopoAtual = (
                                            self.indexEscopoAntesDaFuncao
                                        )
                                        self.indexDaTabelaDeTokens += 1

                                        if (
                                            self.token_atual().tipo
                                            == "token200_;"
                                        ):
                                            self.indexDaTabelaDeTokens += 1
                                            self.tabelaDeSimbolos.append(temp)
                                        else:
                                            raise Exception(
                                                "Erro sintatico: falta do ponto e vírgula na linha "
                                                + str(self.token_atual().linha)
                                            )
                                    else:
                                        raise Exception(
                                            "Erro sintatico: falta da chave direita na linha "
                                            + str(self.token_atual().linha)
                                        )

                                else:
                                    raise Exception(
                                        "Erro sintatico: falta da chave esquerda na linha "
                                        + str(self.token_atual().linha)
                                    )
                            else:
                                raise Exception(
                                    "Erro sintatico: falta do parentese direito na linha "
                                    + str(self.token_atual().linha)
                                )

                        elif self.token_atual().tipo == "token203_)":

                            temp.append(tempParenteses)
                            if self.token_atual().tipo == "token203_)":
                                self.indexDaTabelaDeTokens += 1
                                if self.token_atual().tipo == "token204_{":
                                    self.indexEscopoAntesDaFuncao = (
                                        self.indexEscopoAtual
                                    )
                                    self.indexEscopoAtual += 1
                                    self.indexDaTabelaDeTokens += 1
                                    tempBlock = []
                                    while self.token_atual().tipo != "token603_return":
                                        tempBlock.append(
                                            self.block_statement())

                                    temp.append(tempBlock)
                                    tempReturn = []
                                    if self.token_atual().tipo == "token603_return":
                                        tempReturn.append(
                                            self.indexEscopoAtual)
                                        tempReturn.append(
                                            self.token_atual().tipo)
                                        tempReturnParms = []
                                        tempReturnParms = self.return_statement(
                                            tempReturnParms
                                        )
                                        tempReturn.append(tempReturnParms)
                                        temp.append(tempReturn)
                                        if self.token_atual().tipo == "token205_}":
                                            self.indexEscopoAtual = (
                                                self.indexEscopoAntesDaFuncao
                                            )
                                            self.indexDaTabelaDeTokens += 1
                                            if (
                                                self.token_atual().tipo
                                                == "token200_;"
                                            ):
                                                self.indexDaTabelaDeTokens += 1
                                                self.tabelaDeSimbolos.append(
                                                    temp)
                                            else:
                                                raise Exception(
                                                    "Erro sintatico: falta do ponto e vírgula na linha "
                                                    + str(self.token_atual().linha)
                                                )
                                        else:
                                            raise Exception(
                                                "Erro sintatico: falta da chave direita na linha "
                                                + str(self.token_atual().linha)
                                            )
                                    else:
                                        raise Exception(
                                            "Erro sintatico: falta do retorno na linha "
                                            + str(self.token_atual().linha)
                                        )
                                else:
                                    raise Exception(
                                        "Erro sintatico: falta da chave esquerda na linha "
                                        + str(self.token_atual().linha)
                                    )
                            else:
                                raise Exception(
                                    "Erro sintatico: falta do parentese direito na linha "
                                    + str(self.token_atual().linha)
                                )
                        else:
                        
                            raise Exception(
                                "Erro sintatico: falta da virgula na linha "
                                + str(self.token_atual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sintatico: falta o token500_Id na linha "
                            + str(self.token_atual().linha)
                        )

                else:
                    if self.token_atual().tipo == "token203_)":
                        temp.append(tempParenteses)
                        self.indexDaTabelaDeTokens += 1

                        # exit(0)

                        # nomeDaFuncao = temp[4]
                        # paramsDaFuncao = temp[5]

                        # self.tabelaDeTresEnderecos.append(
                        #     ('label', nomeDaFuncao, 'null'))

                        # for param in paramsDaFuncao:
                        #     self.tabelaDeTresEnderecos.append(
                        #         ('pop', param[2], 'null'))

                        # self.tabelaDeTresEnderecos.append(
                        #     ('push', self.tempTresEnderecos, 'null'))
                        # self.tabelaDeTresEnderecos.append(
                        #     ('ret', 'null', 'null'))

                        if self.token_atual().tipo == "token204_{":
                            self.indexEscopoAntesDaFuncao = self.indexEscopoAtual
                            self.indexEscopoAtual += 1
                            self.indexDaTabelaDeTokens += 1

                            tempBlock = []
            
                            while self.token_atual().tipo != "token603_return":
                                tempBlock.append(self.block_statement())

                            temp.append(tempBlock)

                            tempReturn = []
                
                            if self.token_atual().tipo == "token603_return":
                                tempReturn.append(self.indexEscopoAtual)
                                tempReturn.append(self.token_atual().tipo)
                        
                                tempReturnParms = []
                                tempReturnParms = self.return_statement(
                                    tempReturnParms
                                )

                                tempReturn.append(tempReturnParms)
                                temp.append(tempReturn)
                                if self.token_atual().tipo == "token205_}":
                                    self.indexEscopoAtual = (
                                        self.indexEscopoAntesDaFuncao
                                    )
                                    self.indexDaTabelaDeTokens += 1
                                    if self.token_atual().tipo == "token200_;":
                                        self.indexDaTabelaDeTokens += 1
                        
                                        self.tabelaDeSimbolos.append(temp)
                                    else:
                                        raise Exception(
                                            "Erro sintatico: falta do ponto e vírgula na linha "
                                            + str(self.token_atual().linha)
                                        )
                                else:
                                    raise Exception(
                                        "Erro sintatico: falta da chave direita na linha "
                                        + str(self.token_atual().linha)
                                    )
                            else:
                                raise Exception(
                                    "Erro sintatico: falta do retorno na linha "
                                    + str(self.token_atual().linha)
                                )

                        else:
                            raise Exception(
                                "Erro sintatico: falta da chave esquerda na linha "
                                + str(self.token_atual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sintatico: falta do parentese direito na linha "
                            + str(self.token_atual().linha)
                        )
            else:
                raise Exception(
                    "Erro sintatico: falta do parentese esquerdo na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sintático: Nome do procedimento não definido na linha " +
                str(self.token_atual().linha)
            )

    def call_proc_statement(self, temp):
        if self.token_atual().tipo == "token500_Id":
            temp.append(self.token_atual().lexema)
            self.indexDaTabelaDeTokens += 1
            if self.token_atual().tipo == "token202_(":
                self.indexDaTabelaDeTokens += 1
                tempParams = []
                if (
                    self.token_atual().tipo == "token500_Id"
                    or self.token_atual().lexema == "True"
                    or self.token_atual().lexema == "False"
                    or self.token_atual().tipo == TOKEN_NUM
                ):
                    tempParams.append(self.token_atual().lexema)
                    self.indexDaTabelaDeTokens += 1
                    if self.token_atual().tipo == "token201_,":
                        tempParams.append(
                            self.params_call_statement(tempParams))
                        tempParams.pop()
                        temp.append(tempParams)

                        if self.token_atual().tipo == "token203_)":
                            self.indexDaTabelaDeTokens += 1
                            return temp

                    elif self.token_atual().tipo == "token203_)":
                        self.indexDaTabelaDeTokens += 1
                        temp.append(tempParams)
                        return temp
                    else:
                        raise Exception(
                            "Erro sintatico: falta da virgula na linha "
                            + str(self.token_atual().linha)
                        )
                else:
                    temp.append(tempParams)
                    if self.token_atual().tipo == "token203_)":

                        self.indexDaTabelaDeTokens += 1
                        return temp
                    else:
                        raise Exception(
                            "Erro sintatico: falta do parentese direito na linha "
                            + str(self.token_atual().linha)
                        )
            else:
                raise Exception(
                    "Erro sintatico: falta do parentese esquerdo na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do token500_Id na linha " +
                str(self.token_atual().linha)
            )


    def call_func_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token500_Id":
            temp.append(self.token_atual().lexema)
            self.indexDaTabelaDeTokens += 1
            if self.token_atual().tipo == "token202_(":
                self.indexDaTabelaDeTokens += 1
                tempParams = []
                if (
                    self.token_atual().tipo == "token500_Id"
                    or self.token_atual().lexema == "True"
                    or self.token_atual().lexema == "False"
                    or self.token_atual().tipo == "token300_Num"
                ):
                    tempParams.append(self.token_atual().lexema)
                    self.indexDaTabelaDeTokens += 1
                    if self.token_atual().tipo == "token201_,":
                        tempParams.append(
                            self.params_call_statement(tempParams))
                        tempParams.pop()
                        if self.token_atual().tipo == "token203_)":
                            self.indexDaTabelaDeTokens += 1
                            temp.append(tempParams)
                            return temp
                        else:
                            raise Exception(
                                "Erro sintatico: falta do parentese direito na linha "
                                + str(self.token_atual().linha)
                            )
                    elif self.token_atual().tipo == "token203_)":
                        self.indexDaTabelaDeTokens += 1
                        temp.append(tempParams)
                        return temp
                    else:
                        raise Exception(
                            "Erro sintatico: falta do parentese direito na linha "
                            + str(self.token_atual().linha)
                        )

                else:
                    temp.append(tempParams)
                    if self.token_atual().tipo == "token203_)":
                        self.indexDaTabelaDeTokens += 1

                        return temp
                    else:
                        raise Exception(
                            "Erro sintatico: falta do parentese direito na linha "
                            + str(self.token_atual().linha)
                        )
            else:
                raise Exception(
                    "Erro sintatico: falta do parentese esquerdo na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta o nome da função na linha " +
                str(self.token_atual().linha)
            )

    def params_call_statement(self, tempParams):
        self.indexDaTabelaDeTokens += 1
        if (
            self.token_atual().tipo == "token500_Id"
            or self.token_atual().lexema == "True"
            or self.token_atual().lexema == "False"
            or self.token_atual().tipo == "token300_Num"
        ):
            tempParams.append(self.token_atual().lexema)
            self.indexDaTabelaDeTokens += 1
            if self.token_atual().tipo == "token201_,":
                self.params_call_statement(tempParams)
            elif (
                self.token_atual().tipo == "token500_Id"
                or self.token_atual().lexema == "True"
                or self.token_atual().lexema == "False"
                or self.token_atual().tipo == "token300_Num"
            ):
                raise Exception(
                    "Erro sintatico: falta vírgula na linha "
                    + str(self.token_atual().linha)
                )
            else:

                return tempParams
        else:
            raise Exception(
                "Erro sintatico: é necessário informar alguma váriavel na linha "
                + str(self.token_atual().linha)
            )


    def print_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token202_(":
            tempParams = []
            temp.append(self.params_print_statement(tempParams))


            self.tabelaDeTresEnderecos.append(
                ('print', self.tempTresEnderecos, 'null'))
            if self.token_atual().tipo == "token203_)":
                self.indexDaTabelaDeTokens += 1
                if self.token_atual().tipo == "token200_;":
                    self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return
                else:

                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do Parentese direito na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do Parentese esquerdo na linha  "
                + str(self.token_atual().linha)
            )


    def params_print_statement(self, tempParams):
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token604_call":
            tempParams.append(self.token_atual().tipo)
            self.indexDaTabelaDeTokens += 1
            if self.token_atual().tipo == "token602_func":
                tempParams.append(self.token_atual().tipo)
                tempParams = self.call_func_statement(tempParams)
                return tempParams
            elif self.token_atual().tipo == "token615_proc":
                raise Exception(
                    "Erro sintatico: Procedimento não tem retorno na linha "
                    + str(self.token_atual().linha)
                )
            else:
                raise Exception(
                    "Erro sintatico: chamada incorreta de função na linha "
                    + str(self.token_atual().linha)
                )

        elif (
            (self.token_atual().tipo == "token300_Num")
            or (self.token_atual().tipo == "token611_boolValue")
            or (self.token_atual().tipo == "token500_Id")
        ):
            tempParams.append(self.token_atual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                self.token_atual().tipo == "token101_+"
                or self.token_atual().tipo == "token102_-"
                or self.token_atual().tipo == "token103_*"
                or self.token_atual().tipo == "token104_/"
            ):
                tempParams.append(self.token_atual().lexema)
                self.call_op_statement(tempParams)
                return tempParams
            else:
                return tempParams
        else:
            raise Exception(
                "Erro sintatico: uso incorreto dos parametros na linha "
                + str(self.token_atual().linha)
            )

    def elsePartStatement(self, tempElse):
    
        lookAhead = self.token_look_ahead()
        self.indexToken += 1
        if self.token_atual().tipo == "token204_{" and lookAhead != "token205_}": 
            self.indexToken += 1
            tempBlock = []
            while(self.token_atual().tipo != "token205_}" and self.tokenLookAhead().tipo != "token606_endelse"):         
                tempBlock.append(self.block_statement(isIf=True))
            if self.token_atual().tipo == "token205_}":
                self.indexToken += 1
                if self.token_atual().tipo == "token606_endelse":  
                    tempElse.append(self.token_atual().tipo)
                    self.indexToken += 1
                    return tempElse
                else:
                    raise Exception(
                        "Erro sintático: falta de endelse na linha "
                        + str(self.token_atual().linha)
                        )
            else:
                raise Exception(
                    "Erro sintático: falta do } na linha "
                    + str(self.token_atual().linha)
                )      
        else:
            raise Exception(
                "Erro sintático: falta do } ou bloco vazio na linha " +
                str(self.token_atual().linha)
            )   

    def ifStatementWhile(self, temp, is_proc: bool): 
        self.indexToken += 1
        if self.token_atual().tipo == "token202_(":
            self.indexToken += 1
            tempExpression = []
            tempExpression = self.expression_statement(tempExpression)
            temp.append(tempExpression)
        
            if self.token_atual().tipo == "token203_)":
                lookAhead = self.token_look_ahead()
                self.indexToken += 1
                if self.token_atual().tipo == "token204_{" and lookAhead.tipo != "token205_}":
                    self.indexToken +=1
                    self.indexEscopoAtual += 1
                    tempBlock = []
            
                    while(self.token_atual().tipo != "token205_}"
                        and self.tokenLookAhead().tipo != "token605_endif"):
                        if(self.tokenAtual().tipo == "token603_return" and is_proc):
                            raise Exception(
                                "Erro sintático: return declarado dentro de um procedimento na linha "
                                + str(self.tokenAtual().linha)
                            ) 
                        tempBlock.append(self.blockStatement(True, True))
            
                    temp.append(tempBlock)          

                    if self.token_atual().tipo == "token205_}": 
                        self.indexToken += 1
                        if self.token_atual().tipo == "token605_endif":
                            temp.append(self.token_atual().tipo)
                            self.indexToken += 1
                        
                            tempElse = []
                            if self.token_atual().tipo == "token606_else":
                                tempElse.append(self.indexEscopoAtual)
                                tempElse.append(self.token_atual().tipo)
                                tempElse = self.elsePartStatement(tempElse)     
                                
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
                                "Erro sintático: falta de token605_endif "
                                + str(self.token_atual().linha)
                            )
                    else:
                        raise Exception(
                        "Erro sintático: falta do token205_} na linha " +
                        str(self.token_atual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sintático: falta do token204_{ ou bloco vazio na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintático: falta do parêntese direito na linha " + 
                    str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sintático: falta do parêntese esquerdo na linha " +
                str(self.token_atual().linha)
            )

    def if_statement(self, temp, context=False):
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token202_(":
            self.indexDaTabelaDeTokens += 1
            tempExpression = []
            tempExpression = self.expression_statement(tempExpression)
            temp.append(tempExpression)

            if self.token_atual().tipo == "token203_)":
                olhaAfrente = self.token_look_ahead()
                self.indexDaTabelaDeTokens += 1
                if self.token_atual().tipo == "token204_{" and olhaAfrente.tipo != "token205_}":
                    self.indexDaTabelaDeTokens += 1
                    self.indexEscopoAtual += 1
                    tempBlock = []
                    while (
                        self.token_atual().tipo != "token205_}"
                        and self.token_look_ahead().tipo != "token605_endif"
                    ):
                        tempBlock.append(self.block3_statement(context=True))

                    temp.append(tempBlock)
                    if self.token_atual().tipo == "token205_}":
                        self.indexDaTabelaDeTokens += 1
                        if self.token_atual().tipo == "token605_endif":
                            temp.append(self.token_atual().tipo)
                            self.indexDaTabelaDeTokens += 1

                            tempElse = []
                            if self.token_atual().tipo == "token606_else":
                                tempElse.append(self.indexEscopoAtual)
                                tempElse.append(self.token_atual().tipo)
                                tempElse = self.else_part_statement(
                                    tempElse)  

                                temp.append(tempElse)
                                if not context:
                                    self.tabelaDeSimbolos.append(temp)
                                self.indexEscopoAtual -= 1
                            else:
                                temp.append(tempElse)
                                if not context:
                                    self.tabelaDeSimbolos.append(temp)
                                self.indexEscopoAtual -= 1
                                return
                        else:
                            raise Exception(
                                "Erro sintatico: falta de token605_endif "
                                + str(self.token_atual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sintatico: falta do token205_} na linha "
                            + str(self.token_atual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sintatico: falta do token204_{ ou bloco vazio na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do Parentese direito na linha  "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do Parentese esquerdo na linha  "
                + str(self.token_atual().linha)
            )


    def else_part_statement(self, tempElse):
        olhaAfrente = self.token_look_ahead()
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token204_{" and olhaAfrente.tipo != "token205_}":
            self.indexDaTabelaDeTokens += 1
            tempBlock = []
            while (
                self.token_atual().tipo != "token205_}"
                and self.token_look_ahead().tipo != "token606_endelse"
            ):
                tempBlock.append(self.block3_statement())
            tempElse.append(tempBlock)
            if self.token_atual().tipo == "token205_}":
                self.indexDaTabelaDeTokens += 1
                if self.token_atual().tipo == "token606_endelse":
                    tempElse.append(self.token_atual().tipo)
                    self.indexDaTabelaDeTokens += 1
                    return tempElse
                else:
                    raise Exception(
                        "Erro sintatico: falta de token606_endelse na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do token205_} na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do token204_{ ou bloco vazio na linha "
                + str(self.token_atual().linha)
            )


    def if_statement2(self, temp, context=False):
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token202_(":
            self.indexDaTabelaDeTokens += 1
            tempExpression = []
            tempExpression = self.expression_statement(tempExpression)
            temp.append(tempExpression)
            if self.token_atual().tipo == "token203_)":
                olhaAfrente = self.token_look_ahead()
                self.indexDaTabelaDeTokens += 1
                if self.token_atual().tipo == "token204_{" and olhaAfrente.tipo != "token205_}":
                    self.indexDaTabelaDeTokens += 1
                    self.indexEscopoAtual += 1
                    tempBlock = []
                    while (
                        self.token_atual().tipo != "token205_}"
                        and self.token_look_ahead().tipo != "token605_endif"
                    ):
                        tempBlock.append(self.block2_statement())
                    temp.append(tempBlock)
                    if self.token_atual().tipo == "token205_}":
                        self.indexDaTabelaDeTokens += 1
                        if self.token_atual().tipo == "token605_endif":
                            temp.append(self.token_atual().tipo)
                            self.indexDaTabelaDeTokens += 1
                            tempElse = []
                            if self.token_atual().tipo == "token606_else":
                                tempElse.append(self.indexEscopoAtual)
                                tempElse.append(self.token_atual().tipo)
                                tempElse = self.else_part_statement2(
                                    tempElse)  

                                temp.append(tempElse)
                                if not context:
                                    self.tabelaDeSimbolos.append(temp)
                                self.indexEscopoAtual -= 1
                            else:
                                temp.append(tempElse)
                                if not context:
                                    self.tabelaDeSimbolos.append(temp)
                                self.indexEscopoAtual -= 1
                                return
                        else:
                            raise Exception(
                                "Erro sintatico: falta de token605_endif "
                                + str(self.token_atual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sintatico: falta do token205_} na linha "
                            + str(self.token_atual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sintatico: falta do token204_{ ou Bloco vazio na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do Parentese direito na linha  "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do Parentese esquerdo na linha  "
                + str(self.token_atual().linha)
            )


    def else_part_statement2(self, tempElse):
        olhaAfrente = self.token_look_ahead()
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token204_{" and olhaAfrente.tipo != "token205_}":
            self.indexDaTabelaDeTokens += 1
            tempBlock = []
            while (
                self.token_atual().tipo != "token205_}"
                and self.token_look_ahead().tipo != "token606_endelse"
            ):
                tempBlock.append(self.block2_statement())
            tempElse.append(tempBlock)
            if self.token_atual().tipo == "token205_}":
                self.indexDaTabelaDeTokens += 1
                if self.token_atual().tipo == "token606_endelse":
                    tempElse.append(self.token_atual().tipo)
                    self.indexDaTabelaDeTokens += 1
                    return tempElse
                else:
                    raise Exception(
                        "Erro sintatico: falta de token606_endelse na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do token205_} na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do token204_{ ou bloco vazio na linha "
                + str(self.token_atual().linha)
            )


    def while_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token202_(":
            self.indexDaTabelaDeTokens += 1
            tempExpression = []
            tempExpression = self.expression_statement(tempExpression)
            temp.append(tempExpression)
            if self.token_atual().tipo == "token203_)":
                self.indexDaTabelaDeTokens += 1
                if self.token_atual().tipo == "token204_{":
                    self.indexDaTabelaDeTokens += 1
                    self.indexEscopoAtual += 1
                    tempBlock = []
                    while (
                        self.token_atual().tipo != "token205_}"
                        and self.token_look_ahead().tipo != "token607_endwhile"
                    ):
                        tempBlock.append(self.block2_statement(context=True))

                    temp.append(tempBlock)

                    if self.token_atual().tipo == "token205_}":
                        self.indexDaTabelaDeTokens += 1
                        if self.token_atual().tipo == "token607_endwhile":
                            temp.append(self.token_atual().tipo)
                            self.indexDaTabelaDeTokens += 1
                            self.tabelaDeSimbolos.append(temp)
                            self.indexEscopoAtual -= 1
                        else:
                            raise Exception(
                                "Erro sintatico: falta de token607_endwhile na linha "
                                + str(self.token_atual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sintatico: falta do token205_} na linha "
                            + str(self.token_atual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sintatico: falta do token204_{ na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do token203_) na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do token202_( na linha "
                + str(self.token_atual().linha)
            )


    def unconditional_branch_statement(self):
        if self.token_atual().tipo == "token614_cont":
            self.indexDaTabelaDeTokens += 1
            if self.token_atual().tipo == "token200_;":
                self.indexDaTabelaDeTokens += 1
            else:
                raise Exception(
                    "Erro sintatico: falta do ponto e virgula na linha "
                    + str(self.token_atual().linha)
                )

        if self.token_atual().tipo == "token613_break":
            self.indexDaTabelaDeTokens += 1
            if self.token_atual().tipo == "token200_;":
                self.indexDaTabelaDeTokens += 1
            else:
                raise Exception(
                    "Erro sintatico: falta do ponto e virgula na linha "
                    + str(self.token_atual().linha)
                )


    def expression_statement(self, tempExpression):
        if self.token_atual().tipo == "token500_Id" or self.token_atual().tipo == "token300_Num":
            tempExpression.append(self.token_atual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                self.token_atual().tipo == "token105_=="
                or self.token_atual().tipo == "token106_!="
                or self.token_atual().tipo == "token110<="
                or self.token_atual().tipo == "token109_<"
                or self.token_atual().tipo == "token108_>="
                or self.token_atual().tipo == "token107_>"
            ):
                tempExpression.append(self.token_atual().lexema)
                self.indexDaTabelaDeTokens += 1
                if self.token_atual().tipo == "token500_Id" or self.token_atual().tipo == "token300_Num":
                    tempExpression.append(self.token_atual().lexema)
                    self.indexDaTabelaDeTokens += 1
                    return tempExpression
                else:
                    raise Exception(
                        "Erro sintatico: falta do token500_Id na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do operador booleano na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do token500_Id na linha " +
                str(self.token_atual().linha)
            )


    def call_op_statement(self, tempEndVar):
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token500_Id" or self.token_atual().tipo == "token300_Num":
            tempEndVar.append(self.token_atual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                self.token_atual().tipo == "token101_+"
                or self.token_atual().tipo == "token102_-"
                or self.token_atual().tipo == "token103_*"
                or self.token_atual().tipo == "token104_/"
            ):
                tempEndVar.append(self.token_atual().lexema)
                self.call_op_statement(tempEndVar)

                # expressaoTratada = arvoreExpressao(tempEndVar)

                # var = expressaoTresEnderecos(expressaoTratada)

                # self.tabelaDeTresEnderecos.extend(var)
            else:
                return
        else:
            raise Exception(
                "Erro sintatico: falta do token500_Id na linha " +
                str(self.token_atual().linha)
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

            elif simbolo == "token615_proc":
                self.declaration_proc_semantico(self.tabelaDeSimbolos[k])

            elif simbolo == "token604_call":
                self.buscar_proc_decl_semantica(self.tabelaDeSimbolos[k])

            elif simbolo == "token609_int" or simbolo == "token610_bool":
                var_decl = self.buscar_var_decl(self.tabelaDeSimbolos[k])
                if var_decl:
                    raise Exception(
                        f'Erro semântico: Variável "{self.tabelaDeSimbolos[k][3]}" já declarada neste escopo, linha '
                        + str(self.tabelaDeSimbolos[k][1])
                    )

            elif simbolo == "token605_if":
                self.expression_semantico(self.tabelaDeSimbolos[k])

            elif simbolo == "token607_while":
                self.expression_semantico(self.tabelaDeSimbolos[k])

            elif simbolo == "token500_Id":
                self.call_var_semantico(self.tabelaDeSimbolos[k])

        print("#============================#\n")
        print("#  FIM DA ANÁLISE SEMÂNTICA  #\n")
        print("#  FINALIZADO SEM PROBLEMAS  #\n")
        print("#============================#\n")

    def check_func_semantica(self, token, func_context, func_params):

            simbolo = token[2]

            if simbolo == "token604_call":
                if token[3] == "token602_func":
                    self.call_func_semantico(
                        token,
                        4,
                        token[0],
                        5,
                        token[1],
                    )
                if token[3] == "token615_proc":
                    self.call_proc_semantico(
                        token, 5, token[1]
                    )

            if simbolo == "token609_int" or simbolo == "token610_bool":
                var_decl = self.buscar_var_decl(token, func_context, func_params)
                if var_decl:
                    raise Exception(
                        f'Erro semântico: Variável "{token[3]}" já declarada neste escopo, linha '
                        + str(token[1])
                    )
                return


            if simbolo == "token605_if":
                self.expression_semantico(token)

            if simbolo == "token607_while":
                self.expression_semantico(token)

            if simbolo == "token500_Id":
                self.call_var_func_semantico(token, func_context, func_params)
        
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
                            self.deriva_atribuicao(
                                self.tabelaDeSimbolos[k], simbolo)
                            break

            # elif self.buscarParamsProc(simbolo) == True:
            #     flag = True
            #     break

            # elif self.buscarParamsFunc(simbolo, 3) == True:
            #     flag = True
            #     break

        if flag == False:
            raise Exception(
                f'Erro Semântico: variável "{simbolo[3]}" não declarada neste escopo, linha: ' +
                str(simbolo[1])
            )

    def call_var_func_semantico(self, simbolo, func_context, func_params):
        context = [param for param in func_params]
        for token in func_context:
            context.append(token)
        flag = False
        for k in range(len(context)):
            if (
                context[k][2] == "token609_int"
                or context[k][2] == "token610_bool"
            ):
                if context[k][3] == simbolo[3]:
       
                    if context[k][0] <= simbolo[0]:
                        if context[k][1] <= simbolo[1]:
                            flag = True  
                            self.deriva_atribuicao(
                                context[k], simbolo, func_context=context)
                            break

            # elif self.buscarParamsProc(simbolo) == True:
            #     flag = True
            #     break

            # elif self.buscarParamsFunc(simbolo, 3) == True:
            #     flag = True
            #     break

        if flag == False:
            raise Exception(
                "Erro Semântico: variável não declarada na linha: " +
                str(simbolo[1])
            )

    def buscarParamsProc(self, simbolo):
        paramsProc = self.buscarNaTabelaDeSimbolos("token615_proc", 2)
        if paramsProc != None:
            paramsProc = paramsProc[5]
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

    def declaration_func_semantico(self, tabelaNoIndiceAtual):
        func_params = [[param[0], tabelaNoIndiceAtual[1], param[1], param[2]] for param in tabelaNoIndiceAtual[5]]
        for param in tabelaNoIndiceAtual[5]:
            check_repetition = [p[2] for p in tabelaNoIndiceAtual[5] if p[2] == param[2]]
            if len(check_repetition) > 1:
                raise Exception(
                    f'Erro semântico: Parâmetro {param[2]} declarado mais de uma vez, linha '
                    + str(tabelaNoIndiceAtual[1])
                )
            func_params.append(
                [param[0], tabelaNoIndiceAtual[1], TOKEN_ID, param[2], '=', []]
            )

        for i in tabelaNoIndiceAtual[6]:
            self.check_func_semantica(i, tabelaNoIndiceAtual[6], func_params)
        if tabelaNoIndiceAtual[3] == "token609_int":
            if len(tabelaNoIndiceAtual[7][3]) != 1:
                raise Exception(
                    'Erro semântico: O retorno só pode conter um valor, operações ou chamada de função deve ser feita em variáveis antes e atribuídas então ao retorno, linha '
                    + str(tabelaNoIndiceAtual[1])
                )
            if not tabelaNoIndiceAtual[7][3][0].isnumeric():
                var_decl = self.buscar_var_decl_atrib_return(tabelaNoIndiceAtual, tabelaNoIndiceAtual[6], func_params)
                if (var_decl[2] != TOKEN_INT):
                    raise Exception(
                        "Erro Semântico: O retorno espera um número inteiro ou uma variável do tipo inteiro na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )

        if tabelaNoIndiceAtual[3] == "token610_bool":
            if (
                tabelaNoIndiceAtual[7][3][0] == "True"
                or tabelaNoIndiceAtual[7][3][0] == "False"
            ) is False:
                raise Exception(
                    "Erro Semântico: O retorno espera um token611_boolValue na linha: "
                    + str(tabelaNoIndiceAtual[1])
                )

    def decl_func_params_semantico(self, tabelaNoIndiceAtual):
        for i, token in enumerate(tabelaNoIndiceAtual[5]):
            var_decl = self.buscar_var_decl_atrib_params(tabelaNoIndiceAtual, i)
            if var_decl:
                raise Exception(
                    f'Erro semântico: Variável de mesmo nome do parâmetro já declarada em escopo exterior, linha '
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
        func_params = [[param[0], tabelaNoIndiceAtual[1], param[1], param[2]] for param in tabelaNoIndiceAtual[5]]
        for param in tabelaNoIndiceAtual[5]:
            check_repetition = [p[2] for p in tabelaNoIndiceAtual[5] if p[2] == param[2]]
            if len(check_repetition) > 1:
                raise Exception(
                    f'Erro semântico: Parâmetro {param[2]} declarado mais de uma vez, linha '
                    + str(tabelaNoIndiceAtual[1])
                )
            func_params.append(
                [param[0], tabelaNoIndiceAtual[1], TOKEN_ID, param[2], '=', []]
            )

        for i in tabelaNoIndiceAtual[6]:
            self.check_func_semantica(i, tabelaNoIndiceAtual[6], func_params)

    def call_proc_semantico(self, tabelaNoIndiceAtual, m, linha):

        flag = False
        for k in range(len(self.tabelaDeSimbolos)):
            if self.tabelaDeSimbolos[k][2] == "token615_proc":
                if self.tabelaDeSimbolos[k][4] == tabelaNoIndiceAtual[3]:
                    if self.tabelaDeSimbolos[k][0] <= tabelaNoIndiceAtual[0]:
                        flag = True
                        self.verificarParams(
                            self.tabelaDeSimbolos[k],
                            tabelaNoIndiceAtual,
                            5,
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

    def salvarValores(self, lista, contador):
        if(contador < len(lista)):
            self.tabelaDeTresEnderecos.append(("temp"+str(self.tempAtualTresEnd)  + " := " "temp"+str(self.tempAtualTresEnd-1) + lista[contador] + lista[contador+1]))
            self.tempAtualTresEnd += 1
            contador += 2
            if(contador < len(lista) + 2):
                self.salvarValores(lista, contador)
    
    def deriva_atribuicao(self, simboloDeclaradoNaTabela, simbolo, func_context=False):
        is_func_call = False
        for i, s in enumerate(simbolo[5]):
            if simboloDeclaradoNaTabela[2] == TOKEN_INT:
                if type(s) is str and not s.isnumeric():
                    if s not in (LEX_SOMA, LEX_SUB, LEX_MULT, LEX_DIV):
                        if s in (LEX_TRUE, LEX_FALSE):
                            raise Exception(
                                f'Erro semântico: Valor "{s}" não pode ser atribuído a variável numérica na linha '
                                + str(simbolo[1])
                            )
                        if s == TOKEN_CALL:
                            is_func_call = True
                            continue
                        if is_func_call:
                            func_decl = self.buscar_func_decl_semantica(simbolo)
                            is_func_call = func_decl
                            if func_decl:
                                if func_decl[3] != TOKEN_INT:
                                    raise Exception(
                                        f'Erro semântico: Retorno da função "{func_decl[4]}" do tipo {func_decl[3]} não pode ser atribuído à variável numérica na linha '
                                        + str(simbolo[1])
                                    )
                            else:
                                raise Exception(
                                    f'Erro semântico: Função "{simbolo[5][1]}" não encontrada neste escopo, linha '
                                    + str(simbolo[1])
                                )
                        else:
                            var_decl = self.buscar_var_decl_atrib(simbolo, i, func_context)
                            if var_decl:
                                if var_decl[2] != TOKEN_INT:
                                    raise Exception(
                                        f'Erro semântico: Variável "{var_decl[3]}" do tipo {var_decl[2]} não pode ser atribuído à variável numérica na linha '
                                        + str(simbolo[1])
                                    )
                                else:
                                    continue
                            elif not var_decl:
                                raise Exception(
                                    f'Erro semântico: Variável "{s}" não declarada neste escopo, linha '
                                    + str(simbolo[1])
                                )
                            else:
                                raise Exception(
                                    f'Erro semântico: Valor "{s}" não pode ser atribuído a variável numérica na linha '
                                    + str(simbolo[1])
                                )
                elif type(s) is list:
                    continue
                    for index, param in enumerate(is_func_call[5]):
                        if param[1] == TOKEN_INT:
                            if not s[index].isnumeric():
                                raise Exception(
                                    f'Erro semântico: Valor {s[index]} não suportado no {index}º parâmetro da função {is_func_call[4]}, linha '
                                    + str(simbolo[i])
                                )
                        elif param[1] == TOKEN_BOOL:
                            if s[index] not in (LEX_TRUE, LEX_FALSE):
                                raise Exception(
                                    f'Erro semântico: Valor {s[index]} não suportado no {index}º parâmetro da função {is_func_call[4]}, linha '
                                    + str(simbolo[i])
                                )
                    is_func_call = False


            elif simboloDeclaradoNaTabela[2] == TOKEN_BOOL:
                if s in (LEX_TRUE, LEX_FALSE):
                    continue
                else:
                    var_decl = self.buscar_var_decl_atrib(simbolo, i, func_context)
                    if s.isnumeric():
                        raise Exception(
                            f'Erro semântico: Valor numérico não pode ser atribuído à variável do tipo booleano, linha '
                            + str(simbolo[1])
                        )
                    if var_decl:
                        if var_decl[2] != TOKEN_BOOL:
                            raise Exception(
                                f'Erro semântico: Variável "{var_decl[3]}" do tipo {var_decl[2]} não pode ser atribuído a variável booleana na linha '
                                + str(simbolo[1])
                            )
                        else:
                            continue
                    elif not var_decl:
                        raise Exception(
                            f'Erro semântico: Variável "{s}" não declarada neste escopo, linha '
                            + str(simbolo[1])
                        )
            pass

    def inverter_relacional(self, relacional):
        if relacional == LEX_IGUAL:
            return LEX_DIFERENTE
        elif relacional == LEX_DIFERENTE:
            return LEX_IGUAL
        elif relacional == LEX_MAIOR:
            return LEX_MENORIGUAL
        elif relacional == LEX_MENOR:
            return LEX_MAIORIGUAL
        elif relacional == LEX_MAIORIGUAL:
            return LEX_MENOR
        elif relacional == LEX_MENORIGUAL:
            return LEX_MAIOR