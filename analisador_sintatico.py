# Bibliotecas para entrada e saida de arquivos
import sys
import os.path

# Bliblioteca padrao de string
import string

# Biblioteca para juncao de tipos iteraveis - nesse caso juncao de dict
from itertools import chain

class AnalisadorSintatico():
    # ========================== DECLARACAO DE METODOS DA CLASSE
    # Metodo construtor da classe
    def __init__(self):
        self.arquivo_entrada = "resposta-lexica.txt"
        self.arquivo_saida = "resp-sint.txt"

        self.tem_erro_sintatico = False

        self.arquivo_saida = open(self.arquivo_saida, 'w')
        # Verifica se o arquivo de entrada existe no diretorio em questao
        if not os.path.exists(self.arquivo_entrada):
            print("Arquivo de entrada inexistente")
            self.arquivo_saida.write("Arquivo de entrada inexistente")
            return

        # Abre o arquivo de entrada do programa
        self.arquivo = open(self.arquivo_entrada, 'r')
        self.tokens = self.arquivo.readlines()
        self.arquivo.close()
        self.i = 0
        self.j = 0
        self.linha_atual = ""

        # Definindo tabela de simbolos analise semantica
        self.variaveis_globais_tab = {}
        self.funcoes_tab = {}
        self.algoritmo_tab = {}

    # Faz o cabecote de leitura apontar para o proximo token da lista
    def next_token(self):
        self.i += 1
        self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]

    def conteudo_token(self):
        return self.tokens[self.i][ : self.tokens[self.i].find('->')]
        
    # CADA UMA DAS FUNCOES ABAIXO REPRESENTA UMA PRODUCAO DA GRAMATICA
  #
   # O algoritmo basico que foi seguindo para construir as funcoes representa 
    # um analisador sintatico preditivo recursivo, segue o codigo abaixo:
    # void A(){
    #  Escolha uma producao-A, A-> x1, x2, ... , xk 
    #  for(i = 1 ateh k){
    #   if(xi eh um nao terminal){
    #      ativa procedimento xi();
    #    }
    #    else if(xi igual ao simbolo de entrada a){
    #      avance a entrada ao proximo simbolo
    #    }
    #    else{
    #      ocorreu um erro
    #    }
    #  }
    #}
    #

    #P(1) <start> := <variaveis_declaracao><funcao_declaracao><algoritmo_declaracao>
    def start(self):
        if("Erro lexico" in self.tokens[self.i]):
            self.i += 1

        self.variaveis_globais_tab = self.variaveis_declaracao()
        #self.funcoes_tab = self.funcao_declaracao()
        #self.algoritmo_declaracao()

        if(self.tem_erro_sintatico):
            #print("Verifique os erros sintaticos e tente compilar novamente")
            self.arquivo_saida.write("Verifique os erros sintaticos e tente compilar novamente\n")
        else:
            if("$" in self.tokens[self.i]):
                #print("Cadeia de tokens na analise sintatica reconhecida com sucesso")
                self.arquivo_saida.write("Cadeia de tokens reconhecida com sucesso\n")
            else:
                #print("Fim de Programa Nao Encontrado!")
                self.arquivo_saida.write("Fim de Programa Nao Encontrado!")

        #===========================
        #print das tabelas
        #===========================

        #fecha arquivo de saida
        self.arquivo_saida.close()

    #P(6) <declaracao> := <tipo_primitivo> token_identificador
    def declaracao(self):
        dict_declaracao = {}
        id_declaracao = ""
        tipo_declaracao = ""
        if("Erro Lexico" in self.tokens[self.i]):
            self.i += 1
        tipo_declaracao = self.tipo_primitivo()
        if( 'tok500_' in self.tokens[self.i] ):  
            id_declaracao = self.conteudo_token()
            self.next_token()
        else:
            if('tok200_;' in self.tokens[self.i]):
                while('tok200_;' in self.tokens[self.i]):
                    self.next_token()
                #print("Erro sintatico - ';' duplicado  - linha: "+self.linha_atual+"\n")
                self.arquivo_saida.write("Erro sintatico  - ';' duplicado - linha: "+self.linha_atual+"\n")
                self.arquivo_saida.write('Token problemático: '+self.tokens[self.i]+'\n')
                self.tem_erro_sintatico = True  
            else:
                self.arquivo_saida.write("Erro sintatico  - Esperado um 'identificador' - linha: "+self.linha_atual+"\n")
                self.arquivo_saida.write('Token problemático: '+self.tokens[self.i]+'\n')
                self.tem_erro_sintatico = True
            while (not 'tok200_;' in self.tokens[self.i]):
                self.next_token()
        
        dict_declaracao[id_declaracao] = tipo_declaracao
        return dict_declaracao

