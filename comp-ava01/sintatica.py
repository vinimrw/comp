# Bibliotecas para entrada e saida de arquivos
import sys
import os.path
# Bliblioteca padrao de string
import string

# Biblioteca para juncao de tipos iteraveis - nesse caso juncao de dict
#from itertools import chain

# Declarando Classe do Analisador Sintatico
class AnalisadorSintatico():
  # ========================== DECLARACAO DE METODOS DA CLASSE
  # Metodo construtor da classe
  def __init__(self):
    self.arquivo_entrada = "resp-lex.txt"
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

    self.vartab = {}
    self.func_tab = {}
    self.main_tab = {}

  # Faz o cabecote de leitura apontar para o proximo token da lista
  def next_token(self):
    self.i += 1
    self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]

  def conteudo_token(self):
    return self.tokens[self.i][ : self.tokens[self.i].find('->')]







   # <syntax> := <variable_decl><func_decl><main_decl>
  def syntax(self):
    
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1

    self.var_tab = self.variable_decl()
    self.func_tab = self.func_decl()
    self.main_decl()

    if(self.tem_erro_sintatico):
      print("Verifique os erros sintaticos e tente compilar novamente")
      self.arquivo_saida.write("Verifique os erros sintaticos e tente compilar novamente\n")
    else:
      if("$" in self.tokens[self.i]):
        print("Cadeia de tokens na analise sintatica reconhecida com sucesso")
        self.arquivo_saida.write("Cadeia de tokens reconhecida com sucesso\n")
      else:
        print("Fim de Programa Nao Encontrado!")
        self.arquivo_saida.write("Fim de Programa Nao Encontrado!")

    # Fechando arquivo de saida
    self.arquivo_saida.close()




