### Analisador Lexico ###

# Implementacao do analisador lexico de um compilador
# Cada codigo citado a seguir representa um tipo de token
# Essa codificacao eh usada no arquivo de saida que contem os 
# resultados de operacao do analisador lexico
# tok1 - Operador
#   tok100 - . x
#   tok101 - +
#   tok102 - -
#   tok103 - *
#   tok104 - /
#   tok105 - ++ x
#   tok106 - -- x
#   tok107 - == 
#   tok108 - != 
#   tok109 - >
#   tok110 - >=
#   tok111 - <
#   tok112 - <=
#   tok113 - && x
#   tok114 - || x
#   tok115 - =

# tok2 - Delimitador
#   tok200 - ; x
#   tok201 - , 
#   tok202 - (
#   tok203 - )
#   tok204 - {
#   tok205 - }
#   tok206 - [
#   tok207 - ]

# tok3 - Numero
# tok300 - Numero Inteiro
# tok301 - Numero Real x

# tok400 - Caractere Constante x

# tok500 - Identificador

# tok6 - Palavra reservada
#   tok600 - algoritmo
#   tok601 - variaveis
#   tok602 - constantes
#   tok603 - registro
#   tok604 - funcao
#   tok605 - retorno
    #   tok606 - vazio x
#   tok607 - se
#   tok608 - senao
#   tok609 - enquanto
#   tok610 - para
    #   tok611 - leia x
    #   tok612 - escreva x
#   tok613 - inteiro
    #   tok614 - real x
#   tok615 - booleano
    #   tok616 - char x
    #   tok617 - cadeia x
#   tok618 - verdadeiro
#   tok619 - falso

# tok700 - Cadeia constante
# ========================== ERROS LEXICOS
# Simbolo nao pertencente ao conjunto de simbolos terminais da linguagem
# Identificador Mal formado
# Tamanho do identificador
# Numero mal formado
# Fim de arquivo inesperado (comentario de bloco nao fechado)
# Caractere ou string mal formados
# ==============================================================================

# Bibliotecas para entrada e saida de arquivos
from operator import truediv
import sys
import os.path 

# Bliblioteca padrao de string
import string
from turtle import st

class AnalisadorLexico():
    # DECLARACAO DE METODOS DA CLASSE
    def __init__(self):
        self.arquivo_e = "programa.txt"
        self.arquivo_s = "resposta-lexica.txt"

#######################################

    # Metado para mudar arquivo de entrada
    def mudaEntrada(self, string):
        self.arquivo_e = string

    def getEntrada(self):
        return self.arquivo_e

    def getSaida(self):
        return self.arquivo_s

#######################################

  # Metodo que verifica se a entrada eh um delimitador
  # O metodo find() retorna a posicao do caractere na string de 
  # entrada caso o mesmo seja encontrado

    def ehDelimitador(self, caracter):
        #String com os delimitadores componentes da linguagem 
        delimitadores = ";,(){}[]:="
        if caracter in delimitadores:
            return True
        return False

# Metodo que especifica qual dos tokens delimitadores eh a entrada
    def qualTokenDelimitador(self, entrada):
        #String com os delimitadores componentes da linguagem 
        delimitadores = ";,(){}[]:="
        posicao = delimitadores.find(entrada)
        return "tok20"+str(posicao)

# Metodo que verifica se a entrada eh uma letra
    def ehLetra(self, caracter):
        # (a...z|A...Z)
        letra = string.ascii_letters
        if caracter in letra:
            return True
        return False

# Metrodo que verifica se a entrada eh um digito
    def ehDigito(self, caracter):
        #String com os digitos 0...9
        digito = '0123456789'
        if caracter in digito: 
            return True
        return False

#Metodo que verifica se a entrada eh um simbolo asc_ii
    def ehSimbolo(self, caracter):
        # Strings com os simbolos da tabela ASCII (32 a 126)
        simbolos = ''' !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHJKLMNOPQRSTUVXWYZ[\]^_`abcdefghijklmnopqrstuvxwyz{|}~'''
        if (caracter in simbolos):
            return True
        return False

# Metodo que verifica se a entrada eh um operador
    def ehOperador(self, entrada):
        # Listas com os operadores componentes da linguagem
        operadores = '. + - * / ++ -- == != > >= < <= && || ='.split()
        if entrada in operadores:
            return True
        return False

# Metodo que especifica qual dos tokens operadores eh a entrada
    def qualTokenOperador(self, entrada): 
        operadores = '. + - * / ++ -- == != > >= < <= && || ='.split()
        posicao = 0
        for x in operadores: 
            if x == entrada:
                break
            posicao += 1
        if(posicao > 9):
            return"tok1"+str(posicao)
        else:
            return "tok10"+str(posicao)

