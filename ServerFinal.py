import socket
import time
import re
import threading
import sys

# LEIA O COMENTÁRIO DO FINAL DESSE ARQUIVO

tLock = threading.Lock()
shutdown = False
filtro = False
nome = None
All = True

def getWords(text):
    return re.compile('\w+').findall(text)


# aqui é a thread dos comandos de filtro
# faz umas paradas dependendo do que você mandar
def comandos():
    while not shutdown:
        try:
            tLock.acquire()
            while True:    
                comando = raw_input()
                # por exemplo, se digitar "/showprivate tal", vai ativar o filtro de privadas pra tal
                if "/showprivate " in str(comando):
                    global All
                    All = False
                    global filtro
                    filtro = True
                    global nome
                    nome = getWords(comando)[1]
                    print ("Mostrando mensagens privadas de " + nome)
                elif "/showpublic" in str(comando):
                    All = False
                    filtro = False
                    print ("Mostrando mensagens publicas")
                elif "/showclients" in str(comando):
                    index6 = 0
                    for client in clients:
                        print clients[index6] + " de nome " + alias[index6]
                        index6 = index6 + 1
                elif "/showall" in str(comando):
                    All = True
                    filtro = False
                    print ("Mostrando todas as mensagens")
                elif "/quit" in str(comando):
                    global quitting
                    quitting = False
                    print ("Servidor fechado")
                    s.close()
        except:
            pass
        finally:
            tLock.release()

host = '192.168.25.53'
port = 5000

clients = []
alias = []
teste = 0

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host,port))
s.setblocking(0)

rT = threading.Thread(target=comandos, args=())
rT.start()

quitting = False
print "Server Started."
# aqui é o while que a gente recebe as mensagens dos clientes
while not quitting:
    try:
        clientes = 0
        for client in clients:
            clientes = clientes + 1
        # verifica quantidade limite de conexões (bugado, não soube fazer mas só buga depois de atingir o limite)
        # daniel, a função socket.listen() é só pra TCP, não funciona aqui
        if clientes <= 15:
            # print len(clients)
            # recebe, na porta 1024 (?) o ip+porta do socket que ta chegando + o que ta chegando
            data, addr = s.recvfrom(1024)
            # se agum cliente enviar /cavalovoador, o servidor fecha
            if "/cavalovoador" in str(data):
                quitting = True
            # aqui a gente joga o cliente numa lista de clientes e numa lista de nomes(alias)
            # pra pode haver a identificação através dos nicknames de quem está no servidor, não através do ip/porta
            # mais intuitivo/fácil pra quem for usar
            if addr not in clients:
                    clients.append(addr)
                    alias.append(getWords(data)[0])
                    print time.ctime(time.time()) + ": " + getWords(data)[0] + " se conectou"
            elif All == True:
                print time.ctime(time.time()) + str(addr) + ":" + str(data)
            # a partir daqui a gente basicamente lê a mensagem que chegou e, se for uma mensagem "especial"
            # a gente envia só pra quem deve receber.
            if '/private' in str(data):
                index = 0
                for alia in alias:
                    if alia == getWords(data)[2]:
                        s.sendto(getWords(data)[0] + " quer iniciar um chat privado com voce. /sim para sim e /nao para nao", clients[index])
                        print time.ctime(time.time()) + str(addr) + ":" + str(data)
                        teste = 1
                    index=index+1
                if teste == 0:
                    for client in clients:
                       if client == addr:
                          s.sendto("\nUsuario nao encontrado.", client)
                teste = 0;
            elif "Aceitou pedido de chat privado" in str(data):
                index2 = 0
                for alia in alias:
                    if alia == getWords(data)[7]:
                        s.sendto("\n" + data, clients[index2])
                        print time.ctime(time.time()) + str(addr) + ":" + str(data)
                    else:
                        s.sendto(getWords(data)[5] + ' e '+ getWords(data)[0] + " sairam do chat publico", clients[index2])
                    index2 = index2 + 1
            elif " em privado para " in str(data):
                index1 = 0;
                for alia in alias:
                    if alia == getWords(data)[4]:
                        s.sendto("\n" + data, clients[index1])
                        if filtro == True and nome in data:
                            print time.ctime(time.time()) + str(addr) + ":" + str(data)
                    index1 = index1+1
            elif "Nao aceitou o pedido de chat privado" in str(data):
                print getWords(data)[9]
                # print (str(data))
                index4 = 0;
                for alia in alias:
                    if alia == getWords(data)[9]:
                        s.sendto("\n" + data, clients[index4])
                        print time.ctime(time.time()) + str(addr) + ":" + str(data)
                    index4 = index4+1
            elif "saiu do privado com" in str(data):
                index3 = 0;
                for alia in alias:
                    if alia == getWords(data)[5]:
                        s.sendto("\n" + data, clients[index3])
                        print time.ctime(time.time()) + str(addr) + ":" + str(data)
                    else:
                        s.sendto(getWords(data)[5] + ' e '+ getWords(data)[0] + " entraram no chat publico", clients[index3])
                    index3 = index3+1
            elif "se desconectou do chat" in str(data):
                index5 = 0
                print "Clientes conectados"
                for alia in alias:
                    if alia == getWords(data)[0]:
                        alias.pop([index5])
                        clients.pop([index5])
                    else:
                        print clients[index5]
                    index5 = index5 + 1
            else:
                if "/sim" not in str(data) and "/nao" not in str(data):
                    for client in clients:
                        if client != addr:
                            s.sendto("\n" + data, client)
                if filtro == False and All == False:
                    print time.ctime(time.time()) + str(addr) + ":" + str(data)
        else:
            s.sendto("\n/Servidor Cheio", addr)
            print addr + " se desconectou devido o servidor estar cheio"
            # clients.pop()
    except:
        pass
socket.shutdown(socket.SHUT_WR)
rT.join()
s.close()

# isso é tudo que eu consegui pensar pra comentar e facilitar quando Daniel for explicar pra vocês
# como vou dizer no grupo do whatsapp (ainda não disse, lógico), não vou poder chegar mais cedo, pq vou fazer
# uns exames de sangue e, quando falei que podia chegar mais cedo, tinha esquecido que eu não vou poder comer até sair dos exames
# como eu acordei às 3 da  manhã e não consegui dormir de novo (aproveitei pra olhar o trabalho aqui), vou ficar com uma fome da PORRA
# por isso vou voltar pra casa pra poder almoçar direito. Boa sorte aí tentando ler e entender, rraleu.
# agora que ja leu aqui, aconselho começar a ler as coisas pelo arquivo do Cliente, pq comecei a comentar a partir dele. Não sei,
# mas possa ser que faça mais lógica começando por ele. Flw
