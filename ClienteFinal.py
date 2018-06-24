import socket
import threading
import time
import re

# LEIA A MENSAGEM NO FINAL DO ARQUIVO DO SERVIDOR ANTES DE TUDO, POR FAVOR

# função que pega uma certa palavra de um dado texto
def getWords(text):
    return re.compile('\w+').findall(text)

tLock = threading.Lock()
shutdown = False
private = False
nome = None
messagem = None

# threade que recebe as mensagens do servidor
# além de receber as mensagens, ela verifica qual mensagem ta sendo recebida pra
# caso seja uma mensagem "especial", fazer tal coisa
def receving(name, sock):
    while not shutdown:
        try:
            tLock.acquire()
            while True:
                data, addr = sock.recvfrom(1024)
                # print (str(data))s
                # if ""

                # por exemplo aqui, que quando a pessoa recebe uma mensagem com "quer iniciar um cart privado com voce"
                # ela bota o private pra True e tal. Aí é comunicação direta com o servidor
                # pra ver como essas mensagens tao chegando aqui, tem que olhar no servidor
                if "quer iniciar um chat privado com voce" in str(data):
                    global private
                    if private == False: 
                        private = True
                        global nome
                        nome = getWords(data)[0]
                    # print nome
                        print (str(data))
                elif "/Servidor Cheio" in str(data):
                    print (str(data))
                    print "Tente novamente mais tarde"
                    s.close()
                    
                elif "/nao" in (str(data)):
                    print ("Voce nao aceitou o pedido")
                elif "Aceitou pedido de chat privado" in str(data):
                    print (str(data))
                    # nome = getWords(data)[0]
                    private = True
                elif "saiu do privado com" in str(data):
                    private = False
                    nome = None
                elif private == True:
                    if "em privado para" in str(data):
                        print (str(data))
                else: 
                    print (str(data))
        except:
            pass
        finally:
            tLock.release()

# inicializando as paradinhas básicas. Socket e thread
host = ''
port = 0
server = ('192.168.25.53',5000)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.setblocking(0)

rT = threading.Thread(target=receving, args=("RecvThread",s))
rT.start()
print 'Por favor, digite seu nome sem espacos ou underlines'
alias = raw_input("Name: ")
while ' ' in alias or "_" in alias:
    if ' ' in alias or "_" in alias:
        print "Erro, tente novamente sem espacos ou underlines: "
    alias = raw_input("Name: ")
s.sendto(alias + " entrou no chat", server)
message = (raw_input())

# entra no while principal de envio de mensagens
# nesse while é onde ocorre o envio das mensagens e, de novo,
# dependendo da mensagem escrita, a gente seta algumas coisas
while message != '/quit':
        if message != '':
            s.sendto(alias + ": " + message, server)
            if private == False:
                message = raw_input()

            # por exemplo aqui, que, se a mensagem escrita tiver "private ", a gente pega o segundo nome
            # e seta a variável nome pra essa seunga palavra da mensagem
            # quando é aceito o pedido de privado (lá em cima), botando private pra True, a gente vai pro
            # outro while la embaixo
            if "/private " in str(message):
                nome = getWords(message)[1]

            if "/sim" in str(message):
                if nome != None:
                    s.sendto(alias + ": Aceitou pedido de chat privado de " + nome, server)
                    private = True

            if "/nao" in str(message):
                if nome != None:
                    s.sendto(alias +" : Nao aceitou o pedido de chat privado de " + nome, server)
                    private = False
                    nome = None

            if '/quit' in str(message):
                print "voce saiu do chat"
                s.sendto(alias + " se desconectou do chat.", server)
                s.close()
                shutdown = True
            # esse é o while pra mensagens privadas. A gente manda pro servidor "tal" enviou em privado pra "tal2"
            # e assim o servidor identifica quem ta mandando e pra quem ta mandando
            while private == True:
                s.sendto(alias + " em privado para " + nome + ": " + message, server)
                message = raw_input()
                if "/pvquit" in str(message):
                    if nome != None:
                        s.sendto(alias + " saiu do privado com " + nome, server)
                        private = False
                        nome = None
            time.sleep(0.2)

shudown = True
socket.shutdown(socket.SHUT_WR)
rT.join()
s.close()