# Metodo que verifica se a entrada eh uma palavra reservada
    def ehReservada(self, entrada):
        # Criando Listas para abrigar palavras que serao indexadas por uma mesma letra no dicionario a seguir
        reservadas = "algoritmo variaveis constantes registro funcao retorno vazio se senao enquanto para leia escreva inteiro real booleano char cadeia verdadeiro falso".split()
        if entrada in reservadas:
            return True
        return False

# Metodo que especifica qual dos tokens palavras reservadas eh a entrada
    def qualTokenReservada(self, entrada):

        reservadas = "algoritmo variaveis constantes registro funcao retorno vazio se senao enquanto para leia escreva inteiro real booleano char cadeia verdadeiro falso".split()
        posicao = 0
        for x in reservadas:
            if x == entrada:
                break
            posicao += 1
        if(posicao > 9):
            return "tok6"+str(posicao)
        else:
            return "tok60"+str(posicao)

# Metodo que executa o analsador lexico
    def analisa(self):
        # Abre o arquivo de saida do programa
        arquivo_saida = open(self.arquivo_s, 'w')
        # Verifica se o arquivo de entrada existe no diretorio em questao
        if not os.path.exists(self.arquivo_e):
            arquivo_saida.write("Arquivo de entrada inexistente")
            return

        # Abre o arquivo de entrada do programa
        arquivo = open(self.arquivo_e, 'r')
        # Le a primeira linha
        linha_programa = arquivo.readline()
        # Variavel que indica a linha do caracter_atual
        numero_linha = 1
        # Percorre o programa linha por linha
        while linha_programa:
            i = 0
            tamanho_linha = len(linha_programa)
            while i < tamanho_linha: #Percorre os caracteres da linha
                caracter_atual = linha_programa[i]
                caracter_seguinte = None
            # Soh posso pegar o caractere_seguinte se ele existe na linha
                if ((i+1 < tamanho_linha)):
                    caracter_seguinte = linha_programa[i+1]
# ===================================================================================
                # Verifica se o caracter eh um delimitador - OK
                if (self.ehDelimitador(caracter_atual)):
                    arquivo_saida.write(self.qualTokenDelimitador(caracter_atual)+'_'+caracter_atual +"->"+str(numero_linha)+'\n')
