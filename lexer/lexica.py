
class Token:
    def __init__(self, tipo, lexema, linha):
        self.tipo = tipo
        self.lexema = lexema
        self.linha = linha

    def __str__(self):
        return "Linha: %s\n %s\n" % (str(self.linha), str(self.tipo))

class Scanner:

    def __init__(self, programa):
        self.inicio = 0
        self.atual = 0
        self.linha = 1
        self.tokens = []
        self.programa = programa

    def nextChar(self):
        self.atual += 1
        return self.programa[self.atual - 1]  #

    def scan(self):
        self.scanTokens()
        self.scanReserved()
        return self.tokens

    def scanTokens(self):
        while self.atual < len(self.programa):
            self.inicio = self.atual
            char = self.nextChar()
            
            if char == " " or char == "\t" or char == "\r":
                pass

            elif char == "\n":
                self.linha += 1           

            elif char == "(" or char == ")" or char == "{" or char == "}":
                self.tokens.append(
                    Token(
                        self.delimitadoresToken(char),
                        self.programa[self.inicio : self.atual],
                        self.linha,
                    )
                )

            elif char == "+" or char == "-" or char == "*" or char == "/":
                self.tokens.append(
                    Token(
                        self.opAritmeticaToken(char),
                        self.programa[self.inicio : self.atual],
                        self.linha,
                    )
                )

            elif char == "=" or char == "!" or char == "<" or char == ">":
                self.tokens.append(
                    Token(
                        self.opBolleanaToken(char),
                        self.programa[self.inicio : self.atual],
                        self.linha,
                    )
                )

            elif char == ";":  
                self.tokens.append(
                    Token(
                        "token200_;", self.programa[self.inicio : self.atual], self.linha
                    )
                )

            elif char == ",":  
                self.tokens.append(
                    Token("token201_,", self.programa[self.inicio : self.atual], self.linha)
                )

        
            elif char >= "0" and char <= "9":
                while self.lookAhead() >= "0" and self.lookAhead() <= "9":
                    self.nextChar()
                self.tokens.append(
                    Token("token300_Num", self.programa[self.inicio : self.atual], self.linha)
                )

            elif char.isalpha():
                while self.lookAhead().isalnum():
                    self.nextChar()
                self.tokens.append(
                    Token("token500_Id", self.programa[self.inicio : self.atual], self.linha)
                )

            else:
                raise Exception(
                    f"Erro léxico: Caractere {char} inválido na linha "
                    + str(self.linha)
                )

    def delimitadoresToken(self, char):
        
        if char == "(":  
            return "token202_("

        elif char == ")":  
            return "token203_)"

        elif char == "{":  
            return "token204_{"

        elif char == "}":  
            return "token205_}"

    def opAritmeticaToken(self, char):

        if char == "+":  
            return "token101_+"

        elif char == "-": 
            return "token102_-"

        elif char == "*": 
            return "token103_*"

        elif char == "/":  
            return "token104_/"

    def opBolleanaToken(self, char):

        if char == "=":  
            if self.lookAhead() == "=":  
                self.atual += 1
                return "token105_=="

            else: 
                return "token111_="

        elif char == "!":  
            if self.lookAhead() == "=":
                self.atual += 1
                return "token106_!="


        elif char == ">":  
            if self.lookAhead() == "=": 
                self.atual += 1
                return "token108_>="
            else: 
                return "token107_>"

        elif char == "<":  
            if self.lookAhead() == "=": 
                self.atual += 1
                return "token110<="

            else:  
                return "token109_<"

    def scanReserved(self):
        for i in self.tokens:
            if i.tipo == "token500_Id":

                if i.lexema == "main":
                    i.tipo = "token600_main"

                elif i.lexema == "endmain":
                    i.tipo = "token601_endmain"

                elif i.lexema == "func":
                    i.tipo = "token602_func"
                
                elif i.lexema == "endfunc":
                    i.tipo = "token602_endfunc"
                
                elif i.lexema == "return":
                    i.tipo = "token603_return"

                elif i.lexema == "call":
                    i.tipo = "token604_call"

                elif i.lexema == "if":
                    i.tipo = "token605_if"

                elif i.lexema == "endif":
                    i.tipo = "token605_endif"

                elif i.lexema == "else":
                    i.tipo = "token606_else"

                elif i.lexema == "endelse":
                    i.tipo = "token606_endelse"

                elif i.lexema == "while":
                    i.tipo = "token607_while"

                elif i.lexema == "endwhile":
                    i.tipo = "token607_endwhile"

                elif i.lexema == "print":
                    i.tipo = "token608_print"

                elif i.lexema == "break":
                    i.tipo = "token613_break"

                elif i.lexema == "continue":
                    i.tipo = "token614_cont"

                elif i.lexema == "int":
                    i.tipo = "token609_int"

                elif i.lexema == "bool":
                    i.tipo = "token610_bool"

                elif i.lexema == "True":
                    i.tipo = "token611_boolValue"

                elif i.lexema == "False":
                    i.tipo = "token611_boolValue"

                elif i.lexema == "proc":
                    i.tipo = "token615_proc"

                elif i.lexema == "endproc":
                    i.tipo = "token615_endproc"


    def lookAhead(self):
        if self.atual < len(self.programa):
            return self.programa[self.atual]
        else:
            return "\0"













