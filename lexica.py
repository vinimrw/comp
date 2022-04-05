# Bibliotecas para entrada e saida de arquivos
import sys
import os.path
# Bliblioteca padrao de string
import string

# Declarando Classe do analisador Lexico
class AnalisadorLexico():

  # Metodo construtor da classe
  def __init__(self):
    self.arquivo_e = "programa.txt"
    self.arquivo_s = "resp-lex.txt"

  # Metodo para mudar arquivo de entrada
  def mudaEntrada(self, string):
    self.arquivo_e = string

  def getEntrada(self):
    return self.arquivo_e

  def getSaida(self):
    return self.arquivo_s

  # Metodo que verifica se a entrada eh um delimitador ;,(){}
  def ehDelimitador(self, caracter):
    delimitadores = ";,(){}"
    if caracter in delimitadores:
      return True
    return False

  # Metodo que especifica qual dos tokens delimitadores eh a entrada
  def qualTokenDelimitador(self, entrada):
    delimitadores = ";,(){}"
    posicao = delimitadores.find(entrada)
    return "token20"+str(posicao)

  # Metodo que verifica se a entrada eh uma letra
  def ehLetra (self, caracter):
    # String com as letras componentes da linguagem (a..z|A..Z)
    letra = string.ascii_letters
    if caracter in letra:
      return True
    return False

  # Metodo que verifica se a entrada eh um digito
  def ehDigito (self, caracter):
    digito = '0123456789'
    if caracter in digito:
      return True
    return False

  # Metodo que verifica se a entrada eh um simbolo asc_ii
  def ehSimbolo(self, caracter):
    # Strings com os simbolos da tabela ASCII (32 a 126)
    simbolos = ''' !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHJKLMNOPQRSTUVXWYZ[\]^_`abcdefghijklmnopqrstuvxwyz{|}~'''
    if(caracter in simbolos):
      return True
    return False

  # Metodo que verifica se a entrada eh um operador
  def ehOperador(self, entrada):
    operadores = '. + - * / == != > >= < <= ='.split()
    if entrada in operadores:
      return True
    return False
  
  # Metodo que especifica qual dos tokens operadores eh a entrada
  def qualTokenOperador(self, entrada):
    operadores = '. + - * / == != > >= < <= ='.split()
    posicao = 0
    for x in operadores:
      if x == entrada:
        break
      posicao += 1
    if(posicao > 9):
      return "token1"+str(posicao)
    else:
      return "token10"+str(posicao)

  # Metodo que verifica se a entrada eh uma palavra reservada
  def ehReservada(self, entrada):
    reservadas = "main var func return void if else while print int bool true false".split()
    if entrada in reservadas:
      return True
    return False

  # Metodo que especifica qual dos tokens palavras reservadas eh a entrada
  def qualTokenReservada(self, entrada):
    reservadas = '''main var func return void if else while print int bool true false'''.split()
    posicao = 0
    for x in reservadas:
      if x == entrada:
        break
      posicao += 1
    if(posicao > 9):
      return "token6"+str(posicao)
    else:
      return "token60"+str(posicao)

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
      while i < tamanho_linha: 
        caracter_atual = linha_programa[i] 
        caractere_seguinte = None
        if ((i+1) < tamanho_linha):
          caractere_seguinte = linha_programa[i+1] 

        # Verifica se o caracter eh um delimitador 
        if (self.ehDelimitador(caracter_atual)):
          arquivo_saida.write(self.qualTokenDelimitador(caracter_atual)+'_'+caracter_atual+'->'+str(numero_linha)+'\n')

        # Consumindo comentarios de linha 
        elif (caracter_atual == '/' and caractere_seguinte == '/'):
          # Fazendo o programa pular para a proxima linha
          i = tamanho_linha

        # Consumindo comentarios de bloco 
        elif (caracter_atual == '/' and caractere_seguinte == '*'):
          #A caso a variavel vire false significa que nao foi achado o final do comentario de bloco
          cont = True       
          linha_comeco = numero_linha 
          while cont and not (caracter_atual == '*' and caractere_seguinte == '/'):
            # Soh posso pegar o caractere atual e o proximo se ele existe na linha
            if ((i+2) < tamanho_linha):
              i += 1
              caracter_atual = linha_programa[i]
              caractere_seguinte = linha_programa[i+1]                   
            else:
              linha_programa = arquivo.readline()
              tamanho_linha = len(linha_programa)
              numero_linha += 1
              i = -1
              if (not linha_programa):
                arquivo_saida.write ("Erro Lexico - Comentario de bloco nao fechado - linha: %d\n" %linha_comeco)
                cont = False
          i += 1 
    
        # Verificando se o elemento eh um operador
        elif caractere_seguinte != None and self.ehOperador(caracter_atual+caractere_seguinte):
          arquivo_saida.write(self.qualTokenOperador(caracter_atual+caractere_seguinte)+'_'+caracter_atual+caractere_seguinte+'->'+str(numero_linha)+'\n')
          i += 1
        elif self.ehOperador(caracter_atual):
          arquivo_saida.write(self.qualTokenOperador(caracter_atual)+'_'+caracter_atual+'->'+str(numero_linha)+'\n')


        # Verificando se o elemento em questao eh cadeia constante onde string.punctuation[1] retorna o simbolo - "
        elif (caracter_atual == string.punctuation[1]):
          i+=1 # Para passar a primeira ocorrencia do caractere "
          ehValido = True
          # Se a linha soh contem uma ocorrencia de ", significa que a string nao foi fechada
          if (linha_programa[i:].find(string.punctuation[1]) == -1):
            arquivo_saida.write('Erro Lexico - Constante nao fechada - Linha: %d\n' %numero_linha)
            i = tamanho_linha
          else:
            fim_cadeia = i+linha_programa[i:].find(string.punctuation[1])
            nova_cadeia = linha_programa[i:fim_cadeia]
            i = fim_cadeia
            for x in nova_cadeia:
              if(not self.ehSimbolo(x)):
                ehValido = False
                arquivo_saida.write('Erro Lexico - Constante com simbolo invalido (Nao ascii) - Linha: %d\n' %numero_linha)
                break
            if(ehValido):
              arquivo_saida.write('token700_'+nova_cadeia+'->'+str(numero_linha)+'\n')


        # Verificando se o elemento em questao eh um numero 
        elif (self.ehDigito(caracter_atual)):
          string_temp = caracter_atual
          i += 1
          j = 0 # Vai contar se o numero tem pelo menos 1 digito depois do '.'
          caracter_atual = linha_programa[i]
          while (self.ehDigito(caracter_atual) and (i+1 < tamanho_linha)):
            string_temp += caracter_atual
            i += 1
            caracter_atual = linha_programa[i]

          if (caracter_atual == '.'):
            if ((i+1) < tamanho_linha):
              string_temp += caracter_atual
              i += 1
              caracter_atual = linha_programa[i]
              while self.ehDigito(caracter_atual) and i+1 < tamanho_linha:
                j += 1
                string_temp += caracter_atual
                i += 1
                caracter_atual = linha_programa[i]

              if(caracter_atual == '.'):
                j = 0
                # Tratamento de erro, modalidade do desespero
                while (i+1 < tamanho_linha):
                  i += 1
                  caracter_atual = linha_programa[i]
                  if self.ehDelimitador(caracter_atual) or caracter_atual == ' ':
                    i -= 1 # Preciso voltar um elemento da linha para que o delimitador seja reconhecido no momento certo
                    break
            else:
              arquivo_saida.write('Erro Lexico - Numero mal formado - Linha: %d\n' %numero_linha)

            if (j > 0):
              arquivo_saida.write('token301_'+string_temp+'->'+str(numero_linha)+'\n')
            else: 
              arquivo_saida.write('Erro Lexico - Numero mal formado - Linha: %d\n' %numero_linha)
          else:
            arquivo_saida.write('token300_'+string_temp+'->'+str(numero_linha)+'\n')
            if(not self.ehDigito(caracter_atual)):
              i -= 1

        # Verificando identificadores ou palavras reservadas 
        elif (self.ehLetra(caracter_atual)):
          # Apos verificar que o primeiro caractere da palavra era uma letra, vou percorrendo o identificador
          # ateh encontrar um caractere que nao possa ser de identificadores ou ateh o final da linha
          string_temp = caracter_atual
          i += 1
          algum_erro = False
          while i < tamanho_linha:
            caractere_seguinte = None
            caracter_atual = linha_programa[i]
            if(i+1 < tamanho_linha):
              caractere_seguinte = linha_programa[i+1]
            if (self.ehLetra(caracter_atual) or self.ehDigito(caracter_atual) or caracter_atual == '_'):
              string_temp += caracter_atual
            elif (self.ehDelimitador(caracter_atual) or caracter_atual == ' ' or caracter_atual == '\t' or caracter_atual == '\r'):
              i -= 1 
              break
            elif(caractere_seguinte != None and self.ehOperador(caracter_atual+caractere_seguinte)) or self.ehOperador(caracter_atual):
              i-=1
              break
            elif caracter_atual != '\n':
              arquivo_saida.write("Erro Lexico - Identificador com caracter invalido: "+caracter_atual+" - linha: %d\n" %numero_linha)
              algum_erro = True
              break
            i += 1 
            
          if (algum_erro):
            while (i+1 < tamanho_linha):
              i += 1
              caracter_atual = linha_programa[i]
              if self.ehDelimitador(caracter_atual) or caracter_atual == ' ' or caracter_atual == '\t' or caracter_atual == '\r' or caracter_atual == '/':
                i -= 1 
                break
          else: # Se nao houver erros basta verificar se o elemento eh palavra reservada tambem
            if (self.ehReservada(string_temp)):
              arquivo_saida.write(self.qualTokenReservada(string_temp)+'_'+string_temp+'->'+str(numero_linha)+'\n')
            else:
              arquivo_saida.write('token500_'+string_temp+'->'+str(numero_linha)+'\n')
          

        # Verificando Caracter Invalido
        elif caracter_atual != '\n' and caracter_atual != ' ' and caracter_atual != '\t' and caracter_atual != '\r':
          arquivo_saida.write('Erro Lexico - Caracter Invalido: - linha: %d\n' %numero_linha)


        i += 1 # Incrementando a leitura dos caracteres da linha lida no momento


      linha_programa = arquivo.readline() # Le a proxima linha
      numero_linha += 1


##############################################################################
################################## MAIN ######################################
##############################################################################

    # Fim do programa
    arquivo_saida.write('$')
    # Fim do arquivo de entrada
    arquivo.close()
    # Fim do arquivo de entrada
    arquivo_saida.close

# Executando o programa

analisador_lexico = AnalisadorLexico()
analisador_lexico.analisa()