# ===================================================================================               
                # Consumindo comentarios de linha - OK
                elif (caracter_atual == '/' and caracter_seguinte == '/'):
                    #fazendo o programa pular para a proxima linha
                    i = tamanho_linha
                # ===========================================================
                # Consimindo comentario de bloco - Ok
                elif (caracter_atual == '/' and caracter_seguinte == '*'):
                    cont = True #Variavel que impedirah o loop de seguir de continuar caso seja falsa, isso acontece com erro fim inesperado de aquivo
                    linha_comeco = numero_linha #guarda a linha que o bloco comeco, para caso o erro de bloco nao fechado ocorrer o pro grama poderah indicar o comeco do erro

                    while cont and not (caracter_atual == '*' and caracter_seguinte == '/'):
                        #soh posso pegar o caractere atual e o proximo se ele existe na linha 
                        if ((i+2) < tamanho_linha):
                            i += 1
                            caracter_atual = linha_programa[i]
                            caracter_seguinte = linha_programa[i+1]
                        else:
                            linha_programa = arquivo.readline() # le a proxima linha
                            tamanho_linha += len(linha_programa)
                            numero_linha += 1
                            i = -1
                            if (not linha_programa):
                                arquivo_saida.write("Erro lexico - Comentario de bloco nao fechado - linha: %d\n" %linha_comeco)
                                cont = False
                    i += 1 # Faco isso para que nao considere o '/' do final do bloco (na composicao */) no proximo loop
                #==============================================================================
                #Verificando se o elemento eh um operador 
                elif caracter_seguinte != None and self.ehOperador(caracter_atual+caracter_seguinte):
                    arquivo_saida.write(self.qualTokenOperador(caracter_atual+caracter_seguinte)+'_'+caracter_atual+caracter_seguinte+'->'+str(numero_linha)+ '\n')
                    i += 1
                elif self.ehOperador(caracter_atual):
                    arquivo_saida.write(self.qualTokenOperador(caracter_atual)+'_'+caracter_atual+'->'+str(numero_linha)+'\n')

                #====================================================
                # verifica se o elemento em questao eh caractere constante - Ok
                # string.punctuation[6] retorna o simbolo - ' - que representa o inicio do caractere constante
                #elif (caracter_atual == string.punctuation[6]):
                 #   if(linha_programa[i+1] == '\n') or (not (string.punctuation[6] in linha_programa[i+1])):
                  #      arquivo_saida.write('Erro Lexico - Caractere nao fechado - Linha: %d\n' %numero_linha)
                   #     i = tamanho_linha
                    #elif self.ehSimbolo(linha_programa[i+1]) and linha_programa[i+1] != string.punctuation[6] and linha_programa[i+2] == string.punctuation[6]:
                     #   arquivo_saida.write('token400_'+linha_programa[i+1]+'->'+str(numero_linha)+'\n')

                #=========================================

                #verifica se o elemnto em questao eh um numero - ok 
                elif(self.ehDigito(caracter_atual)):
                    string_temp = caracter_atual
                    i += 1
                    j = 0 #vai ocntar se o numero tem pelo menos 1 digito depois do '.'
                    caracter_atual = linha_programa[i]
                    while(self.ehDigito(caracter_atual) and (i+1 < tamanho_linha)):
                        string_temp += caracter_atual
                        i += 1
                        caracter_atual = linha_programa[i]
                    if(caracter_atual == '.'):
                        if ((i+1) < tamanho_linha):
                            string_temp += caracter_atual
                            i +=1
                            caracter_atual = linha_programa[i]
                            while self.ehDigito(caracter_atual) and i+1 <tamanho_linha:
                                j +=1 
                                string_temp += caracter_atual
                                i +=1
                                caracter_atual = linha_programa[i]

                            if(caracter_atual == '.'):
                                j = 0
                                #tratamento de erro, modalidade do desespero
                                while i+1 < tamanho_linha:
                                    i += 1
                                    caracter_atual = linha_programa[i]
                                    if self.ehDelimitador(caracter_atual) or caracter_atual == ' ':
                                        i -= 1 # preciso voltar um elemnto da linha para que o delimitador seja reconhecido no moemnto certo
                                        break
                            else:
                                arquivo_saida.write('Erro lexico - numero mal formado - Linha: %d\n' %numero_linha)

                            if(j>0):
                                arquivo_saida.write('token301_'+string_temp+'->'+str(numero_linha)+'\n')
                            else:
                                arquivo_saida.write('Erro lexico - numero mal formado - Linha %d\n' %numero_linha)
                        else:
                            arquivo_saida.write('tok300_'+string_temp+'->'+str(numero_linha)+'\n')
                            if(not self.ehDigito(caracter_atual)):
                                i -=1
                        ######################################################
                        #verificando identificadores ou palavras reservadas - ok 

                elif(self.ehLetra(caracter_atual)):
                    #apos veririficar que o primeiro caractere da palavra era uma letra, vou percorrer o identificador 
                    #ate encontrar um caractere que nao posse ser de identificadores ou ate o final da linha 
                    string_temp = caracter_atual
                    i += 1
                    algum_erro = False
                    while i< tamanho_linha:
                        caracter_seguinte = None
                        caracter_atual = linha_programa[i]
                        if(i+1 < tamanho_linha):
                            caracter_seguinte = linha_programa[i+1]
                        if(self.ehLetra(caracter_atual) or self.ehDigito(caracter_atual) or caracter_atual == '_'):
                            string_temp += caracter_atual
                        elif(self.ehDelimitador(caracter_atual) or caracter_atual == ' 'or caracter_atual == '\t' or caracter_atual == '\r'):
                            i -= 1 #preciso voltar um elemnto da linha para que o delimitador seja reconhecido no momento certo
                            break
                        elif (caracter_seguinte != None and self.ehOperador(caracter_atual+caracter_seguinte)) or self.ehOperador(caracter_atual):
                            i -=1
                            break
                        elif(caracter_atual != '\n'):
                            arquivo_saida.write("Erro Lexico - identificar com caracter Invalido: " +caracter_atual+"- linha: %d\n" %numero_linha )
                            algum_erro = True
                            break
                        i +=1 #passando o arquivo ate chegar ao final do id/palavra reservada

                    if(algum_erro):
                        while(i+1 < tamanho_linha):
                            i+=1
                            caracter_atual = linha_programa[i]
                            if self.ehDelimitador(caracter_atual) or caracter_atual == ' ' or caracter_atual == '\t' or caracter_atual == '\r' or caracter_atual == '/':
                                i-=1 ##preciso voltar um elemnto da linha para que o delimitador seja reconhecido no momento certo
                                break
                    else: # Se nao houver erros basta verificar se o elemento eh palavra reservada tambem
                        if (self.ehReservada(string_temp)):
                            arquivo_saida.write(self.qualTokenReservada(string_temp)+'_'+string_temp+'->'+str(numero_linha)+'\n')
                        else:
                            arquivo_saida.write('tok500_'+string_temp+'->'+str(numero_linha)+'\n')

                #==========================================================================
                #verifica erro lexico - caracter invalido 
                elif caracter_atual != '\n' and caracter_atual != ' ' and caracter_atual != '\t' and caracter_atual != '\r':
                    arquivo_saida.write('Erro Lexico - Caracter Invalido: ' + caracter_atual + ' - linha: %d\n' %numero_linha)
                # =============================================================
                i += 1

            linha_programa = arquivo.readline() # le a proxima linha
            numero_linha += 1
        #fim do programa
        arquivo_saida.write('$')
        #fim do arquivo de entrada
        arquivo.close()
        #fim do arquivo de saida
        arquivo_saida.close
        #=================================fim do analisar lexico 

#exe
analisador_lexico = AnalisadorLexico()
analisador_lexico.analisa()