#P(7) <tipo_primitivo> := | inteiro | booleano
    def tipo_primitivo(self):
        if("Erro Lexico" in self.tokens[self.i]):
            self.i += 1

        tipo =""
        if('tok613_inteiro' in self.tokens[self.i] or
            'tok615_booleano' in self.tokens[self.i]):
            tipo = self.conteudo_token()
            self.next_token()
        else:
            if('tok200_;' in self.tokens[self.i]):
                while('tok200_;' in self.tokens[self.i]):
                    self.next_token()
                self.arquivo_saida.write("Erro sintatico - ';' duplicados:  - linha: "+self.linha_atual+"\n")
                self.arquivo_saida.write('Token problemático: '+self.tokens[self.i]+'\n')
                self.tem_erro_sintatico = True
            self.arquivo_saida.write("Erro sintatico - Esperado as palavras reservadas 'cadeida' ou 'char' ou 'inteiro' ou 'real' ou 'booleano' - linha: "+self.linha_atual+"\n")
            self.arquivo_saida.write('Token problemático: '+self.tokens[self.i]+'\n')
            self.tem_erro_sintatico = True
            while( not 'tok500_' in self.tokens[self.i]):
                self.next_token()
        return tipo

#P(15) <valor_primitivo> := token_inteiro | verdadeiro | falso  | token_cadeia_string
    def valor_primitivo(self):
        valor_p = ""
        if("Erro Lexico" in self.tokens[self.i]):
            self.i += 1
        if( 'tok300_' in self.tokens[self.i] or 'tok700_' in self.tokens[self.i] or 'tok618_verdadeiro' in self.tokens[self.i] or 'tok619_falso' in self.tokens[self.i]):
            valor_p = self.conteudo_token()
            self.next_token()
        else:
            self.arquivo_saida.write("Erro sintatico - Esperado valor primitivo (numero, cadeia, char, verdadeiro ou falso):  - linha: "+self.linha_atual+"\n")
            self.arquivo_saida.write('Token problemático: '+self.tokens[self.i]+'\n')
            self.tem_erro_sintatico = True
            while( not 'tok200_;' in self.tokens[self.i]):
                self.next_token()
        return valor_p