#<declaration> := <type_pri> token_id
  # <declaration> := <type_pri> token_identificador           
  def declaration(self):
    # DECLARACAO DE COMPONENTES PARA SEMANTICO
    # Lista que guarda as informacoes da declaration em questao
    dict_declaracao = {}
    id_declaracao = ""
    tipo_declaracao = ""
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1

    tipo_declaracao = self.type_pri()

    if( 'token500_' in self.tokens[self.i] ):    
      id_declaracao = self.conteudo_token()
      self.next_token()
    else:
      if('token200_;' in self.tokens[self.i]):
        while('token200_;' in self.tokens[self.i]):
          self.next_token()
        print("Erro sintatico - ';' duplicado  - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write("Erro sintatico  - ';' duplicado - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True  
      else:
        print("Erro sintatico - Esperado um 'indentificador'  - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write("Erro sintatico  - Esperado um 'identificador' - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
      while( not 'token200_;' in self.tokens[self.i]):
          self.next_token()

    dict_declaracao[id_declaracao] = tipo_declaracao
    return dict_declaracao


  #P(3) <type_pri> := | int | bool                                                      
  def type_pri(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1

    tipo = ""
    if('token609_int' in self.tokens[self.i] or
      'token610_bool' in self.tokens[self.i]):
      tipo = self.conteudo_token()
      self.next_token()
    else:
      if('token200_;' in self.tokens[self.i]):
        while('token200_;' in self.tokens[self.i]):
          self.next_token()
        self.arquivo_saida.write("Erro sintatico - ';' duplicados:  - linha: "+self.linha_atual+"\n")
        print("Erro sintatico - ';' duplicados "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        print('Token problematico: '+self.tokens[self.i])
        self.tem_erro_sintatico = True
      self.arquivo_saida.write("Erro sintatico - Esperado as palavras reservadas 'int' ou 'bool' - linha: "+self.linha_atual+"\n")
      print("Erro sintatico - Esperado as palavras reservadas 'int' ou 'bool' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      print('Token problematico: '+self.tokens[self.i])
      self.tem_erro_sintatico = True
      while( not 'token500_' in self.tokens[self.i]):
          self.next_token()

    return tipo

#=================================================================


  # P(5) <value_pri> := token_int | true	| false
  def value_pri(self):
    valor_p = ""
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if( 'token300_' in self.tokens[self.i] or 
      'token611_true' in self.tokens[self.i] or
      'token612_false' in self.tokens[self.i]):
      valor_p = self.conteudo_token()
      self.next_token()
    else:
      self.arquivo_saida.write("Erro sintatico - Esperado valor primitivo (numero, verdadeiro ou falso):  - linha: "+self.linha_atual+"\n")
      print("Erro sintatico - Esperado valor primitivo (numero, verdadeiro ou falso):  - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      print('Token problematico: '+self.tokens[self.i])
      self.tem_erro_sintatico = True
      while( not 'token200_;' in self.tokens[self.i]):
        self.next_token()

    return valor_p
             

















































 # <variable_decl> := var { <syntax_var> }                                                        
  def variable_decl(self):
    retorno_variaveis_declaracao = {}
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if( 'token601_var' in self.tokens[self.i]):
      self.next_token()
      if( 'token204_{' in self.tokens[self.i] ):
        self.next_token()
        # Indica que acabou a minha declaration de variaveis
        if( not "token205_}" in self.tokens[self.i] ):
          # Atribuindo as variaveis declaradas como globais pelo usuario
          retorno_variaveis_declaracao = self.syntax_var()
        if( 'token205_}' in self.tokens[self.i] ):
          self.next_token()
        else:
          self.arquivo_saida.write("Erro sintatico - Esperado simbolo '}' ao final do bloco de variaveis - linha: "+self.linha_atual+"\n")
          print("Erro sintatico - Esperado simbolo '}' ao final do bloco de variaveis - linha: "+self.linha_atual+"\n")
          self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
          print('Token problematico: '+self.tokens[self.i])
          self.tem_erro_sintatico = True
          if('token602_func' in self.tokens[self.i] or "token600_main" in self.tokens[self.i]):
            self.next_token()
          while( not 'token602_func' in self.tokens[self.i] or "token600_main" in self.tokens[self.i]):
            self.next_token()
      else:
        print("Erro sintatico - Esperado simbolo '{' apos a declaração de variaveis - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write("Erro sintatico - Esperado simbolo '{' apos a declaração de variaveis - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
        while( not 'token602_func' in self.tokens[self.i] or "token600_main" in self.tokens[self.i]):
          self.next_token()
    else:
      print("Erro sintatico - A declaração do bloco de variaveis, mesmo que vazio, eh obrigatoria nessa linguagem - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write("Erro sintatico - A declaração do bloco de variaveis, mesmo que vazio, eh obrigatoria nessa linguagem - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while( not 'token602_func' in self.tokens[self.i] or "token600_main" in self.tokens[self.i]):
        self.next_token()
    return retorno_variaveis_declaracao
      



  # <syntax_var> := <declaration>; <syntax_var> | token_id token_id; <syntax_var>  | Ɛ
  def syntax_var(self):
    # Irah armazenar as variaveis globais declaradas pelo usuario
    variaveis_globais = {}
    conteudo_variaveis = []

    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1

    # No caso da declaration ser de um tipo registro, espero um identificador
    if( 'token500_' in self.tokens[self.i] ):
      # Armazeno o nome do tipo registro
      tipo_registro = self.conteudo_token() 
      self.next_token()
      if( 'token500_' in self.tokens[self.i] ):
        # armazeno o nome dado pelo usuario para a variavel registro criada
        identificador_registro = self.conteudo_token() 
        self.next_token()
        if( 'token200_;' in self.tokens[self.i] ):
          self.next_token()
          # Coloco o nome da variavel como chave do dicionario
          # O conteudo do dicionario eh uma lista contendo o tipo do registro
          # seguido da frase sem inicializacao, por nao ser premitido inicializar registro,
          # seguido da indicacao que essa variavel eh um registro
          variaveis_globais[identificador_registro] = conteudo_variaveis
          conteudo_variaveis.append(tipo_registro)
          conteudo_variaveis.append("tipo_registro")
          conteudo_variaveis.append("sem_inicilizacao")
          if(not 'token205_}' in self.tokens[self.i] ):
            variaveis_globais.update( self.syntax_var() )
          else:
            return variaveis_globais
        else:
          print("Erro sintatico - Esperado simbolo ';' apos identificador declarado - linha: "+self.linha_atual+"\n")
          print('Token problematico: '+self.tokens[self.i])
          self.arquivo_saida.write("Erro sintatico - Esperado simbolo ';' apos identificador declarado - linha: "+self.linha_atual+"\n")
          self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
          self.tem_erro_sintatico = True
          while( not 'token609_int' in self.tokens[self.i] or
          not 'token610_bool' in self.tokens[self.i] or
          not 'token500_' in self.tokens[self.i]):
            self.next_token()
      else:
        print("Erro sintatico - Esperado identificador declarado - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Erro sintatico - Esperado identificador declarado - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
        while( not 'token609_int' in self.tokens[self.i] or
          not 'token610_bool' in self.tokens[self.i] or
          not   'token500_' in self.tokens[self.i]):
            self.next_token()
    # Em caso da variaveis declarada nao ser um registro, espero um tipo primitivo
    elif(
          'token609_int' in self.tokens[self.i] or
          'token610_bool' in self.tokens[self.i]):
      dict_declaracao = self.declaration()
      chave = list( dict_declaracao.keys() )
      variaveis_globais[ chave[0] ] =  conteudo_variaveis
      conteudo_variaveis.append( dict_declaracao[chave[0]] )

      # Armazena as informacoes especificas de cada variavel declarada
      conteudo_aux = []
      conteudo_aux = self.id_var_aux()
      if(len(conteudo_aux) == 0):
        conteudo_variaveis.append("simples")
        conteudo_variaveis.append("sem_inicilizacao")
      else:
        # Variavel simples
        if(conteudo_aux[0] == 0):
          conteudo_variaveis.append("simples")
          conteudo_variaveis.append(conteudo_aux[1])

      if( 'token200_;' in self.tokens[self.i] ):
        self.next_token()
        if( not 'token205_}' in self.tokens[self.i] ):
          variaveis_globais.update( self.syntax_var() )
        else:
          return variaveis_globais
      else:
        print("Erro sintatico - Esperado simbolo ';' apos a declaração da varavel - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Erro sintatico - Esperado simbolo ';' apos a declaração da varavel - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
        while( 
          not 'token609_int' in self.tokens[self.i] or
          not 'token610_bool' in self.tokens[self.i] or
          not 'token500_' in self.tokens[self.i]):
            self.next_token()
    else:
      if('token200_;' in self.tokens[self.i]):
        while('token200_;' in self.tokens[self.i]):
          self.next_token()
        self.arquivo_saida.write("Erro sintatico - ';' duplicados:  - linha: "+self.linha_atual+"\n")
        print("Erro sintatico - ';' duplicados "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        print('Token problematico: '+self.tokens[self.i])
        self.tem_erro_sintatico = True
      self.arquivo_saida.write("Erro sintatico - Esperado as palavras reservadas 'int' ou 'bool' - linha: "+self.linha_atual+"\n")
      print("Erro sintatico - Esperado as palavras reservadas 'int' ou 'bool' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      print('Token problematico: '+self.tokens[self.i])
      self.tem_erro_sintatico = True
      while( 
          not 'token609_int' in self.tokens[self.i] or
          not 'token610_bool' in self.tokens[self.i] or
          not 'token500_' in self.tokens[self.i] ):
            self.next_token() 

    return variaveis_globais
#x                                 
  def id_var_aux(self):
    retorno_identificador_deriva = []
    vetor_matriz = 0
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('token200_;' in self.tokens[self.i]):
      return retorno_identificador_deriva
    elif('token111_=' in self.tokens[self.i]):
      valor_inicializacao = self.inicializacao()
    else:
      print("Erro sintatico - Esperado '=' - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado '=' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while( not 'token200_;' in self.tokens[self.i]):
        self.next_token()
    return retorno_identificador_deriva                                                        
  def inicializacao(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('token200_;' in self.tokens[self.i]):
      return
    elif('token111_=' in self.tokens[self.i]):
      self.next_token()
      return self.value_pri()





# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================




  #<func_decl> := func <type_return> token_id (<decl_param>)  { <syntax_func>  } <func_decl> 	| Ɛ
  def func_decl(self):
    # guarda o conteudo de todas as funcoes
    tabela_funcao = {}
    # guarda o conteudo da funcao lida no momento
    conteudo_funcao = []
    # guarda os parametros da funcao em ordem de declaration
    param_funcao = []
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    # Caso tenha chegado ao 
    if ("token600_main" in self.tokens[self.i]):
      return tabela_funcao
    elif('token602_func' in self.tokens[self.i]):
      self.next_token()
      # o tipo da funcao eh a primeira coisa da lista de conteudo_funcao
      conteudo_funcao.append( self.type_return() )

      if( 'token500_' in self.tokens[self.i] ):
        nome_funcao = self.conteudo_token()
        # A tabela de funcoes recebe como chave o nome da funcao e possui todo seu conteudo
        tabela_funcao[ nome_funcao ] = conteudo_funcao
        self.next_token()
        if( 'token202_(' in self.tokens[self.i] ):
          self.next_token()
          if(not 'token203_)' in self.tokens[self.i] ):
            # Adicionando parametros da funcao ao conteudo de funcao
            # caso a funcao nao tenha parametros essa celula sera um dicionario vazio
            param_funcao = self.decl_param()

          if( 'token203_)' in self.tokens[self.i] ):
            conteudo_funcao.append( param_funcao )
            self.next_token()
            if( 'token204_{' in self.tokens[self.i] ):
              self.next_token()
              if(not 'token205_}' in self.tokens[self.i] ):
                # passo o nome da funcao para saber com qual funcao estou trabalhando no momento
                self.syntax_func( )
              if( 'token205_}' in self.tokens[self.i] ):
                self.next_token()

                tabela_funcao.update ( self.func_decl() )
              else:
                print("Erro sintatico - Esperado simbolo '}' ao final do bloco da funcao - linha: "+self.linha_atual+"\n")
                print('Token problematico: '+self.tokens[self.i])
                self.arquivo_saida.write("Erro sintatico - Esperado simbolo '}' ao final do bloco da funcao - linha: "+self.linha_atual+"\n")
                self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
                self.tem_erro_sintatico = True
                while(not "token600_main" in self.tokens[self.i] or
                  not 'token602_func' in self.tokens[self.i]):
                  self.next_token()
            else:
              print("Erro sintatico - Esperado simbolo '{' apos o fechamento de parentesis da declaração de parametros da funcao - linha: "+self.linha_atual+"\n")
              print('Token problematico: '+self.tokens[self.i])
              self.arquivo_saida.write("Erro sintatico - Esperado simbolo '{' apos o fechamento de parentesis da declaração de parametros da funcao - linha: "+self.linha_atual+"\n")
              self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
              self.tem_erro_sintatico = True
              while(not "token600_main" in self.tokens[self.i] or
              not 'token602_func' in self.tokens[self.i]):
                self.next_token()
          else:
            print("Erro sintatico - Esperado simbolo ')' ao final da declaração de parametros da funcao - linha: "+self.linha_atual+"\n")
            print('Token problematico: '+self.tokens[self.i])
            self.arquivo_saida.write("Erro sintatico - Esperado simbolo ')' ao final da declaração de parametros da funcao - linha: "+self.linha_atual+"\n")
            self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
            self.tem_erro_sintatico = True
            while( not "token600_main" in self.tokens[self.i] or
            not 'token602_func' in self.tokens[self.i]):
              self.next_token()
        else:
          print("Erro sintatico - Esperado simbolo '(' no início da declaração de parametros da funcao - linha: "+self.linha_atual+"\n")
          print('Token problematico: '+self.tokens[self.i])
          self.arquivo_saida.write("Erro sintatico - Esperado simbolo '(' no início da declaração de parametros da funcao - linha: "+self.linha_atual+"\n")
          self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
          self.tem_erro_sintatico = True
          while("token600_main" in self.tokens[self.i] or
            'token602_func' in self.tokens[self.i]):
            self.next_token()
          while(not "token600_main" in self.tokens[self.i] or
            not 'token602_func' in self.tokens[self.i]):
            self.next_token()
      else:
        print("Erro sintatico - Esperado identificador com o nome da funcao declarada - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Erro sintatico - Esperado identificador com o nome da funcao declarada - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
        while(not "token600_main" in self.tokens[self.i] or
            not 'token602_func' in self.tokens[self.i]):
          self.next_token()
    else:
      print("Erro sintatico - Esperado palavra reservada funcao - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado palavra reservada funcao - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      if("token600_main" in self.tokens[self.i] or
         'token602_func' in self.tokens[self.i]):
        self.next_token()
      while(not "token600_main" in self.tokens[self.i] or
             not 'token602_func' in self.tokens[self.i]):
        self.next_token()

    return tabela_funcao




  # <type_return> := <type_pri>  | void
  def type_return(self):
    tipo_retorno = []
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1

    if( 'token604_void' in self.tokens[self.i] ):
      tipo_retorno.append( self.conteudo_token() )
      tipo_retorno.append( "simples" )
      self.next_token()
    elif ('token500_' in self.tokens[self.i] ):
      tipo_retorno.append( self.conteudo_token() )
      tipo_retorno.append( "registro" )
      self.next_token()
      
    elif( 'token609_int' in self.tokens[self.i] or
          'token610_bool' in self.tokens[self.i]):
      tipo_retorno.append( self.type_pri() )
      var_vetor_matriz = self.identificador_param_deriva()
      if(var_vetor_matriz == 0):
        tipo_retorno.append("simples")

    else:
      print("Erro sintatico - Esperado tipo de retorno da funcao - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado tipo de retorno da funcao - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not 'token500_' in self.tokens[self.i]):
        self.next_token()

    return tipo_retorno









  #P(14) <decl_param> := <declaration>  <deriva_param>
  def decl_param(self):
    # guarda todos os parametros e seus conteudos especificos
    parametros = []
    # guarda os conteudos especificos de cada parametro
    lista_parametro = []
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1

    if ('token500_' in self.tokens[self.i] ):
      # recupero o tipo do parametro - especificamente o tipo registro
      tipo_param = self.conteudo_token()
      self.next_token()
      if ('token500_' in self.tokens[self.i] ):
        # recupero o nome do parametro em questao
        nome_parametro = self.conteudo_token()
        lista_parametro.append (nome_parametro)
        lista_parametro.append( tipo_param )
        lista_parametro.append("registro")
        parametros.append (lista_parametro)
        self.next_token()
        parametros += self.deriva_param()
      else:
        print("Erro sintatico - Esperado identificador declarado como parametro - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Erro sintatico - Esperado identificador declarado como parametro - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
        while(not 'token201_,' in self.tokens[self.i] or
         not 'token203_)' in self.tokens[self.i]):
            self.next_token()
    elif(
      'token609_int' in self.tokens[self.i] or
      'token610_bool' in self.tokens[self.i]):
        dict_declaracao = self.declaration()
        nome_parametro = list ( dict_declaracao.keys() )
        lista_parametro.append ( nome_parametro[0] )
        lista_parametro.append ( dict_declaracao[nome_parametro[0]] )

        var_vetor_matriz = self.identificador_param_deriva()
        if(var_vetor_matriz == 0):
          lista_parametro.append("simples")

        parametros.append (lista_parametro)

        parametros += self.deriva_param()
    else:
      print("Erro sintatico - Esperado tipo primitivo na declaração de parametros - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado tipo primitivo na declaração de parametros - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not 'token201_,' in self.tokens[self.i] or
         not 'token203_)' in self.tokens[self.i]):
        self.next_token()

    return parametros

  def identificador_param_deriva(self):
    var_vetor_matriz = 0
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('token201_,' in self.tokens[self.i] or
        'token203_)' in self.tokens[self.i] or
        'token500_' in self.tokens[self.i] ):
      return var_vetor_matriz
    return var_vetor_matriz





  # <deriva_param> := ,<decl_param> | Ɛ
  def deriva_param(self):
    deriva_return = []
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1

    if('token203_)' in self.tokens[self.i]):
      return deriva_return
    elif('token201_,' in self.tokens[self.i]):
      self.next_token()
      deriva_return += self.decl_param()
    return deriva_return


  #P(18) <syntax_func> := <variable_decl> <commands_decl> return <return_deriva>;   | <commands_decl> return <return_deriva>;
  def syntax_func(self):
    
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1

    if('token601_var' in self.tokens[self.i]):
      # dicionario que guarda as variaveis locais dessa funcao
      variaveis_locais_func = self.variable_decl()
      # o conteudo da funcao possui inicialmente o dicionario de variaveis locais, que pode ser vazio caso nao existam
      self.commands_decl()
      if('token603_return' in self.tokens[self.i]):
        self.next_token()
        self.return_deriva()
        if('token200_;' in self.tokens[self.i]):
          self.next_token()
        else:
          print("Erro sintatico - Esperado simbolo ';' ao final da declaração de retorno da funcao - linha: "+self.linha_atual+"\n")
          print('Token problematico: '+self.tokens[self.i])
          self.arquivo_saida.write("Erro sintatico - Esperado simbolo ';' ao final da declaração de retorno da funcao - linha: "+self.linha_atual+"\n")
          self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
          self.tem_erro_sintatico = True
          while(not 'token205_}' in self.tokens[self.i]):
            self.next_token()
      else:
        print("Erro sintatico - Esperada palavra reservada retorno para indicar que a funcao acabou e esta retornando algo ou vazio - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Erro sintatico - Esperada palavra reservada retorno para indicar que a funcao acabou e esta retornando algo ou vazio - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
        while(not 'token205_}' in self.tokens[self.i]):
          self.next_token()
    elif( 'token605_if' in self.tokens[self.i] or
        'token608_print' in self.tokens[self.i] or
        'token607_while' in self.tokens[self.i] or
        'token500_' in self.tokens[self.i]):
          self.commands_decl()
          if('token603_return' in self.tokens[self.i]):
              self.i += 1
              self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
              self.return_deriva()
          else:
              print("Erro sintatico - Esperada palavra reservada retorno para indicar que a funcao acabou e esta retornando algo ou vazio - linha: "+self.linha_atual+"\n")
              print('Token problematico: '+self.tokens[self.i])
              self.arquivo_saida.write("Erro sintatico - Esperada palavra reservada retorno para indicar que a funcao acabou e esta retornando algo ou vazio - linha: "+self.linha_atual+"\n")
              self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
              self.tem_erro_sintatico = True
              while(not 'token205_}' in self.tokens[self.i]):
                  self.i += 1
                  self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    else:
      print("Erro sintatico - Esperado declaracao de variveis ou declaracao de comandos - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado declaracao de variveis ou declaracao de comandos - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not 'token205_}' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
            
  #<return_deriva> := void	| token_id		| <value_pri>
  def return_deriva(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if( 'token604_void' in self.tokens[self.i]):
      self.next_token()
    elif('token500_' in self.tokens[self.i]):
      self.next_token()
      self.id_param_aux()
    elif(
      'token609_int' in self.tokens[self.i] or
      'token610_bool' in self.tokens[self.i]):
        self.value_pri()
    else:
      print("Erro sintatico - Esperado o retorno da funcao - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado o retorno da funcao - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not 'token200_;' in self.tokens[self.i]):
        self.next_token()

  # <commands_decl> := <commands> <commands_decl>  | Ɛ      
  def commands_decl(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('token603_return' in self.tokens[self.i] or
       'token205_}' in self.tokens[self.i]):
      return
    elif( 'token605_if' in self.tokens[self.i] or
        'token608_print' in self.tokens[self.i] or
        'token607_while' in self.tokens[self.i] or
        'token500_' in self.tokens[self.i]):
      self.commands()
      self.commands_decl()
    else: 
      print("Erro sintatico - Esperado uma atribuicao ou um comando - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado uma atribuicao ou um comando - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not 'token603_return' in self.tokens[self.i] or
       not 'token205_}' in self.tokens[self.i] or
       not 'token605_if' in self.tokens[self.i] or
       not 'token608_print' in self.tokens[self.i] or
       not 'token607_while' in self.tokens[self.i] or
       not 'token500_' in self.tokens[self.i]):
            self.next_token()
      

































  # <commands> := <conditional_if>	| <while_loop>	| <print_statement>		| Ɛ    
  def commands(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if( 'token605_if' in self.tokens[self.i] ):
      self.conditional_if()
    elif( 'token608_print' in self.tokens[self.i] ):
      self.print_statement()
#    elif( 'tok611_leia' in self.tokens[self.i] ):
#      self.leia_declaracao()
    elif( 'token607_while' in self.tokens[self.i] ):
      self.while_loop()
#    elif( 'tok610_para' in self.tokens[self.i] ):
#      self.para_declaracao()
    elif('token500_' in self.tokens[self.i]):
      self.atribuicao()
    else:
      print("Erro sintatico - Esperado uma atribuicao ou um comando - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado uma atribuicao ou um comando - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i] or
            not 'token205_}' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      
  #<atribuicao> := token_id  = <atribuicao_deriva>;
  def atribuicao(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('token500_' in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      self.id_param_aux()
      if('token111_=' in self.tokens[self.i]):
        self.i += 1
        self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
        self.atribuicao_deriva()
        if('token200_;' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
        else:
          print("Erro sintatico - Esperado ';' - linha: "+self.linha_atual+"\n")
          print('Token problematico: '+self.tokens[self.i])
          self.arquivo_saida.write("Erro sintatico - Esperado ';' - linha: "+self.linha_atual+"\n")
          self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
          self.tem_erro_sintatico = True
          while(not 'token605_if' in self.tokens[self.i] or
           not 'token608_print' in self.tokens[self.i] or
           not 'token607_while' in self.tokens[self.i] or
           not 'token500_' in self.tokens[self.i] or
           not 'token603_return' in self.tokens[self.i] or
           not 'token205_}' in self.tokens[self.i]):
              self.i += 1
              self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      else:
        print("Erro sintatico - Esperado '=' - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Erro sintatico - Esperado '=' - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
        while(not 'token605_if' in self.tokens[self.i] or
           not 'token608_print' in self.tokens[self.i] or
           not 'token607_while' in self.tokens[self.i] or
           not 'token500_' in self.tokens[self.i] or
           not 'token603_return' in self.tokens[self.i] or
           not 'token205_}' in self.tokens[self.i]):
              self.i += 1
              self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    else:
      print("Erro sintatico - Esperado uma variavel - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado uma variavel - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or 
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i] or
            not 'token205_}' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]

  #<atribuicao_deriva> := <simple_exp> | <call_func>
  def atribuicao_deriva(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('token500_' in self.tokens[self.i]):
      self.call_func()
    elif('token202_(' in self.tokens[self.i] or
         'token101_+' in self.tokens[self.i] or
         'token102_-' in self.tokens[self.i] or
         'token500_' in self.tokens[self.i] or
         'token300_' in self.tokens[self.i]):
      self.simple_exp()
    else:
      print("Erro sintatico - Esperando uma expressão aritmetica ou uma chamada de funcao - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperando uma expressão aritmetica ou uma chamada de funcao - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not 'token200_;' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
  

  #<call_func> := token_id (<decl_param_call>)
  def call_func(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('token500_' in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      if('token202_(' in self.tokens[self.i]):
        self.i += 1
        self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
        self.decl_param_call()
        if('token203_)' in self.tokens[self.i]):
          self.i += 1
          self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
        else:
          print("Erro sintatico - Esperada simbolo ')' para finalizar bloco de comando <call_func> - linha: "+self.linha_atual+"\n")
          print('Token problematico: '+self.tokens[self.i])
          self.arquivo_saida.write("Erro sintatico - Esperada simbolo ')' para finalizar bloco de comando <call_func> - linha: "+self.linha_atual+"\n")
          self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
          self.tem_erro_sintatico = True
          while(not 'token200_;' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      else:
        print("Erro sintatico - Esperada simbolo '(' para finalizar bloco de comando <call_func> - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Erro sintatico - Esperada simbolo '(' para finalizar bloco de comando <call_func> - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
        while(not 'token200_;' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    else:
      print("Erro sintatico - Esperada simbolo 'token500_' para finalizar bloco de comando <call_func> - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperada simbolo 'token500_' para finalizar bloco de comando <call_func> - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not 'token200_;' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]

  #<decl_param_call> := <decl_call> <call_param_deriva> | Ɛ
  def decl_param_call(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('token203_)' in self.tokens[self.i]):
      return
    elif('token500_' in self.tokens[self.i] or   'token300_' in self.tokens[self.i] or 'tok301_' in self.tokens[self.i]):
      self.decl_call()
      self.call_param_deriva()
    else:
      print("Erro sintatico - Esperando uma expressão aritmetica ou uma chamada de funcao - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperando um numero - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not 'token201_,' in self.tokens[self.i] or
            not 'token203_)' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    
  #<decl_call> := token_identifcador<id_param_aux> | <value_pri>
  def decl_call(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('token500_' in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      self.id_param_aux()
    elif(  'token300_' in self.tokens[self.i] or 'tok301_' in self.tokens[self.i]):
      self.value_pri()
    else:
      print("Erro sintatico - Esperado valores primitvos ou uma variavel - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado valores primitvos ou uma variavel - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not 'token201_,' in self.tokens[self.i]):
        self.i += 1
        self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]

  #<call_param_deriva> := , <decl_param_call> | Ɛ
  def call_param_deriva(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('token203_)' in self.tokens[self.i]):
      return
    elif('token201_,' in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      self.decl_param_call()
    else:
      print("Erro sintatico - Esperado ',' - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado ',' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not 'token201_,' in self.tokens[self.i] or
            not 'token203_)' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
  
  def id_param_aux(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('token200_;' in self.tokens[self.i] or
       'token111_=' in self.tokens[self.i]or
       'token201_,' in self.tokens[self.i] or
       'token202_(' in self.tokens[self.i] or
       'token203_)' in self.tokens[self.i] or
       'token101_+' in self.tokens[self.i] or
       'token102_-' in self.tokens[self.i] or
       'token103_*' in self.tokens[self.i] or
       'token104_/' in self.tokens[self.i] or
       'token105_==' in self.tokens[self.i] or
       'token106_!=' in self.tokens[self.i] or
       'token107_>' in self.tokens[self.i] or
       'token108_>=' in self.tokens[self.i] or
       'token109_<' in self.tokens[self.i] or
       'token110_<=' in self.tokens[self.i] or
       'token500_' in self.tokens[self.i] or
       'token300_' in self.tokens[self.i] or
       'token604_void' in self.tokens[self.i] or
       'token609_int' in self.tokens[self.i] or
       'token610_bool' in self.tokens[self.i]):
          return
    elif("token100_." in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      if("token500_" in self.tokens[self.i]):
        self.i += 1
        self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    elif("tok206_[" in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      self.indice()
      if("tok207_]" in self.tokens[self.i]):
          self.i += 1
          self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
          self.matriz_chamada()
      else:
        print("Erro sintatico - Esperado verifique a linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Esperado verifique a linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
        while(not 'token200_;' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    else:
        print("Erro sintatico - Verifique a linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Verifique a linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
        while(not 'token200_;' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
  def matriz_chamada(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if("token200_;" in self.tokens[self.i]):
      return
    elif("tok206_[" in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      self.indice()
      if("tok207_]" in self.tokens[self.i]):
          self.i += 1
          self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      else:
        print("Erro sintatico - Esperado verifique a linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Esperado verifique a linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
        while(not 'token200_;' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    else:
      print("Erro sintatico - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not 'token200_;' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
  def indice(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('tok207_]' in self.tokens[self.i]):
      return
    if('token300_' in self.tokens[self.i]):
        self.i += 1
        self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    else:
      print("Erro sintatico Verifique a linha - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not 'tok207_]' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]





























  # <conditional_if> := if (<exp_rel_bol>) {<commands_decl>}<else_decl>
  def conditional_if(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if("token605_if" in self.tokens[self.i]):
      self.i += 1
      if("token202_(" in self.tokens[self.i]):
        self.i += 1
        self.exp_rel_bol()
        if("token203_)" in self.tokens[self.i]):
          self.i += 1
          if('token204_{' in self.tokens[self.i]):
            self.i += 1
            self.commands_decl()
            if('token205_}' in self.tokens[self.i]):
              self.i += 1
              self.else_decl()
            else:
              print("Erro sintatico - Esperada simbolo '}'  para finalizar bloco de comando do 'if' - linha: "+self.linha_atual+"\n")
              print('Token problematico: '+self.tokens[self.i])
              self.arquivo_saida.write("Erro sintatico - Esperada simbolo '}'  para finalizar bloco de comando do 'if' - linha: "+self.linha_atual+"\n")
              self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
              self.tem_erro_sintatico = True
              while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
        
          else:
            print("Erro sintatico - Esperada simbolo '{'  para iniciar o bloco de comando do 'if' - linha: "+self.linha_atual+"\n")
            print('Token problematico: '+self.tokens[self.i])
            self.arquivo_saida.write("Erro sintatico - Esperada simbolo '{'  para iniciar o bloco de comando do 'if' - linha: "+self.linha_atual+"\n")
            self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
            self.tem_erro_sintatico = True
            while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
        else:
          print("Erro sintatico - Esperada simbolo ')'  para finalizar a expressão do comando 'if' - linha: "+self.linha_atual+"\n")
          print('Token problematico: '+self.tokens[self.i])
          self.arquivo_saida.write("Erro sintatico - Esperada simbolo ')'  para finalizar a expressão do comando 'if' - linha: "+self.linha_atual+"\n")
          self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
          self.tem_erro_sintatico = True
          while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      else:
        print("Erro sintatico - Esperada simbolo '(' apos o comando se - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Erro sintatico - Esperada simbolo '(' apos o comando se - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
        while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
        
    else:
      print("Erro sintatico - Esperada comando 'if' - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperada comando 'if' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
        
 # <else_decl> := else {<commands_decl>}   | Ɛ
  def else_decl(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('token605_if' in self.tokens[self.i] or
        'token608_print' in self.tokens[self.i] or
        'token607_while' in self.tokens[self.i] or
        'token500_' in self.tokens[self.i] or
        'token603_return' in self.tokens[self.i] or
        'token205_}' in self.tokens[self.i]):
      return
    elif("token606_else" in self.tokens[self.i]):
      self.i += 1
      if('token204_{' in self.tokens[self.i]):
        self.i += 1
        self.commands_decl()
        if('token205_}' in self.tokens[self.i]):
          self.i += 1
        else:
          print("Erro sintatico - Esperada simbolo '}'  para finalizar para finalizar o bloco de comando do 'else' - linha: "+self.linha_atual+"\n")
          print('Token problematico: '+self.tokens[self.i])
          self.arquivo_saida.write("Erro sintatico - Esperada simbolo '}'  para finalizar para finalizar o bloco de comando do 'else' - linha: "+self.linha_atual+"\n")
          self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
          self.tem_erro_sintatico = True
          while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      else:
        print("Erro sintatico - Esperada simbolo '{'  para iniciar o bloco de comando do 'else' - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Erro sintatico - Esperada simbolo '{'  para iniciar o bloco de comando do 'else' - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
        while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    else:
        print("Erro sintatico - Esperado o bloco de comando do 'else' - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Erro sintatico - Esperado o bloco de comando do 'else' - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
        while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      

  # <while_loop> := while (<exp_rel_bol>) { <commands_decl> }
  def while_loop(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if("token607_while" in self.tokens[self.i]):
      self.i += 1
      if("token202_(" in self.tokens[self.i]):
        self.i += 1
        self.exp_rel_bol()
        if("token203_)" in self.tokens[self.i]):
          self.i += 1
          if('token204_{' in self.tokens[self.i]):
            self.i += 1
            self.commands_decl()
            if('token205_}' in self.tokens[self.i]):
              self.i += 1
            else:
              print("Erro sintatico - Esperada simbolo '}'  para finalizar bloco de comando do 'while' - linha: "+self.linha_atual+"\n")
              print('Token problematico: '+self.tokens[self.i])
              self.tem_erro_sintatico = True
              self.arquivo_saida.write("Erro sintatico - Esperada simbolo '}'  para finalizar bloco de comando do 'while' - linha: "+self.linha_atual+"\n")
              self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
              while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
          else:
            print("Erro sintatico - Esperada simbolo '{'  para iniciar o bloco de comando do 'while' - linha: "+self.linha_atual+"\n")
            print('Token problematico: '+self.tokens[self.i])
            self.tem_erro_sintatico = True
            self.arquivo_saida.write("Erro sintatico - Esperada simbolo '{'  para iniciar o bloco de comando do 'while' - linha: "+self.linha_atual+"\n")
            self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
            while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
        else:
          print("Erro sintatico - Esperada simbolo ')'  para finalizar a expressão do comando 'while' - linha: "+self.linha_atual+"\n")
          print('Token problematico: '+self.tokens[self.i])
          self.tem_erro_sintatico = True
          self.arquivo_saida.write("Erro sintatico - Esperada simbolo ')'  para finalizar a expressão do comando 'while' - linha: "+self.linha_atual+"\n")
          self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
          while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      else:
        print("Erro sintatico - Esperada simbolo '(' apos o comando enquanto - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.tem_erro_sintatico = True
        self.arquivo_saida.write("Erro sintatico - Esperada simbolo '(' apos o comando enquanto - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
        
    else:
      print("Erro sintatico - Esperada comando 'while' - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperada comando 'while' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]




  
  
  # <print_statement> := print (<print_syntax>);

  def print_statement(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if("token608_print" in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      if("token202_(" in self.tokens[self.i]):
        self.i += 1
        self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
        self.print_syntax()
        if("token203_)" in self.tokens[self.i]):
          self.i += 1
          self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
          if("token200_;" in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
          else:
            print("Erro sintatico - Espera-se simbolo ';' ao final da chamada de funcao print - linha: "+self.linha_atual+"\n")
            print('Token problematico: '+self.tokens[self.i])
            self.arquivo_saida.write("Erro sintatico - Espera-se simbolo ';' ao final da chamada de funcao print - linha: "+self.linha_atual+"\n")
            self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
            self.tem_erro_sintatico = True
            while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
        else:
          print("Erro sintatico - Espera-se simbolo ')' ao final da declaração de parametros da chamada de funcao print - linha: "+self.linha_atual+"\n")
          print('Token problematico: '+self.tokens[self.i])
          self.arquivo_saida.write("Erro sintatico - Espera-se simbolo ')' ao final da declaração de parametros da chamada de funcao print - linha: "+self.linha_atual+"\n")
          self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
          self.tem_erro_sintatico = True
          while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      else:
        print("Erro sintatico - Espera-se simbolo '(' ao início da declaração de parametros da chamada de funcao print - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Erro sintatico - Espera-se simbolo '(' ao início da declaração de parametros da chamada de funcao print - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
        while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    else:
      print("Erro sintatico - Espera-se palavra reservada escreva para chamada de funcao print - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Espera-se palavra reservada escreva para chamada de funcao print - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not 'token605_if' in self.tokens[self.i] or
         not 'token608_print' in self.tokens[self.i] or
         not 'token607_while' in self.tokens[self.i] or
         not 'token500_' in self.tokens[self.i] or
         not 'token603_return' in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
  
  # <print_syntax> := <exp_print><print_aux><print_syntax>  | Ɛ
  def print_syntax(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if("token203_)" in self.tokens[self.i]):
      return
    elif("token700_" in self.tokens[self.i] or "tok400_" in self.tokens[self.i] or "token500_" in self.tokens[self.i] or "(" in self.tokens[self.i]):
      self.exp_print()
      self.print_aux
      self.print_syntax()
    else:
      print("Erro sintatico - Espera-se uma variavel ou uma constante ou um numero - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Espera-se uma variavel ou uma constante ou um numero - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not "token203_)" in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
 
  # <print_aux> := ,<exp_print> 	| Ɛ
  def print_aux(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if("token203_)" in self.tokens[self.i]):
      return
    elif("token201_," in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      self.exp_print()
    else:
      print("Erro sintatico - Espera-se ',' - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Espera-se ',' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not "token203_)" in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    




























  # <exp_print> := token_cost 	| token_id 	| (<simple_exp>)
  def exp_print(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if("token700_" in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    elif("tok400_" in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    elif("token500_" in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      self.id_param_aux()
    elif("token202_(" in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      self.simple_exp()
      if("token203_)" in self.tokens[self.i]):
        self.i += 1
        self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      else:
        print("Erro sintatico - Esperado simbolo ')' para fechamento de expressões - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Erro sintatico - Esperado simbolo ')' para fechamento de expressões - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
        while(not "token203_)" in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    else:
      print("Erro sintatico - Esperado simbolo '(' para abertura de expressões - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado simbolo '(' para abertura de expressões - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not "token203_)" in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]



























  #<arith_expr> := token_id = <simple_exp>
  def arith_expr(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if("token500_" in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      if("token111_=" in self.tokens[self.i]):
        self.i += 1
        self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
        self.simple_exp()
        if("token200_;" in self.tokens[self.i]):
          self.i += 1
        else:
          print("Erro sintatico - Esperado simbolo (;) ao final do expressão aritmética - linha: "+self.linha_atual+"\n")
          print('Token problematico: '+self.tokens[self.i])
          self.arquivo_saida.write("Erro sintatico - Esperado simbolo (;) ao final do expressão aritmética - linha: "+self.linha_atual+"\n")
          self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
          self.tem_erro_sintatico = True  
      else:  
        print("Erro sintatico - Esperado simbolo '=' para atribuicao de valores a variaveis - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Erro sintatico - Esperado simbolo '=' para atribuicao de valores a variaveis - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
    else:
      print("Erro sintatico - Esperado um identificador representante da variavel que recebera a atribuicao - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado um identificador representante da variavel que recebera a atribuicao - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      
  # <exp_rel_bol> := <simple_exp> <bool_exp> <simple_exp> 	| Ɛ   
  def exp_rel_bol(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    #import pdb; pdb.set_trace() # Break do debbug
    if("token500_" in self.tokens[self.i] or
       "token300_" in self.tokens[self.i] or
       "token202_(" in self.tokens[self.i]):
      self.exp_boll()
      self.op_relacional()
      self.exp_boll()
      self.exp_rel_deriva()
    else:
      print("Erro sintatico - Esperado uma variavel ou um numero ou '(' - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado uma variavel ou um numero ou '(' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not "token203_)" in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]


  #<exp_boll> := <termo><termo_syntax>
  def exp_boll(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if("token500_" in self.tokens[self.i] or
       "token300_" in self.tokens[self.i] or
       "token202_(" in self.tokens[self.i]):
        self.term()
        self.termo_syntax()
    else:
      print("Erro sintatico - Esperado uma variavel ou um numero ou '(' - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado uma variavel ou um numero ou '(' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not "token110_<=" in self.tokens[self.i] or
            not "token108_>=" in self.tokens[self.i] or
            not "token107_>" in self.tokens[self.i] or
            not "token109_<" in self.tokens[self.i] or
            not "token105_==" in self.tokens[self.i] or
            not "token106_!=" in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]


  #<simple_exp> := <ss_token><term><termo_syntax>  | <term><termo_syntax>
  def simple_exp(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if("token101_+" in self.tokens[self.i] or "token102_-" in self.tokens[self.i]):
      self.ss_token()
      self.term()
      self.termo_syntax()
    elif("token500_" in self.tokens[self.i] or
       "token300_" in self.tokens[self.i] or
       "token202_(" in self.tokens[self.i]):
      self.term()
      self.termo_syntax()
    else:
      print("Erro sintatico - Esperado uma variavel ou um numero ou '(' ou '+' ou '-' - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Esperado uma variavel ou um numero ou '(' ou '+' ou '-' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not "token110_<=" in self.tokens[self.i] or
            not "token108_>=" in self.tokens[self.i] or
            not "token107_>" in self.tokens[self.i] or
            not "token109_<" in self.tokens[self.i] or
            not "token105_==" in self.tokens[self.i] or
            not "token106_!=" in self.tokens[self.i] or
            not "token203_)" in self.tokens[self.i] or
            not "token200_;" in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]


  # <op_relacional> := < | > | == | != | <= | >=
  def op_relacional(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if("token110_<=" in self.tokens[self.i] or "token108_>=" in self.tokens[self.i] or "token107_>" in self.tokens[self.i] or "token109_<" in self.tokens[self.i] or "token105_==" in self.tokens[self.i] or "token106_!=" in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    else:
      print("Erro sintatico - Operador relacional era esperado: < | > | == | != | <= | >= - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Operador relacional era esperado: < | > | == | != | <= | >= - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while( not "token500_" in self.tokens[self.i] or
       not "token300_" in self.tokens[self.i] or
       not "token202_(" in self.tokens[self.i] or
             not "token101_+" in self.tokens[self.i] or
             not "token102_-" in self.tokens[self.i]):
          self.i += 1
          self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]

























      
  # <exp_rel_deriva> := <op_bolleano> <simple_exp> <op_relacional> <simple_exp> <exp_rel_deriva> | Ɛ
  def exp_rel_deriva(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if("token203_)" in self.tokens[self.i]):
      return
    elif("tok113_&&" in self.tokens[self.i] or "tok114_||" in self.tokens[self.i]):
#      self.op_bolleano()
      self.simple_exp()
      self.op_relacional()
      self.simple_exp()
      self.exp_rel_deriva()
    else:
      print("Erro sintatico - Esperado operadores '&&' ou '||' - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado uma variavel ou um numero ou '(' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not "token203_)" in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]






























  # <ss_token> := + | -
  def ss_token(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if("token101_+" in self.tokens[self.i] or "token102_-" in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    else:
      print("Erro sintatico - esperado um '+' ou '-' - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - esperado um '+' ou '-' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while( not"token500_" in self.tokens[self.i] or
       not "token300_" in self.tokens[self.i] or
       not "token202_(" in self.tokens[self.i]):
          self.i += 1
          self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]

 # <term> := <factor><factor_syntax>
  def term(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('token500_' in self.tokens[self.i] or 'token300_' in self.tokens[self.i] or 'token202_(' in self.tokens[self.i]):
      self.fator()
      self.fator_deriva()
    else:
      print("Erro sintatico - Esperado um identificador, número inteiro ou simbolo '(' - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado um identificador, número inteiro ou simbolo '(' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while( not "token101_+" in self.tokens[self.i] or
             not "token102_-" in self.tokens[self.i]):
          self.i += 1
          self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
          

 #<termo_syntax> := +<arith_som_syntax>	| -<op_sub_syntax> 	| Ɛ
  def termo_syntax(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if("token110_<=" in self.tokens[self.i] or
             "token108_>=" in self.tokens[self.i] or
             "token107_>" in self.tokens[self.i] or
             "token109_<" in self.tokens[self.i] or
             "token105_==" in self.tokens[self.i] or
             "token106_!=" in self.tokens[self.i] or
             "token203_)" in self.tokens[self.i] or
             "token200_;" in self.tokens[self.i]):
        return
    elif('token101_+' in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      self.op_soma_deriva()
    elif('token102_-' in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      self.op_sub_syntax()
    else:
      print("Erro sintatico - Esperado '+' ou '-' - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado '+' ou '-' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not "token110_<=" in self.tokens[self.i] or
            not "token108_>=" in self.tokens[self.i] or
            not "token107_>" in self.tokens[self.i] or
            not "token109_<" in self.tokens[self.i] or
            not "token105_==" in self.tokens[self.i] or
            not "token106_!=" in self.tokens[self.i] or
            not "token203_)" in self.tokens[self.i] or
            not "token200_;" in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    

 # <factor> := token_id 		| token_int 		| (<simple_exp>) 
  def fator(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('token500_' in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      self.id_param_aux()
    elif('token300_' in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    elif('token202_(' in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      self.simple_exp()
      if('token203_)' in self.tokens[self.i]):
        self.i += 1
        self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      else:
        print("Erro sintatico - Parêntesis desbalanceados - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Erro sintatico - Parêntesis desbalanceados - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
    else: 
      print("Erro sintatico - esperado um identificador, token inteiro, ou (expressão simples) - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - esperado um identificador, token inteiro, ou (expressão simples) - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not "token110_<=" in self.tokens[self.i] or
            not "token108_>=" in self.tokens[self.i] or
            not "token107_>" in self.tokens[self.i] or
            not "token109_<" in self.tokens[self.i] or
            not "token105_==" in self.tokens[self.i] or
            not "token106_!=" in self.tokens[self.i] or
            not "token101_+" in self.tokens[self.i] or
            not "token102_-" in self.tokens[self.i] or
            not "token103_*" in self.tokens[self.i] or
            not "token104_/" in self.tokens[self.i] or
            not "token111_=" in self.tokens[self.i] or
            not "token203_)" in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
  # <fator_deriva> := <MD_token><fator><fator_deriva> | Ɛ
  def fator_deriva(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if("token110_<=" in self.tokens[self.i] or
            not "token108_>=" in self.tokens[self.i] or
            not "token107_>" in self.tokens[self.i] or
            not "token109_<" in self.tokens[self.i] or
            not "token105_==" in self.tokens[self.i] or
            not "token106_!=" in self.tokens[self.i] or
            not "token101_+" in self.tokens[self.i] or
            not "token102_-" in self.tokens[self.i] or
            not "token111_=" in self.tokens[self.i] or
            not "token203_)" in self.tokens[self.i] or
            not "token200_;" in self.tokens[self.i]):
                return
    elif("token103_*" in self.tokens[self.i] or "token104_/" in self.tokens[self.i]):
      self.MD_token()
      self.term()
    else:
      print("Erro sintatico - Esperado '*' ou '/' - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado '*' ou '/' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not "token110_<=" in self.tokens[self.i] or
            not "token108_>=" in self.tokens[self.i] or
            not "token107_>" in self.tokens[self.i] or
            not "token109_<" in self.tokens[self.i] or
            not "token105_==" in self.tokens[self.i] or
            not "token106_!=" in self.tokens[self.i] or
            not "token101_+" in self.tokens[self.i] or
            not "token102_-" in self.tokens[self.i] or
            not "token111_=" in self.tokens[self.i] or
            not "token203_)" in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
  # <op_soma_deriva> := <termo><termo_syntax> | +
  def op_soma_deriva(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('token101_+' in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    elif("token500_" in self.tokens[self.i] or
       "token300_" in self.tokens[self.i] or
       "token202_(" in self.tokens[self.i]):
      self.term()
      self.termo_syntax()
    else:
      print("Erro sintatico - Esperado '+' - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado '+' ou '-' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not "token110_<=" in self.tokens[self.i] or
            not "token108_>=" in self.tokens[self.i] or
            not "token107_>" in self.tokens[self.i] or
            not "token109_<" in self.tokens[self.i] or
            not "token105_==" in self.tokens[self.i] or
            not "token106_!=" in self.tokens[self.i] or
            not "token203_)" in self.tokens[self.i] or
            not "token200_;" in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    
 # <op_sub_syntax> := <term><termo_syntax> | -
  def op_sub_syntax(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('token102_-' in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    elif("token500_" in self.tokens[self.i] or
       "token300_" in self.tokens[self.i] or
       "token202_(" in self.tokens[self.i]):
      self.term()
      self.termo_syntax()
    else:
      print("Erro sintatico - Esperado '-' - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Esperado '+' ou '-' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not "token110_<=" in self.tokens[self.i] or
            not "token108_>=" in self.tokens[self.i] or
            not "token107_>" in self.tokens[self.i] or
            not "token109_<" in self.tokens[self.i] or
            not "token105_==" in self.tokens[self.i] or
            not "token106_!=" in self.tokens[self.i] or
            not "token203_)" in self.tokens[self.i] or
            not "token200_;" in self.tokens[self.i]):
                self.i += 1
                self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    
  #  # <MD_token> := * | /   
  def MD_token(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if("token103_*" in self.tokens[self.i] or "token104_/" in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    else:
      print("Erro sintatico - esperado operador '*' ou '/' - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - esperado operador '*' ou '/' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not "token500_" in self.tokens[self.i] or
       not "token300_" in self.tokens[self.i] or
       not "token202_(" in self.tokens[self.i]):
        self.i += 1
        self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]


  #===========================================================================















































# <main_decl> :=  main {<mais_syntax> }
  def main_decl(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if ("token600_main" in self.tokens[self.i]):
      self.i += 1
      self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      if("token204_{" in self.tokens[self.i]):
        self.i += 1
        self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
        self.main_syntax()
        if("token205_}" in self.tokens[self.i]):
          self.i += 1
          self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
        else:
          print("Erro sintatico - Esperado '}' na declaração de main - linha: "+self.linha_atual+"\n")
          print('Token problematico: '+self.tokens[self.i])
          self.arquivo_saida.write("Erro sintatico - Esperado '}' na declaração de main - linha: "+self.linha_atual+"\n")
          self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
          self.tem_erro_sintatico = True
          while(not "$" in self.tokens[self.i]):
            self.i += 1
            self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
      else:
        print("Erro sintatico - Esperado '{' na declaração de main - linha: "+self.linha_atual+"\n")
        print('Token problematico: '+self.tokens[self.i])
        self.arquivo_saida.write("Erro sintatico - Esperado '{' na declaração de main - linha: "+self.linha_atual+"\n")
        self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
        self.tem_erro_sintatico = True
        while(not "$" in self.tokens[self.i]):
          self.i += 1
          self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    else:
      print("Erro sintatico - Para compilar eh obrigatorio a Declaracao do bloco 'main' - linha: "+self.linha_atual+"\n")
      print('Token problematico: '+self.tokens[self.i])
      self.arquivo_saida.write("Erro sintatico - Para compilar eh obrigatorio a Declaracao do bloco 'main' - linha: "+self.linha_atual+"\n")
      self.arquivo_saida.write('Token problematico: '+self.tokens[self.i]+'\n')
      self.tem_erro_sintatico = True
      while(not "$" in self.tokens[self.i]):
        self.i += 1
        self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
  
  #<main_syntax> := <syntax_var> <commands_decl>		| <commands_decl>		| Ɛ
  def main_syntax(self):
    if("Erro Lexico" in self.tokens[self.i]):
      self.i += 1
    if('token205_}' in self.tokens[self.i]):
      return
    elif("token601_var" in self.tokens[self.i]):
      self.variable_decl()
      self.commands_decl()
    elif('token605_if' in self.tokens[self.i] or
         'token608_print' in self.tokens[self.i] or
         'token607_while' in self.tokens[self.i] or
         'token500_' in self.tokens[self.i] or
         'token603_return' in self.tokens[self.i]):
          self.commands_decl()
    else:
      while('}' in self.tokens[self.i]):
          self.i += 1
          self.linha_atual = self.tokens[self.i][ self.tokens[self.i].find('->')+2: -1]
    # ========================== FIM DO ANALISADOR SINTATICO



##############################################################################
################################## MAIN ######################################
##############################################################################
