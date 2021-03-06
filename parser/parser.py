from pprint import pprint
from lexemas import LEX_DIFERENTE, LEX_DIV, LEX_FALSE, LEX_IGUAL, LEX_MAIOR, LEX_MAIORIGUAL, LEX_MENOR, LEX_MENORIGUAL, LEX_MULT, LEX_SOMA, LEX_SUB, LEX_TRUE

from tokens import TOKEN_ABRE_PARENTESES, TOKEN_BOOL, TOKEN_BREAK, TOKEN_CALL, TOKEN_CONTINUE, TOKEN_DIFERENTE, TOKEN_DIV, TOKEN_ELSE, TOKEN_FECHA_CHAVES, TOKEN_FECHA_PARENTESES, TOKEN_FUNC, TOKEN_ID, TOKEN_IF, TOKEN_IGUAL, TOKEN_INT, TOKEN_MAIOR, TOKEN_MAIORIGUAL, TOKEN_MENOR, TOKEN_MENORIGUAL, TOKEN_MULT, TOKEN_NUM, TOKEN_PONTOVIRGULA, TOKEN_PRINT, TOKEN_PROC, TOKEN_SOMA, TOKEN_SUB, TOKEN_TRUEFALSE, TOKEN_WHILE


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
        self.escopo()  

        self.check_semantica()
        return

    def escopo(self):
        if self.token_atual().tipo == "token601_endmain":
            return
        else:
            self.escopo_main()
            self.escopo()
            return

    def escopo_main(self):
        if self.token_atual().tipo == "token600_main":
            self.indexDaTabelaDeTokens += 1
            if self.token_atual().tipo == "token204_{":
                self.indexDaTabelaDeTokens += 1

                while self.token_atual().tipo != "token205_}":
                    self.block_escopo_main()

                if self.token_atual().tipo == "token205_}":
                    self.indexDaTabelaDeTokens += 1

                    if self.token_atual().tipo == "token601_endmain":
                        print("#============================#\n")
                        print("#  FIM DA AN??LISE SINT??TICA  #\n")
                        print("#  FINALIZADO SEM PROBLEMAS  #\n")
                        print("#============================#\n")   
                        self.tabelaDeTresEnderecos.append(
                            '$'
                        )                     
                    else:
                        raise Exception(
                            "Erro sint??tico: falta do endmain na linha "
                            + str(self.token_atual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sint??tico: falta do } na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sint??tico: falta do { na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sint??tico: C??digo fora do padr??o na linha "
                + str(self.token_atual().linha)
            )

    def block_escopo_main(self, context = False, is_while: bool = False, is_if: bool = False, is_proc: bool = False):
        if self.token_atual().tipo == "token609_int" or self.token_atual().tipo == "token610_bool":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.declaration_var_escopo_main(temp, context=context)
            return temp

        if self.token_atual().tipo == "token602_func":

            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.func_declar(temp)
            return temp

        if self.token_atual().tipo == "token615_proc":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.proc_declar(temp)
            return temp

        if self.token_atual().tipo == "token604_call":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.indexDaTabelaDeTokens += 1
            temp = self.call_proc_escopo_main(temp)
    
            if self.token_atual().tipo == "token200_;":
                self.salvar_call_proc_tres_enderecos(temp)
                self.indexDaTabelaDeTokens += 1
                if not context:
                    self.tabelaDeSimbolos.append(temp)
                return temp
            else:
                raise Exception(
                    "Erro sint??tico: falta do ponto e virgula na linha "
                    + str(self.token_atual().linha)
                )

        if self.token_atual().tipo == "token608_print":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.print_escopo_main(temp)
            return temp


        if self.token_atual().tipo == "token605_if":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.if_escopo_main(temp)
            self.salvar_if_tres_enderecos(temp)
            return temp


        if self.token_atual().tipo == "token607_while":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.while_escopo_main(temp)
            self.salvar_while_tres_enderecos(temp)
            return temp


        if self.token_atual().tipo == "token500_Id": 
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.declaration_var_escopo_main(temp, is_attribution=True, context=context)
            return temp

        else:
            raise Exception(
                f'Erro sint??tico: Token {self.token_atual().lexema} n??o ?? v??lido no escopo atual, linha '
                + str(self.token_atual().linha)
            )

    # o bloco que cont??m break/continue que s?? pode ser chamado dentro de um while
    def block_escopo_while(self, context = True, is_while = True):

        if self.token_atual().tipo == "token609_int" or self.token_atual().tipo == "token610_bool":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.declaration_var_escopo_main(temp)
            return temp


        if self.token_atual().tipo == "token604_call":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.indexDaTabelaDeTokens += 1

            if self.token_atual().tipo == "token602_func":
                temp.append(self.token_atual().tipo)
                temp = self.call_func_escopo_main(temp)
                if self.token_atual().tipo == "token200_;":
                    if not context:
                        self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return temp
                else:
                    raise Exception(
                        "Erro sint??tico: falta do ponto e virgula na linha "
                        + str(self.token_atual().linha)
                    )

            elif self.token_atual().tipo == "token615_proc":
                temp.append(self.token_atual().tipo)
                temp = self.call_proc_escopo_main(temp)
                if self.token_atual().tipo == "token200_;":
                    if not context:
                        self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return temp
                else:
                    raise Exception(
                        "Erro sint??tico: falta do ponto e virgula na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sint??tico: falta de proc ou func na linha "
                    + str(self.token_atual().linha)
                )


        if self.token_atual().tipo == "token608_print":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.print_escopo_main(temp)
            return temp


        if self.token_atual().tipo == "token605_if":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.if_escopo_main_flow(temp, context, is_while=True)
            return temp


        if self.token_atual().tipo == "token606_else":
            raise Exception(
                "Erro sint??tico: else adicionado de maneira incorreta "
                + str(self.token_atual().linha)
            )


        if self.token_atual().tipo == "token607_while":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.while_escopo_main(temp)
            return temp


        if self.token_atual().tipo == "token500_Id":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            temp.append(self.token_atual().lexema)
            self.call_var_escopo_main(temp)
            return temp

 
        if is_while and self.token_atual().tipo == "token613_break" or self.token_atual().tipo == "token614_cont":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.statement_flow()
            return temp

        else:
            raise Exception(
                f'Erro sint??tico: Token {self.token_atual().lexema} n??o ?? v??lido no escopo atual, linha '
                + str(self.token_atual().linha)
            )

    # ?? o que s?? pode ser chamado dentro de um if
    def block_escopo_if(self, context=False, is_while=False, is_if = False):

        if self.token_atual().tipo == "token609_int" or self.token_atual().tipo == "token610_bool":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.declaration_var_escopo_main(temp)
            return temp


        if self.token_atual().tipo == "token604_call":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.indexDaTabelaDeTokens += 1

            if self.token_atual().tipo == "token602_func":
                temp.append(self.token_atual().tipo)
                temp = self.call_func_escopo_main(temp)
                if self.token_atual().tipo == "token200_;":
                    if not context:
                        self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return temp
                else:
                    raise Exception(
                        "Erro sint??tico: falta do ponto e virgula na linha "
                        + str(self.token_atual().linha)
                    )

            elif self.token_atual().tipo == "token615_proc":
                temp.append(self.token_atual().tipo)
                temp = self.call_proc_escopo_main(temp)
                if self.token_atual().tipo == "token200_;":
                    if not context:
                        self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return temp
                else:
                    raise Exception(
                        "Erro sint??tico: falta do ponto e virgula na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sint??tico: falta de proc ou func na linha"
                    + str(self.token_atual().linha)
                )


        if self.token_atual().tipo == "token608_print":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.print_escopo_main(temp)
            return temp


        if self.token_atual().tipo == "token605_if":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.if_escopo_main(temp, context=True)
            return temp

        if self.token_atual().tipo == "token606_else":
            raise Exception(
                "Erro sint??tico: else adicionado de maneira incorreta "
                + str(self.token_atual().linha)
            )

        if self.token_atual().tipo == "token607_while":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.while_escopo_main(temp)
            return temp

  
        if self.token_atual().tipo == "token500_Id":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            temp.append(self.token_atual().lexema)
            self.call_var_escopo_main(temp, is_if = is_if)
            return temp

        if is_while and (self.token_atual().tipo == "token613_break" or self.token_atual().tipo == "token614_cont"):
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.token_atual().linha)
            temp.append(self.token_atual().tipo)
            self.statement_flow()
            return temp

        else:
            raise Exception(
                f'Erro sint??tico: Token {self.token_atual().lexema} n??o ?? v??lido no escopo atual, linha '
                + str(self.token_atual().linha)
            )

    def declaration_var_escopo_main(self, temp, is_attribution = False, context = False):
        if not is_attribution:
            self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token500_Id":
            temp.append(self.token_atual().lexema)
            self.indexDaTabelaDeTokens += 1
            if self.token_atual().tipo == "token111_=" and is_attribution:  
                temp.append(self.token_atual().lexema)
                self.indexDaTabelaDeTokens += 1
                temp.append([])
                self.atrib_var_escopo_main(temp)

                if self.token_atual().tipo == "token200_;":
                    self.indexDaTabelaDeTokens += 1
                    if not context:
                        self.tabelaDeSimbolos.append(temp)
                else:
                    raise Exception(
                        "Erro sint??tico: falta do ponto e virgula na linha "
                        + str(self.token_atual().linha)
                    )                
            elif self.token_atual().tipo == "token200_;":
                self.indexDaTabelaDeTokens += 1
                if not context:
                    self.tabelaDeSimbolos.append(temp)
            else:
                raise Exception(
                    f"Erro sint??tico: token {self.token_atual().lexema} n??o ?? permitido em declara????o de vari??vel, linha "
                    + str(self.token_atual().linha)
                )
        elif self.token_atual().tipo == TOKEN_CALL:
            proc_dec = self.buscar_proc_decl()
        else:
            raise Exception(
                "Erro sint??tico: nome da vari??vel precisa ser declarado na linha " +
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
                        if (i[5][index][1] == TOKEN_INT):
                            if not dados[5][2][index].isnumeric():
                                var_decl = self.call_buscar_var_decl(dados, dados[5][2][index])
                                if var_decl:
                                    continue
                                raise Exception(
                                    f'Erro sem??ntico: Valor "{dados[5][2][index]}" n??o suportado no {index+1}?? par??metro da fun????o {i[4]}, linha '
                                    + str(dados[1])
                                )
                        elif (i[5][index][1] == TOKEN_BOOL):
                            if (dados[5][2][index] != 'True'
                                and dados[5][2][index] != 'False'):
                                var_decl = self.call_buscar_var_decl(dados, dados[5][2][index])
                                if var_decl:
                                    continue
                                raise Exception(
                                    f'Erro sem??ntico: Valor "{dados[5][2][index]}" n??o suportado no {index+1}?? par??metro da fun????o {i[4]}, linha '
                                    + str(dados[1])
                                )
                    return i

    def buscar_func_decl_nome(self, dados):
        for i in self.tabelaDeSimbolos:
            if (i[2] == 'token602_func'
                and i[4] == dados[4]
                and i[0] <= dados[0]
                and i[1] < dados[1]
            ):
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
                                    f'Erro sem??ntico: Valor "{dados[4][index]}" n??o suportado no {index+1}?? par??metro da fun????o {i[4]}, linha '
                                    + str(dados[1])
                                )
                        elif (i[5][index][1] == TOKEN_BOOL):
                            if (dados[4][index] != 'True'
                                and dados[4][index] != 'False'):
                                var_decl = self.call_buscar_var_decl(dados, dados[4][index])
                                if var_decl:
                                    continue
                                raise Exception(
                                    f'Erro sem??ntico: Valor "{dados[4][index]}" n??o suportado no {index+1}?? par??metro da fun????o {i[4]}, linha '
                                    + str(dados[1])
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
                                        f'Erro sem??ntico: tipo de par??mentro inv??lido na linha {self.token_atual().linha}'
                                    )
                                return []
                        elif (i[5][index][1] == 'token611_boolValue'):
                            if (dados[5][2][index] != 'True'
                                and dados[5][2][index] != 'False'):
                                if semantica:
                                    raise Exception(
                                        f'Erro sem??ntico: tipo de par??mentro inv??lido na linha {self.token_atual().linha}'
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
                                        f'Erro sem??ntico: tipo de par??mentro inv??lido na linha {self.token_atual().linha}'
                                    )
                                return []
                        elif (i[5][index][1] == 'token611_boolValue'):
                            if (dados[5][2][index] != 'True'
                                and dados[5][2][index] != 'False'):
                                if semantica:
                                    raise Exception(
                                        f'Erro sem??ntico: tipo de par??mentro inv??lido na linha {self.token_atual().linha}'
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
            elif (i[2] == TOKEN_IF):
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
        for i in reversed(range(len(dados[4]))):
            self.tabelaDeTresEnderecos.append(
                f'param {dados[4][i]}'
            )
            
        self.tabelaDeTresEnderecos.append(
            f'call {dados[3]}, {len(dados[4])}'
        )

    def salvar_if_tres_enderecos(self, dados, is_while=False, whilename=False, endwhilename = False):
        self.tabelaDeTresEnderecos.append((
            f'temp{self.tempAtualTresEnd}: if {dados[3][0]} {self.inverter_relacional(dados[3][1])} {dados[3][2]}'
            + f' goto temp{self.tempAtualTresEnd+2 if (dados[6] and dados[6][1] == TOKEN_ELSE) else self.tempAtualTresEnd+1 }'
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
            elif i[2] == TOKEN_IF:
                self.tempAtualTresEnd += 1
                self.salvar_if_tres_enderecos(i)
        
        if (dados[6]
            and  dados[6][1] == TOKEN_ELSE
        ):
            self.tabelaDeTresEnderecos.append(
                f'goto temp{if_name}'
            )
            self.tempAtualTresEnd += 1
            self.salvar_else_tres_enderecos(dados[6])

        self.tabelaDeTresEnderecos.append(
            f'temp{if_name}:'
        )
        self.tempAtualTresEnd += 1

    def salvar_else_tres_enderecos(self, dados, is_while=False, whilename=False, endwhilename = False):
        self.tabelaDeTresEnderecos.append((
            f'temp{self.tempAtualTresEnd}:'
        ))
        self.tempAtualTresEnd += 1

        if_name = self.tempAtualTresEnd
        for i in dados[2]:
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
            elif i[2] == TOKEN_IF:
                self.tempAtualTresEnd += 1
                self.salvar_if_tres_enderecos(i)

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
                        func_declaration = []
                    for i in reversed(range(len(func_declaration))):
                        self.tabelaDeTresEnderecos.append(f'param {func_declaration[i]}')
                    self.tabelaDeTresEnderecos.append((dados[3] + ' := call ' + dados[5][1] + ',' + str(n_params)))
            else:
                lista = dados[5][::-1]
                contador = 0    
                self.tabelaDeTresEnderecos.append(("temp"+str(self.tempAtualTresEnd) + " := " + lista[contador+2] + lista[contador+1] + lista[contador]))
                contador += 3
                self.tempAtualTresEnd += 1
                if(contador < len(lista)):
                    self.salvar_valores(lista, contador)
                self.tabelaDeTresEnderecos.append((dados[3] + ' := ' + "temp"+str(self.tempAtualTresEnd-1)))
        else:
            self.tabelaDeTresEnderecos.append((dados[3] + ' := ' + dados[5][0]))


    def atrib_var_escopo_main(self, temp, is_if = False):
        tempEndVar = temp[5]
        if self.token_atual().tipo == "token604_call":
            tempEndVar.append(self.token_atual().tipo)
            self.call_func_escopo_main(tempEndVar)
            if not is_if:
                self.salvar_variaveis_tres_endereco(temp)
            return

        if self.token_atual().tipo == "token611_boolValue":

            if (
                self.token_atual().lexema == "True"
                or self.token_atual().lexema == "False"
            ):
                tempEndVar.append(self.token_atual().lexema)
                self.indexDaTabelaDeTokens += 1
                if not is_if:
                    self.salvar_variaveis_tres_endereco(temp)
                return
            else:
                raise Exception(
                    "Erro sint??tico: Valor Booleano atribuido erroneamente na linha "
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
                self.call_op_escopo_main(tempEndVar)
                if not is_if:
                    self.salvar_variaveis_tres_endereco(temp)
            elif self.token_atual().tipo == TOKEN_PONTOVIRGULA:
                if not is_if:
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
                self.call_op_escopo_main(tempEndVar)
                if not is_if:
                    self.salvar_variaveis_tres_endereco(temp)
                return
            elif self.token_atual().tipo == TOKEN_PONTOVIRGULA:
                if not is_if:
                    self.salvar_variaveis_tres_endereco(temp)
                return
        else:
            raise Exception(
                "Erro sint??tico: atribui????o de variavel inv??lida na linha "
                + str(self.token_atual().linha)
            )


    def call_var_escopo_main(self, temp, context = False, is_if=False):
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token111_=":  
            temp.append(self.token_atual().lexema)
            self.indexDaTabelaDeTokens += 1
            temp.append([])
            self.atrib_var_escopo_main(temp, is_if=is_if)

            if self.token_atual().tipo == "token200_;":
                self.indexDaTabelaDeTokens += 1
                if not context:
                    self.tabelaDeSimbolos.append(temp)
            else:
                raise Exception(
                    "Erro sint??tico: falta do ponto e virgula na linha "
                    + str(self.token_atual().linha)
                )  
        else:
            raise Exception(
                "Erro sint??tico: s??mbolo de atribui????o n??o encontrado na linha "
                + str(self.token_atual().linha)
            )


    def func_declar(self, temp):
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
                            while self.token_atual().tipo == "token201_,":
                                self.params_declar(tempParenteses)  

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
                                            self.block_escopo_main(context=True))

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
                                        tempReturnParams = self.return_declar(
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
                                                        f'Erro sem??ntico: Chamada de fun????o n??o suportada no retorno {self.token_atual().linha}'
                                                    )
                                            else:
                                                lista = tempReturn[3][::-1]
                                                contador = 0    
                                                self.tabelaDeTresEnderecos.append(("temp"+str(self.tempAtualTresEnd) + " := " + lista[contador+2] + lista[contador+1] + lista[contador]))
                                                contador += 3
                                                self.tempAtualTresEnd += 1
                                                if(contador < len(lista)):
                                                    self.salvar_valores(lista, contador)
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
                                                == "token602_endfunc"
                                            ):
                                                self.indexDaTabelaDeTokens += 1
                                                self.tabelaDeSimbolos.append(temp)
                                            else:
                                                raise Exception(
                                                    "Erro sint??tico: falta do ponto e v??rgula na linha "
                                                    + str(self.token_atual().linha)
                                                )
                                        else:
                                            raise Exception(
                                                "Erro sint??tico: falta da chave direita na linha "
                                                + str(self.token_atual().linha)
                                            )
                                    else:
                                        raise Exception(
                                            "Erro sint??tico: falta do retorno na linha "
                                            + str(self.token_atual().linha)
                                        )

                                else:
                                    raise Exception(
                                        "Erro sint??tico: falta da chave esquerda na linha "
                                        + str(self.token_atual().linha)
                                    )
                            else:
                                raise Exception(
                                    "Erro sint??tico: falta do parentese direito na linha "
                                    + str(self.token_atual().linha)
                                )
                        else:
                            raise Exception(
                                "Erro sint??tico: falta o ID na linha "
                                + str(self.token_atual().linha)
                            )

                    else:
                        raise Exception(
                            'Erro sint??tico: falta declara????o de par??metros da fun????o, ?? obrigat??rio, linha '
                            + str(self.token_atual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sint??tico: falta do parentese esquerdo na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sint??tico: falta do ID na linha "
                    + str(self.token_atual().linha)
                )


    def return_declar(self, tempReturnParams):
        self.indexDaTabelaDeTokens += 1

  
        if self.token_atual().tipo == "token604_call":
            tempReturnParams.append(self.token_atual().tipo)
            self.indexDaTabelaDeTokens += 1
            if self.token_atual().tipo == "token602_func":
                tempReturnParams.append(self.token_atual().tipo)
                self.call_func_escopo_main(tempReturnParams)
                self.indexDaTabelaDeTokens += 1
                return tempReturnParams
            else:
                raise Exception(
                    "Erro sint??tico: Erro de chamada, s?? ?? permitido chamada de fun????es na linha "
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
                    "Erro sint??tico: falta do ponto e virgula na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sint??tico: Retorno errado na linha "
                + str(self.token_atual().linha)
            )


    def params_declar(self, tempParenteses):
    
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
                    self.params_declar(tempParenteses)
                elif (
                    self.token_atual().tipo == "token609_int" or self.token_atual().tipo == "token610_bool"
                ):
                    raise Exception(
                        "Erro sint??tico: falta v??rgula na linha "
                        + str(self.token_atual().linha)
                    )
                else:
                    return tempParenteses
            else:
                raise Exception(
                    "Erro sint??tico: ?? necess??rio informar alguma v??riavel na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sint??tico: ?? necess??rio informar um tipo na linha "
                + str(self.token_atual().linha)
            )


    def proc_declar(self, temp):
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
                        while self.token_atual().tipo == "token201_,":
                            self.params_declar(tempParenteses)

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
                                        self.block_escopo_main(context=True))

                                temp.append(tempBlock)
                                if self.token_atual().tipo == "token205_}":
                                    self.tabelaDeTresEnderecos.append(('EndFunc'))
                                    self.indexEscopoAtual = (
                                        self.indexEscopoAntesDaFuncao
                                    )
                                    self.indexDaTabelaDeTokens += 1

                                    if (
                                        self.token_atual().tipo
                                        == "token615_endproc"
                                    ):
                                        self.indexDaTabelaDeTokens += 1
                                        self.tabelaDeSimbolos.append(temp)
                                    else:
                                        raise Exception(
                                            "Erro sint??tico: falta do ponto e v??rgula na linha "
                                            + str(self.token_atual().linha)
                                        )
                                else:
                                    raise Exception(
                                        "Erro sint??tico: falta da chave direita na linha "
                                        + str(self.token_atual().linha)
                                    )

                            else:
                                raise Exception(
                                    "Erro sint??tico: falta da chave esquerda na linha "
                                    + str(self.token_atual().linha)
                                )
                        else:
                            raise Exception(
                                "Erro sint??tico: falta do parentese direito na linha "
                                + str(self.token_atual().linha)
                            )

                    else:
                        raise Exception(
                            "Erro sint??tico: falta o Id na linha "
                            + str(self.token_atual().linha)
                        )

                else:
                    raise Exception(
                        'Erro sint??tico: falta declara????o de par??metros da fun????o ou procedimento, ?? obrigat??rio, linha '
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sint??tico: falta do parentese esquerdo na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sint??tico: Nome do procedimento n??o definido na linha " +
                str(self.token_atual().linha)
            )

    def call_proc_escopo_main(self, temp):
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
                            self.params_call_escopo_main(tempParams))
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
                            "Erro sint??tico: falta da virgula na linha "
                            + str(self.token_atual().linha)
                        )
                else:
                    temp.append(tempParams)
                    if self.token_atual().tipo == "token203_)":

                        self.indexDaTabelaDeTokens += 1
                        return temp
                    else:
                        raise Exception(
                            "Erro sint??tico: falta do parentese direito na linha "
                            + str(self.token_atual().linha)
                        )
            else:
                raise Exception(
                    "Erro sint??tico: falta do parentese esquerdo na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sint??tico: falta do ID na linha " +
                str(self.token_atual().linha)
            )


    def call_func_escopo_main(self, temp):
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
                            self.params_call_escopo_main(tempParams))
                        tempParams.pop()
                        if self.token_atual().tipo == "token203_)":
                            self.indexDaTabelaDeTokens += 1
                            temp.append(tempParams)
                            return temp
                        else:
                            raise Exception(
                                "Erro sint??tico: falta do parentese direito na linha "
                                + str(self.token_atual().linha)
                            )
                    elif self.token_atual().tipo == "token203_)":
                        self.indexDaTabelaDeTokens += 1
                        temp.append(tempParams)
                        return temp
                    else:
                        raise Exception(
                            "Erro sint??tico: falta do parentese direito na linha "
                            + str(self.token_atual().linha)
                        )

                else:
                    temp.append(tempParams)
                    if self.token_atual().tipo == "token203_)":
                        self.indexDaTabelaDeTokens += 1

                        return temp
                    else:
                        raise Exception(
                            "Erro sint??tico: falta do parentese direito na linha "
                            + str(self.token_atual().linha)
                        )
            else:
                raise Exception(
                    "Erro sint??tico: falta do parentese esquerdo na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sint??tico: falta o nome da fun????o na linha " +
                str(self.token_atual().linha)
            )

    def params_call_escopo_main(self, tempParams):
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
                self.params_call_escopo_main(tempParams)
            elif (
                self.token_atual().tipo == "token500_Id"
                or self.token_atual().lexema == "True"
                or self.token_atual().lexema == "False"
                or self.token_atual().tipo == "token300_Num"
            ):
                raise Exception(
                    "Erro sint??tico: falta v??rgula na linha "
                    + str(self.token_atual().linha)
                )
            else:

                return tempParams
        else:
            raise Exception(
                "Erro sint??tico: ?? necess??rio informar alguma v??riavel na linha "
                + str(self.token_atual().linha)
            )


    def print_escopo_main(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token202_(":
            tempParams = []
            temp.append(self.params_print_escopo_main(tempParams))


            self.tabelaDeTresEnderecos.append(
                f'write {temp[3][0]}')
            if self.token_atual().tipo == "token203_)":
                self.indexDaTabelaDeTokens += 1
                if self.token_atual().tipo == "token200_;":
                    self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return
                else:

                    raise Exception(
                        "Erro sint??tico: falta do ponto e virgula na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sint??tico: falta do Parentese direito na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sint??tico: falta do Parentese esquerdo na linha  "
                + str(self.token_atual().linha)
            )


    def params_print_escopo_main(self, tempParams):
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token604_call":
            tempParams.append(self.token_atual().tipo)
            self.indexDaTabelaDeTokens += 1
            if self.token_atual().tipo == "token602_func":
                tempParams.append(self.token_atual().tipo)
                tempParams = self.call_func_escopo_main(tempParams)
                return tempParams
            elif self.token_atual().tipo == "token615_proc":
                raise Exception(
                    "Erro sint??tico: Procedimento n??o tem retorno na linha "
                    + str(self.token_atual().linha)
                )
            else:
                raise Exception(
                    "Erro sint??tico: chamada incorreta de fun????o na linha "
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
                self.call_op_escopo_main(tempParams)
                return tempParams
            else:
                return tempParams
        else:
            raise Exception(
                "Erro sint??tico: uso incorreto dos parametros na linha "
                + str(self.token_atual().linha)
            )

    def else_escopo_while(self, tempElse):
    
        lookAhead = self.token_look_ahead()
        self.indexToken += 1
        if self.token_atual().tipo == "token204_{" and lookAhead != "token205_}": 
            self.indexToken += 1
            tempBlock = []
            while(self.token_atual().tipo != "token205_}" and self.tokenLookAhead().tipo != "token606_endelse"):         
                tempBlock.append(self.block_escopo_main(isIf=True))
            if self.token_atual().tipo == "token205_}":
                self.indexToken += 1
                if self.token_atual().tipo == "token606_endelse":  
                    tempElse.append(self.token_atual().tipo)
                    self.indexToken += 1
                    return tempElse
                else:
                    raise Exception(
                        "Erro sint??tico: falta de endelse na linha "
                        + str(self.token_atual().linha)
                        )
            else:
                raise Exception(
                    "Erro sint??tico: falta do } na linha "
                    + str(self.token_atual().linha)
                )      
        else:
            raise Exception(
                "Erro sint??tico: falta do } ou bloco vazio na linha " +
                str(self.token_atual().linha)
            )   

    def if_escopo_main(self, temp, context=False):
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token202_(":
            self.indexDaTabelaDeTokens += 1
            tempExpression = []
            tempExpression = self.expression_escopo_main(tempExpression)
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
                        tempBlock.append(self.block_escopo_if(context=context, is_while=False, is_if=True))

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
                                tempElse = self.else_part_escopo_main(
                                    tempElse, context=context)  

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
                                "Erro sint??tico: falta de endif na linha "
                                + str(self.token_atual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sint??tico: falta do } na linha "
                            + str(self.token_atual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sint??tico: falta do { ou bloco vazio na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sint??tico: falta do Parentese direito na linha  "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sint??tico: falta do Parentese esquerdo na linha  "
                + str(self.token_atual().linha)
            )


    def else_part_escopo_main(self, tempElse, context = False):
        olhaAfrente = self.token_look_ahead()
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token204_{" and olhaAfrente.tipo != "token205_}":
            self.indexDaTabelaDeTokens += 1
            tempBlock = []
            while (
                self.token_atual().tipo != "token205_}"
                and self.token_look_ahead().tipo != "token606_endelse"
            ):
                tempBlock.append(self.block_escopo_if(context=context, is_if=True))
            tempElse.append(tempBlock)
            if self.token_atual().tipo == "token205_}":
                self.indexDaTabelaDeTokens += 1
                if self.token_atual().tipo == "token606_endelse":
                    tempElse.append(self.token_atual().tipo)
                    self.indexDaTabelaDeTokens += 1
                    return tempElse
                else:
                    raise Exception(
                        "Erro sint??tico: falta de token606_endelse na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sint??tico: falta do } na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sint??tico: falta do { ou bloco vazio na linha "
                + str(self.token_atual().linha)
            )


    def if_escopo_main_flow(self, temp, context=False, is_while=False):
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token202_(":
            self.indexDaTabelaDeTokens += 1
            tempExpression = []
            tempExpression = self.expression_escopo_main(tempExpression)
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
                        tempBlock.append(self.block_escopo_while())
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
                                tempElse = self.else_escopo_main_flow(
                                    tempElse, is_while=is_while)  

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
                                "Erro sint??tico: falta de endif na linha "
                                + str(self.token_atual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sint??tico: falta do } na linha "
                            + str(self.token_atual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sint??tico: falta do { ou Bloco vazio na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sint??tico: falta do Parentese direito na linha  "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sint??tico: falta do Parentese esquerdo na linha  "
                + str(self.token_atual().linha)
            )


    def else_escopo_main_flow(self, tempElse, is_while=False):
        olhaAfrente = self.token_look_ahead()
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token204_{" and olhaAfrente.tipo != "token205_}":
            self.indexDaTabelaDeTokens += 1
            tempBlock = []
            while (
                self.token_atual().tipo != "token205_}"
                and self.token_look_ahead().tipo != "token606_endelse"
            ):
                tempBlock.append(self.block_escopo_if(is_while=is_while))
            tempElse.append(tempBlock)
            if self.token_atual().tipo == "token205_}":
                self.indexDaTabelaDeTokens += 1
                if self.token_atual().tipo == "token606_endelse":
                    tempElse.append(self.token_atual().tipo)
                    self.indexDaTabelaDeTokens += 1
                    return tempElse
                else:
                    raise Exception(
                        "Erro sint??tico: falta de endelse na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sint??tico: falta do } na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sint??tico: falta do { ou bloco vazio na linha "
                + str(self.token_atual().linha)
            )


    def while_escopo_main(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.token_atual().tipo == "token202_(":
            self.indexDaTabelaDeTokens += 1
            tempExpression = []
            tempExpression = self.expression_escopo_main(tempExpression)
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
                        tempBlock.append(self.block_escopo_while(context=True))

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
                                "Erro sint??tico: falta de endwhile na linha "
                                + str(self.token_atual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sint??tico: falta do } na linha "
                            + str(self.token_atual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sint??tico: falta do { na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sint??tico: falta do ) na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sint??tico: falta do ( na linha "
                + str(self.token_atual().linha)
            )


    def statement_flow(self):
        if self.token_atual().tipo == "token614_cont":
            self.indexDaTabelaDeTokens += 1
            if self.token_atual().tipo == "token200_;":
                self.indexDaTabelaDeTokens += 1
            else:
                raise Exception(
                    "Erro sint??tico: falta do ponto e virgula na linha "
                    + str(self.token_atual().linha)
                )

        if self.token_atual().tipo == "token613_break":
            self.indexDaTabelaDeTokens += 1
            if self.token_atual().tipo == "token200_;":
                self.indexDaTabelaDeTokens += 1
            else:
                raise Exception(
                    "Erro sint??tico: falta do ponto e virgula na linha "
                    + str(self.token_atual().linha)
                )


    def expression_escopo_main(self, tempExpression):
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
                        "Erro sint??tico: falta do Id na linha "
                        + str(self.token_atual().linha)
                    )
            else:
                raise Exception(
                    "Erro sint??tico: falta do operador booleano na linha "
                    + str(self.token_atual().linha)
                )
        else:
            raise Exception(
                "Erro sint??tico: falta do ID na linha " +
                str(self.token_atual().linha)
            )


    def call_op_escopo_main(self, tempEndVar):
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
                self.call_op_escopo_main(tempEndVar)

            else:
                return
        else:
            raise Exception(
                "Erro sint??tico: falta do ID na linha " +
                str(self.token_atual().linha)
            )

    #An??lise Sem??ntica
    def check_semantica(self):
        for k in range(len(self.tabelaDeSimbolos)):
            simbolo = self.tabelaDeSimbolos[k][2]
            if simbolo == TOKEN_FUNC:
                self.declaration_func_semantico(self.tabelaDeSimbolos[k])

            elif simbolo == TOKEN_PROC:
                self.declaration_proc_semantico(self.tabelaDeSimbolos[k])

            elif simbolo == TOKEN_CALL:
                self.buscar_proc_decl_semantica(self.tabelaDeSimbolos[k])

            elif simbolo == TOKEN_INT or simbolo == TOKEN_BOOL:
                var_decl = self.buscar_var_decl(self.tabelaDeSimbolos[k])
                if var_decl:
                    raise Exception(
                        f'Erro sem??ntico: Vari??vel "{self.tabelaDeSimbolos[k][3]}" j?? declarada neste escopo, linha '
                        + str(self.tabelaDeSimbolos[k][1])
                    )

            elif simbolo == TOKEN_IF:
                self.expression_semantico(self.tabelaDeSimbolos[k])

            elif simbolo == TOKEN_ELSE:
                self.expression_semantico(self.tabelaDeSimbolos[k])

            elif simbolo == TOKEN_WHILE:
                self.expression_semantico(self.tabelaDeSimbolos[k])

            elif simbolo == TOKEN_ID:
                self.call_var_semantico(self.tabelaDeSimbolos[k])

        print("#============================#\n")
        print("#  FIM DA AN??LISE SEM??NTICA  #\n")
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
                        f'Erro sem??ntico: Vari??vel "{token[3]}" j?? declarada neste escopo, linha '
                        + str(token[1])
                    )
                return


            if simbolo == "token605_if":
                self.expression_semantico(token)

            if simbolo == "token607_while":
                self.expression_semantico(token)

            if simbolo == "token500_Id":
                self.call_var_func_semantico(token, func_context, func_params)
        
    def buscar_na_tabela_de_simbolos(self, simbolo, indice):
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
                                            varDeclaradaNaTabela = self.buscar_na_tabela_de_simbolos(
                                                tabelaNoIndiceAtual[5][3][n], 3)
                                            if(varDeclaradaNaTabela != None):
                                                if (varDeclaradaNaTabela[0] <= tabelaNoIndiceAtual[0]
                                                    ) and (varDeclaradaNaTabela[1] <= tabelaNoIndiceAtual[1]):
                                                    if(varDeclaradaNaTabela[2] == self.tabelaDeSimbolos[k][5][n][1]):
                                                        if self.tabelaDeSimbolos[k][3] == "token609_int":
                                                            return True
                                                        else:
                                                            raise Exception(
                                                                "Erro Sem??ntico: token609_int n??o recebe token609_int na linha: "
                                                                + str(tabelaNoIndiceAtual[1])
                                                            )
                                                    else:
                                                        raise Exception(
                                                            "Erro Sem??ntico: tipo de vari??veis incompativ??is nos parametros na linha: "
                                                            + str(tabelaNoIndiceAtual[1])
                                                        )
                                                else:
                                                    raise Exception(
                                                        "Erro Sem??ntico: vari??vel n??o declarada nos parametros na linha: "
                                                        + str(tabelaNoIndiceAtual[1])
                                                    )
                                            else:
                                                raise Exception(
                                                    "Erro Sem??ntico: vari??vel n??o declarada nos parametros na linha: "
                                                    + str(tabelaNoIndiceAtual[1])
                                                )
                                    else:
                                        raise Exception(
                                            "Erro Sem??ntico: quantidade de parametros inv??lida na linha: "
                                            + str(tabelaNoIndiceAtual[1])
                                        )
                                else:
                                    raise Exception(
                                        "Erro Sem??ntico: fun????o n??o declarada na linha: "
                                        + str(tabelaNoIndiceAtual[1])
                                    )

                            else:
                                raise Exception(
                                    "Erro Sem??ntico: fun????o n??o declarada na linha: "
                                    + str(tabelaNoIndiceAtual[1])
                                )
                else:
                    raise Exception(
                        "Erro Sem??ntico: vari??vel n??o pode receber procedimento na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )

            if simbolo.isalpha() and simbolo != 'True' and simbolo != 'False':
                varDeclarada = self.buscar_na_tabela_de_simbolos(
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
                                "Erro Sem??ntico: vari??vel do tipo int n??o recebe inteiro na linha: "
                                + str(tabelaNoIndiceAtual[1])
                            )
                    else:
                        raise Exception(
                            "Erro Sem??ntico: variavel n??o declarada na linha: "
                            + str(tabelaNoIndiceAtual[1])
                        )
                else:
                    raise Exception(
                        "Erro Sem??ntico: variavel n??o declarada na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )
            else:
                raise Exception(
                    "Erro Sem??ntico: vari??vel do tipo inteiro n??o recebe inteiro na linha: "
                    + str(tabelaNoIndiceAtual[1])
                )

        if tabelaNoIndiceAtual[2] == "token610_bool":

   
            simbolo = tabelaNoIndiceAtual[5][0]
            if simbolo == "True" or simbolo == "False":
                return True

            if simbolo.isnumeric():
                raise Exception(
                    "Erro Sem??ntico: vari??vel do tipo bool n??o recebe boolean na linha: "
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
                                            varDeclaradaNaTabela = self.buscar_na_tabela_de_simbolos(
                                                tabelaNoIndiceAtual[5][3][n], 3)
                                            if(varDeclaradaNaTabela != None):
                                                if (varDeclaradaNaTabela[0] <= tabelaNoIndiceAtual[0]
                                                    ) and (varDeclaradaNaTabela[1] <= tabelaNoIndiceAtual[1]):
                                                    if(varDeclaradaNaTabela[2] == self.tabelaDeSimbolos[k][5][n][1]):
                                                        if self.tabelaDeSimbolos[k][3] == "token610_bool":
                                                            return True
                                                        else:
                                                            raise Exception(
                                                                "Erro Sem??ntico: bool n??o recebe boolean na linha: "
                                                                + str(tabelaNoIndiceAtual[1])
                                                            )
                                                    else:
                                                        raise Exception(
                                                            "Erro Sem??ntico: tipo de vari??veis incompativ??is nos parametros na linha: "
                                                            + str(tabelaNoIndiceAtual[1])
                                                        )
                                                else:
                                                    raise Exception(
                                                        "Erro Sem??ntico: vari??vel n??o declarada nos parametros na linha: "
                                                        + str(tabelaNoIndiceAtual[1])
                                                    )
                                            else:
                                                raise Exception(
                                                    "Erro Sem??ntico: vari??vel n??o declarada nos parametros na linha: "
                                                    + str(tabelaNoIndiceAtual[1])
                                                )
                                    else:
                                        raise Exception(
                                            "Erro Sem??ntico: quantidade de parametros inv??lida na linha: "
                                            + str(tabelaNoIndiceAtual[1])
                                        )
                                else:
                                    raise Exception(
                                        "Erro Sem??ntico: fun????o n??o declarada na linha: "
                                        + str(tabelaNoIndiceAtual[1])
                                    )

                            else:
                                raise Exception(
                                    "Erro Sem??ntico: fun????o n??o declarada na linha: "
                                    + str(tabelaNoIndiceAtual[1])
                                )
                else:
                    raise Exception(
                        "Erro Sem??ntico: vari??vel n??o pode receber procedimento na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )


            if simbolo.isalpha() and simbolo != 'True' and simbolo != 'False':
                varDeclarada = self.buscar_na_tabela_de_simbolos(
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
                                    "Erro Sem??ntico: vari??vel do tipo bool n??o recebe boolean na linha: "
                                    + str(tabelaNoIndiceAtual[1])
                                )
                        else:
                            raise Exception(
                                "Erro Sem??ntico: vari??vel do tipo bool n??o recebe boolean na linha: "
                                + str(tabelaNoIndiceAtual[1])
                            )
                    else:
                        raise Exception(
                            "Erro Sem??ntico: variavel n??o declarada na linha: "
                            + str(tabelaNoIndiceAtual[1])
                        )
                else:
                    raise Exception(
                        "Erro Sem??ntico: variavel n??o declarada na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )

            else:
                raise Exception(
                    "Erro Sem??ntico: vari??vel do tipo bool n??o recebe boolean na linha: "
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

        if flag == False:
            raise Exception(
                f'Erro Sem??ntico: vari??vel "{simbolo[3]}" n??o declarada neste escopo, linha: ' +
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

        if flag == False:
            raise Exception(
                "Erro Sem??ntico: vari??vel n??o declarada na linha: " +
                str(simbolo[1])
            )

    def buscarParamsProc(self, simbolo):
        paramsProc = self.buscar_na_tabela_de_simbolos("token615_proc", 2)
        if paramsProc != None:
            paramsProc = paramsProc[5]
            for k in range(len(paramsProc)):
                if simbolo[3] == paramsProc[k][2]:
                    if paramsProc[k][1] == "token609_int":
                        if simbolo[5].isnumeric():
                            return True
                        if not simbolo[5].isnumeric():
                            raise Exception(
                                "Erro Sem??ntico: vari??vel do tipo int n??o recebe inteiro na linha: "
                                + str(simbolo[1])
                            )
                    if paramsProc[k][1] == "token610_bool":
                        if simbolo[5] == "True" or simbolo[5] == "False":
                            return True
                        else:
                            raise Exception(
                                "Erro Sem??ntico: vari??vel do tipo booleano n??o recebe booleano na linha: "
                                + str(simbolo[1])
                            )
                    break
        else:
            return False

    def buscarParamsFunc(self, simbolo, n):
        paramsFunc = self.buscar_na_tabela_de_simbolos("token602_func", 2)
        if paramsFunc != None:
            paramsFunc = paramsFunc[5]
            for k in range(len(paramsFunc)):
                if simbolo[n] == paramsFunc[k][2]:
                    if paramsFunc[k][1] == "token609_int":
                        if simbolo[5].isnumeric():
                            return True
                        if not simbolo[5].isnumeric():
                            raise Exception(
                                "Erro Sem??ntico: vari??vel do tipo int n??o recebe inteiro na linha: "
                                + str(simbolo[1])
                            )
                    if paramsFunc[k][1] == "token610_bool":
                        if simbolo[5] == "True" or simbolo[5] == "False":
                            return True
                        else:
                            raise Exception(
                                "Erro Sem??ntico: vari??vel do tipo booleano n??o recebe booleano na linha: "
                                + str(simbolo[1])
                            )
                    break
        else:
            return False

    def declaration_func_semantico(self, tabelaNoIndiceAtual):
        func_decl = self.buscar_func_decl_nome(tabelaNoIndiceAtual)
        if func_decl:
            raise Exception(
                f'Erro sem??ntico: Nome da fun????o "{tabelaNoIndiceAtual[4]}" j?? definido, linha '
                + str(tabelaNoIndiceAtual[1])
            )
        func_params = [[param[0], tabelaNoIndiceAtual[1], param[1], param[2]] for param in tabelaNoIndiceAtual[5]]
        for param in tabelaNoIndiceAtual[5]:
            check_repetition = [p[2] for p in tabelaNoIndiceAtual[5] if p[2] == param[2]]
            if len(check_repetition) > 1:
                raise Exception(
                    f'Erro sem??ntico: Par??metro {param[2]} declarado mais de uma vez, linha '
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
                    'Erro sem??ntico: O retorno s?? pode conter um valor, opera????es ou chamada de fun????o deve ser feita em vari??veis antes e atribu??das ent??o ao retorno, linha '
                    + str(tabelaNoIndiceAtual[1])
                )
            if not tabelaNoIndiceAtual[7][3][0].isnumeric():
                var_decl = self.buscar_var_decl_atrib_return(tabelaNoIndiceAtual, tabelaNoIndiceAtual[6], func_params)
                if (var_decl[2] != TOKEN_INT):
                    raise Exception(
                        "Erro Sem??ntico: O retorno espera um n??mero inteiro ou uma vari??vel do tipo inteiro na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )

        if tabelaNoIndiceAtual[3] == "token610_bool":
            if (
                tabelaNoIndiceAtual[7][3][0] == "True"
                or tabelaNoIndiceAtual[7][3][0] == "False"
            ) is False:
                raise Exception(
                    "Erro Sem??ntico: O retorno espera um token611_boolValue na linha: "
                    + str(tabelaNoIndiceAtual[1])
                )

    def decl_func_params_semantico(self, tabelaNoIndiceAtual):
        for i, token in enumerate(tabelaNoIndiceAtual[5]):
            var_decl = self.buscar_var_decl_atrib_params(tabelaNoIndiceAtual, i)
            if var_decl:
                raise Exception(
                    f'Erro sem??ntico: Vari??vel de mesmo nome do par??metro j?? declarada em escopo exterior, linha '
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
                "Erro Sem??ntico: fun????o n??o declarada na linha: "
                + str(tabelaNoIndiceAtual[1])
            )

    def verificarParams(
        self, simboloDeclaradoNaTabela, simbolo, n, tipo, m, linha, escopo
    ):
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
                "Erro Sem??ntico: quantidade de par??metros inv??lido na linha: "
                + str(linha)
            )

        if flag != len(simboloDeclaradoNaTabela[n]):
            raise Exception(
                "Erro Sem??ntico: vari??vel do par??metro n??o declarada na linha: "
                + str(linha)
            )
        else:
            return True

    def comparaTipoChamadaComDeclaracao(
        self, declaracaoVarNaTabela, callFuncTabela, tipo, n
    ):
        declaracaoFuncNaTabela = self.buscar_na_tabela_de_simbolos(tipo, 2)
        flag = False
        for k in range(len(declaracaoFuncNaTabela[n])):
            if declaracaoFuncNaTabela[n][k][1] == declaracaoVarNaTabela[2]:
                flag = True
                break


            elif declaracaoVarNaTabela[2] == "token500_Id":
                tipoDeclaracaoDoID = self.buscar_na_tabela_de_simbolos("token500_Id", 2)
                varDeclarada = self.buscar_na_tabela_de_simbolos(
                    tipoDeclaracaoDoID[3], 3)
                if declaracaoFuncNaTabela[n][k][1] == varDeclarada[2]:
                    flag = True
                    break

        if flag == False:
            raise Exception(
                "Erro Sem??ntico: tipo do par??metro inv??lido na linha: "
                + str(callFuncTabela[1])
            )

    def declaration_proc_semantico(self, tabelaNoIndiceAtual):
        func_params = [[param[0], tabelaNoIndiceAtual[1], param[1], param[2]] for param in tabelaNoIndiceAtual[5]]
        for param in tabelaNoIndiceAtual[5]:
            check_repetition = [p[2] for p in tabelaNoIndiceAtual[5] if p[2] == param[2]]
            if len(check_repetition) > 1:
                raise Exception(
                    f'Erro sem??ntico: Par??metro {param[2]} declarado mais de uma vez, linha '
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
                "Erro Sem??ntico: procedimento n??o declarado na linha: "
                + str(tabelaNoIndiceAtual[1])
            )

    def expression_semantico(self, tabelaNoIndiceAtual):
        buscaParam1 = self.buscar_na_tabela_de_simbolos(
            tabelaNoIndiceAtual[3][0], 3)
        buscaParam2 = self.buscar_na_tabela_de_simbolos(
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
                        "Erro Sem??ntico: N??o ?? poss??vel comparar dois tipos diferentes na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )
                if buscaParam2[2] == "token609_int" and buscaParam1[2] != "token609_int":
                    raise Exception(
                        "Erro Sem??ntico: N??o ?? poss??vel comparar dois tipos diferentes na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )

                if buscaParam2[2] == "token609_int" and buscaParam1[2] == "token609_int":
                    if (buscaParam1[0] <= tabelaNoIndiceAtual[0]) and (
                        buscaParam2[0] <= tabelaNoIndiceAtual[0]
                    ):
                        return True
                    else:
                        raise Exception(
                            "Erro Sem??ntico: Vari??vel n??o declarada na linha: "
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
                                "Erro Sem??ntico: N??o ?? poss??vel fazer este tipo de compara????o com booleano na linha: "
                                + str(tabelaNoIndiceAtual[1])
                            )
                    else:
                        raise Exception(
                            "Erro Sem??ntico: Vari??vel n??o declarada na linha: "
                            + str(tabelaNoIndiceAtual[1])
                        )

                if buscaParam2[2] == "token609_int" and buscaParam1[2] != "token610_bool":
                    raise Exception(
                        "Erro Sem??ntico: N??o ?? poss??vel comparar dois tipos diferentes na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )
                if buscaParam2[2] == "token610_bool" and buscaParam1[2] != "token609_int":
                    raise Exception(
                        "Erro Sem??ntico: N??o ?? poss??vel comparar dois tipos diferentes na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )
            else:
                raise Exception(
                    "Erro Sem??ntico: variavel n??o declarada na linha: "
                    + str(tabelaNoIndiceAtual[1])
                )

        elif (
            tabelaNoIndiceAtual[3][0].isalpha()
            and (tabelaNoIndiceAtual[3][2]).isnumeric()
        ):
            if buscaParam1 != None:
                if buscaParam1[2] != "token609_int":
                    raise Exception(
                        "Erro Sem??ntico: N??o ?? poss??vel comparar dois tipos diferentes na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )
                else:
                    if buscaParam1[0] <= tabelaNoIndiceAtual[0]:
                        return True
                    else:
                        raise Exception(
                            "Erro Sem??ntico: Vari??vel n??o declarada na linha: "
                            + str(tabelaNoIndiceAtual[1])
                        )
            else:
                raise Exception(
                    "Erro Sem??ntico: variavel n??o declarada na linha: "
                    + str(tabelaNoIndiceAtual[1])
                )

        elif (tabelaNoIndiceAtual[3][0]).isnumeric() and tabelaNoIndiceAtual[3][
            2
        ].isalpha():
            if buscaParam2 != None:
                if buscaParam2[2] != "token609_int":
                    raise Exception(
                        "Erro Sem??ntico: N??o ?? poss??vel comparar dois tipos diferentes na linha: "
                        + str(tabelaNoIndiceAtual[1])
                    )
                else:
                    if buscaParam2[0] <= tabelaNoIndiceAtual[0]:
                        return True
                    else:
                        raise Exception(
                            "Erro Sem??ntico: Vari??vel n??o declarada na linha: "
                            + str(tabelaNoIndiceAtual[1])
                        )
            else:
                raise Exception(
                    "Erro Sem??ntico: variavel n??o declarada na linha: "
                    + str(tabelaNoIndiceAtual[1])
                )

        else:
            raise Exception(
                "Erro Sem??ntico: parametros inv??lidos na linha: "
                + str(tabelaNoIndiceAtual[1])
            )

    def salvar_valores(self, lista, contador):
        if(contador < len(lista)):
            self.tabelaDeTresEnderecos.append(("temp"+str(self.tempAtualTresEnd)  + " := " "temp"+str(self.tempAtualTresEnd-1) + lista[contador] + lista[contador+1]))
            self.tempAtualTresEnd += 1
            contador += 2
            if(contador < len(lista) + 2):
                self.salvar_valores(lista, contador)
    
    def deriva_atribuicao(self, simboloDeclaradoNaTabela, simbolo, func_context=False):
        is_func_call = False
        for i, s in enumerate(simbolo[5]):
            if simboloDeclaradoNaTabela[2] == TOKEN_INT:
                if type(s) is str and not s.isnumeric():
                    if s not in (LEX_SOMA, LEX_SUB, LEX_MULT, LEX_DIV):
                        if s in (LEX_TRUE, LEX_FALSE):
                            raise Exception(
                                f'Erro sem??ntico: Valor "{s}" n??o pode ser atribu??do a vari??vel num??rica na linha '
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
                                        f'Erro sem??ntico: Retorno da fun????o "{func_decl[4]}" do tipo {func_decl[3]} n??o pode ser atribu??do ?? vari??vel num??rica na linha '
                                        + str(simbolo[1])
                                    )
                            else:
                                raise Exception(
                                    f'Erro sem??ntico: Fun????o "{simbolo[5][1]}" n??o encontrada neste escopo, linha '
                                    + str(simbolo[1])
                                )
                        else:
                            var_decl = self.buscar_var_decl_atrib(simbolo, i, func_context)
                            if var_decl:
                                if var_decl[2] != TOKEN_INT:
                                    raise Exception(
                                        f'Erro sem??ntico: Vari??vel "{var_decl[3]}" do tipo {var_decl[2]} n??o pode ser atribu??do ?? vari??vel num??rica na linha '
                                        + str(simbolo[1])
                                    )
                                else:
                                    continue
                            elif not var_decl:
                                raise Exception(
                                    f'Erro sem??ntico: Vari??vel "{s}" n??o declarada neste escopo, linha '
                                    + str(simbolo[1])
                                )
                            else:
                                raise Exception(
                                    f'Erro sem??ntico: Valor "{s}" n??o pode ser atribu??do a vari??vel num??rica na linha '
                                    + str(simbolo[1])
                                )
                elif type(s) is list:
                    continue

            elif simboloDeclaradoNaTabela[2] == TOKEN_BOOL:
                if s in (LEX_TRUE, LEX_FALSE):
                    continue
                else:
                    var_decl = self.buscar_var_decl_atrib(simbolo, i, func_context)
                    if s.isnumeric():
                        raise Exception(
                            f'Erro sem??ntico: Valor num??rico n??o pode ser atribu??do ?? vari??vel do tipo booleano, linha '
                            + str(simbolo[1])
                        )
                    if var_decl:
                        if var_decl[2] != TOKEN_BOOL:
                            raise Exception(
                                f'Erro sem??ntico: Vari??vel "{var_decl[3]}" do tipo {var_decl[2]} n??o pode ser atribu??do a vari??vel booleana na linha '
                                + str(simbolo[1])
                            )
                        else:
                            continue
                    elif not var_decl:
                        raise Exception(
                            f'Erro sem??ntico: Vari??vel "{s}" n??o declarada neste escopo, linha '
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