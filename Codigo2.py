#!/usr/bin/env python3

import paramiko
import os
import shutil
import time
import sys

commands = {}

def command(name):
    def decorator(func):
        commands[name] = func
        return func
    return decorator

# Função para conectar aos nós escravos via SSH
def connectToSlaves(slaveIps,slaveHostnames,slavePasswords):
    clients = {}
    i = 0
    for ip in slaveIps:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username = slaveHostnames[i], password = slavePasswords[i])
        clients[ip] = client
        i += 1
    return clients

# Função para executar um comando em um nó escravo específico
def executeSlave(sshClients, slaveIp, command):
    try:
        stdin, stdout, stderr = sshClients[slaveIp].exec_command(command)
        return stdout.read().decode(), stderr.read().decode()
    except Exception as e:
        return None, str(e)

# Função para listar arquivos no nó mestre
@command('listFiles')
def listFiles():
    try:
        initConnections()
        directory = input("Digite o diretório no nó mestre: ")        
        files = os.listdir(directory)
        print("\n".join(files))
    except Exception as e:
        print(f"Error: {str(e)}")
    
# funcao para listar usando filtro de nome
@command('listFilesFilter')
def listFilesFilter():
    try:
        initConnections()
        directory = input("Digite o caminho do arquivo/diretório: ")
        filter = input("Digite o nome para filtrar: ")

        directoriesFound = os.listdir(directory)
        
        # Inicializa uma lista para armazenar os detalhes dos diretórios filtrados
        details_list = []
        
        # Adiciona diretórios à lista de detalhes com base no filtro especificado
        for item in directoriesFound:
            item_path = os.path.join(directory, item)
            if filter in item and os.path.isdir(item_path):
                # Obtém informações do diretório
                stats = os.stat(item_path)
                size = stats.st_size
                mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats.st_mtime))
                
                # Cria uma string de detalhes no estilo ls -l
                details = f"{item: <30} Size: {size} bytes, Modified: {mod_time}"
                details_list.append(details)
        
        print("\n".join(details_list))
    except Exception as e:
        print(f"Error: {str(e)}")

# Função para listar arquivos em todos os nós escravos
def listFilesSlaves(sshClients, slaveIps, directory): 
    directory = input("Digite o diretório nos nós escravos: ")
    results = {}
    for slaveIp in slaveIps:
        output, error = executeSlave(sshClients, slaveIps, f"ls {directory}")
        results[slaveIp] = {"output": output, "error": error}
    return results

# Função para copiar arquivos/diretórios
@command('copyFileOrDirectory')
def copyFileOrDirectory(): 
    try:
        initConnections()
        source = input("Digite o caminho do arquivo/diretório de origem: ")
        destination = input("Digite o caminho do destino: ")

        if os.path.isdir(source):
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
        print("\n".join("Copiado com sucesso!"))
    except Exception as e:
        print(f"Error: {str(e)}")

# Função para mover arquivos/diretórios
@command('moveFileOrDirectory')
def moveFileOrDirectory():
    try:
        initConnections()
        source = input("Digite o caminho do arquivo/diretório de origem: ")
        destination = input("Digite o caminho do destino: ")
        shutil.move(source, destination)
        print("\n".join("Movido com sucesso!"))
    except Exception as e:
        print(f"Error: {str(e)}")

# Função para definir permissões em arquivos/diretórios
@command('setPermissions')
def setPermissions(path, permissions):
    try:
        initConnections()
        path = input("Digite o caminho do arquivo/diretório: ")
        permissions = input("Digite as permissões (e.g., 755): ")
        os.chmod(path, int(permissions, 8))
        print("Permissions updated")
    except Exception as e:
        print(f"Error: {str(e)}")

# Função para iniciar as conexões
def initConnections():
    slaveIps = ['192.168.100.196', '192.168.100.197']
    slaveHostnames = ["cluster-1","cluster-2"]
    slavePasswords = ["cluster-1","cluster-2"]
    sshClients = connectToSlaves(slaveIps,slaveHostnames,slavePasswords)   

def main():
    if len(sys.argv) > 1:
        cmd_name = sys.argv[1]
        if cmd_name in commands:
            commands[cmd_name]()
        else:
            print(f"Comando '{cmd_name}' não reconhecido.")
    else:
        print("Comandos disponíveis:")
        for cmd in commands:
            print(f" - {cmd}")

if __name__ == "__main__":
    main()