#P(21) <variaveis_declaracao> := variaveis { <declaracao_var> }
    def variaveis_declaracao(self):
        retorno_variaveis_declaracao = {}
        if("Erro Lexico" in self.tokens[self.i]):
            self.i += 1
        if( 'tok601_variaveis' in self.tokens[self.i]):
            self.next_token()
            if( 'tok204_{' in self.tokens[self.i] ):
                self.next_token()
                # Indica que acabou a minha declaracao de variaveis
                if( not "tok205_}" in self.tokens[self.i] ):
                # Atribuindo as variaveis declaradas como globais pelo usuario
                    retorno_variaveis_declaracao = self.declaracao_var()
                if( 'tok205_}' in self.tokens[self.i] ):
                    self.next_token()
                else:
                    self.arquivo_saida.write("Erro sintatico - Esperado símbolo '}' ao final do bloco de variáveis - linha: "+self.linha_atual+"\n")
                    #print("Erro sintatico - Esperado símbolo '}' ao final do bloco de variáveis - linha: "+self.linha_atual+"\n")
                    self.arquivo_saida.write('Token problemático: '+self.tokens[self.i]+'\n')
                    #print('Token problemático: '+self.tokens[self.i])
                    self.tem_erro_sintatico = True
                    if('tok604_funcao' in self.tokens[self.i] or "tok600_algoritmo" in self.tokens[self.i]):
                        self.next_token()
                    while( not 'tok604_funcao' in self.tokens[self.i] or "tok600_algoritmo" in self.tokens[self.i]):
                        self.next_token()
            else:
                #print("Erro sintatico - Esperado símbolo '{' após a declaração de variáveis - linha: "+self.linha_atual+"\n")
                self.arquivo_saida.write("Erro sintatico - Esperado símbolo '{' após a declaração de variáveis - linha: "+self.linha_atual+"\n")
                #print('Token problemático: '+self.tokens[self.i])
                self.arquivo_saida.write('Token problemático: '+self.tokens[self.i]+'\n')
                self.tem_erro_sintatico = True
                while( not 'tok604_funcao' in self.tokens[self.i] or "tok600_algoritmo" in self.tokens[self.i]):
                    self.next_token()
        else:
            #print("Erro sintatico - A declaracao do bloco de variáveis, mesmo que vazio, é obrigatória nessa linguagem - linha: "+self.linha_atual+"\n")
            self.arquivo_saida.write("Erro sintatico - A declaracao do bloco de variáveis, mesmo que vazio, é obrigatória nessa linguagem - linha: "+self.linha_atual+"\n")
            #print('Token problemático: '+self.tokens[self.i])
            self.arquivo_saida.write('Token problemático: '+self.tokens[self.i]+'\n')
            self.tem_erro_sintatico = True
            while( not 'tok604_funcao' in self.tokens[self.i] or "tok600_algoritmo" in self.tokens[self.i]):
                self.next_token()
        # Desse modo garanto escopo de variaveis globais e locais, pois elas chamam essa mesma funcao
        return retorno_variaveis_declaracao

    
    # # <declaracao_var> := <declaracao>; <declaracao_var> | token_identificador token_identificador; <declaracao_var> | Ɛ 
    def declaracao_var(self):
        # Irah armazenar as variaveis globais declaradas pelo usuario
        variaveis_globais = {}
        conteudo_variaveis = []

        if("Erro Lexico" in self.tokens[self.i]):
            self.i += 1

        # No caso da declaração ser de um tipo registro, espero um identificador
        if( 'tok500_' in self.tokens[self.i] ):
            # Armazeno o nome do tipo id
            tipo_registro = self.conteudo_token() 
            self.next_token()
            if( 'tok500_' in self.tokens[self.i] ):
                # armazeno o nome dado pelo usuario para a variavel registro criada
                identificador_registro = self.conteudo_token()
                self.next_token()
                if( 'tok200_;' in self.tokens[self.i] ):
                    self.next_token()
                    # Coloco o nome da variavel como chave do dicionario
                    # O conteudo do dicionario eh uma lista contendo o tipo do registro
                    variaveis_globais[identificador_registro] = conteudo_variaveis
                    conteudo_variaveis.append(tipo_registro)
                    conteudo_variaveis.append("tipo_registro")
                    conteudo_variaveis.append("sem_inicilizacao")
                    if(not 'tok205_}' in self.tokens[self.i] ):
                        variaveis_globais.update( self.declaracao_var() )
                    else:
                       return variaveis_globais
                else:
                    self.arquivo_saida.write("Erro sintatico - Esperado símbolo ';' após identificador nome do tipo registro declarado - linha: "+self.linha_atual+"\n")
                    self.arquivo_saida.write('Token problemático: '+self.tokens[self.i]+'\n')
                    self.tem_erro_sintatico = True
                    while( not 'tok617_cadeia' in self.tokens[self.i] or 
                    not 'tok613_inteiro' in self.tokens[self.i] or
                    not 'tok615_booleano' in self.tokens[self.i] or
                    not 'tok500_' in self.tokens[self.i]):
                        self.next_token()
            else:
                self.arquivo_saida.write("Erro sintatico - Esperado identificador nome do tipo registro declarado - linha: "+self.linha_atual+"\n")
                self.arquivo_saida.write('Token problemático: '+self.tokens[self.i]+'\n')
                self.tem_erro_sintatico = True
                while( not 'tok617_cadeia' in self.tokens[self.i] or 
                not 'tok613_inteiro' in self.tokens[self.i] or
                not 'tok615_booleano' in self.tokens[self.i] or
                not   'tok500_' in self.tokens[self.i]):
                    self.next_token()
        # Em caso da variaveis declarada nao ser um registro, espero um tipo primitivo
        elif('tok617_cadeia' in self.tokens[self.i] or 
            'tok613_inteiro' in self.tokens[self.i] or
            'tok615_booleano' in self.tokens[self.i]):
            dict_declaracao = self.declaracao()
            chave = list( dict_declaracao.keys() )
            variaveis_globais[ chave[0] ] =  conteudo_variaveis
            conteudo_variaveis.append( dict_declaracao[chave[0]] )
            # Armazena as informacoes especificas de cada variavel declarada
            conteudo_aux = []
            #conteudo_aux = self.identificador_deriva()
            if(len(conteudo_aux) == 0):
                conteudo_variaveis.append("simples")
                conteudo_variaveis.append("sem_inicilizacao")
            else:
                # Variavel simples
                if(conteudo_aux[0] == 0):
                    conteudo_variaveis.append("simples")
                    conteudo_variaveis.append(conteudo_aux[1])
    
            if( 'tok200_;' in self.tokens[self.i] ):
                self.next_token()
                if( not 'tok205_}' in self.tokens[self.i] ):
                    variaveis_globais.update( self.declaracao_var() )
                else:
                    return variaveis_globais
            else: 
                self.arquivo_saida.write("Erro sintatico - Esperado símbolo ';' após a declaração da varável simples, vetor ou matriz - linha: "+self.linha_atual+"\n")
                self.arquivo_saida.write('Token problemático: '+self.tokens[self.i]+'\n')
                self.tem_erro_sintatico = True
                while( not 'tok617_cadeia' in self.tokens[self.i] or 
                not 'tok613_inteiro' in self.tokens[self.i] or
                not 'tok615_booleano' in self.tokens[self.i] or
                not 'tok500_' in self.tokens[self.i]):
                    self.next_token()
        else:
            if('tok200_;' in self.tokens[self.i]):
                while('tok200_;' in self.tokens[self.i]):
                    self.next_token()
                    self.arquivo_saida.write("Erro sintatico - ';' duplicados:  - linha: "+self.linha_atual+"\n")
                    self.arquivo_saida.write('Token problemático: '+self.tokens[self.i]+'\n')
                    self.tem_erro_sintatico = True
            self.arquivo_saida.write("Erro sintatico - Esperado as palavras reservadas 'cadeida' ou 'char' ou 'inteiro' ou 'real' ou 'booleano' ou Tipo de Registro - linha: "+self.linha_atual+"\n")
            print("Erro sintatico - Esperado as palavras reservadas 'cadeida' ou 'char' ou 'inteiro' ou 'real' ou 'booleano' ou Tipo de Registro - linha: "+self.linha_atual+"\n")
            self.arquivo_saida.write('Token problemático: '+self.tokens[self.i]+'\n')
            print('Token problemático: '+self.tokens[self.i])
            self.tem_erro_sintatico = True
            while( not 'tok617_cadeia' in self.tokens[self.i] or 
          not 'tok613_inteiro' in self.tokens[self.i] or
          not 'tok615_booleano' in self.tokens[self.i] or
          not 'tok500_' in self.tokens[self.i] ):
                self.next_token()

            return variaveis_globais

        







analisador_sintatico = AnalisadorSintatico()
analisador_sintatico.start()

    