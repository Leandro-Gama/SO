#!/usr/bin/env python3

import paramiko
import os
import shutil
import time
import sys

def connectToSlaves(slaveIps, slaveHostnames, slavePasswords):
    """
    Estabelece conexões SSH com uma lista de slaves e retorna um dicionário de clientes SSH.
    Parâmetros:
    - slaveIps: Lista de endereços IP dos slaves.
    - slaveHostnames: Lista de nomes de usuários dos slaves.
    - slavePasswords: Lista de senhas dos usuários dos slaves.
    Retorno:
    - clients: Dicionário onde as chaves são os IPs dos slaves e os valores são os objetos de conexão SSH.
    """
    clients = {}
    i = 0
    for ip in slaveIps:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=slaveHostnames[i], password=slavePasswords[i])
        clients[ip] = client
        i += 1
    return clients

def executeSlave(sshClients, slaveIp, command):
    """
    Executa um comando em um slave via SSH.
    Parâmetros:
    - sshClients: Dicionário de clientes SSH conectados aos slaves.
    - slaveIp: Endereço IP do slave onde o comando será executado.
    - command: Comando a ser executado no slave.
    Retorno:
    - stdout: Saída do comando.
    - stderr: Erro, se houver.
    """
    for ip in slaveIp:
        try:
            stdin, stdout, stderr = sshClients[ip].exec_command(command)
            return stdout.read().decode(), stderr.read().decode()
        except Exception as e:
            return None, str(e)

def listFiles(directory):
    """
    Lista os arquivos em um diretório local.
    Parâmetros:
    - directory: Caminho do diretório a ser listado.
    Retorno:
    - Uma string com os nomes dos arquivos ou uma mensagem de erro.
    """
    try:
        files = os.listdir(directory)
        return "\n".join(files)
    except Exception as e:
        return f"Error: {str(e)}"

def listFilesFilter(directory, filter=None):
    """
    Lista e filtra diretórios em um caminho especificado, retornando detalhes sobre eles.
    Parâmetros:
    - directory: Caminho do diretório a ser listado.
    - filter: Filtro opcional para limitar os resultados aos diretórios que correspondem ao filtro.
    Retorno:
    - Uma string com detalhes dos diretórios, no estilo do comando ls -l, filtrados ou uma mensagem de erro.
    """
    try:
        directoriesFound = os.listdir(directory)
        details_list = []
        for item in directoriesFound:
            item_path = os.path.join(directory, item)
            if filter in item and os.path.isdir(item_path):
                stats = os.stat(item_path)
                size = stats.st_size
                mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats.st_mtime))
                details = f"{item: <30} Size: {size} bytes, Modified: {mod_time}"
                details_list.append(details)
        return "\n".join(details_list)
    except Exception as e:
        return f"Error: {str(e)}"

def listFilesSlaves(sshClients, slaveIps, directory):
    """
    Lista arquivos em um diretório específico em vários slaves via SSH.
    Parâmetros:
    - sshClients: Dicionário de clientes SSH conectados aos slaves.
    - slaveIps: Lista de endereços IP dos slaves.
    - directory: Caminho do diretório a ser listado nos slaves.
    Retorno:
    - results: Dicionário contendo a saída e os erros (se houver) de cada slave.
    """
    results = {}
    for slaveIp in slaveIps:
        output, error = executeSlave(sshClients, slaveIps, f"ls {directory}")
        results[slaveIp] = {"output": output, "error": error}
    return results

def copyFileOrDirectory(source, destination):
    """
    Copia um arquivo ou diretório para um novo destino.
    Parâmetros:
    - source: Caminho da origem do arquivo ou diretório.
    - destination: Caminho de destino.
    Retorno:
    - Uma mensagem de sucesso ou erro.
    """
    try:
        if os.path.isdir(source):
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
        return "Copiado com sucesso!"
    except Exception as e:
        return f"Error: {str(e)}"

def moveFileOrDirectory(source, destination):
    """
    Move um arquivo ou diretório para um novo destino.
    Parâmetros:
    - source: Caminho da origem do arquivo ou diretório.
    - destination: Caminho de destino.
    Retorno:
    - Uma mensagem de sucesso ou erro.
    """
    try:
        shutil.move(source, destination)
        return "Movido com sucesso!"
    except Exception as e:
        return f"Error: {str(e)}"

def createFile(path, content):
    """
    Cria um arquivo no caminho especificado e escreve o conteúdo fornecido nele.
    Parâmetros:
    - path: Caminho completo do arquivo a ser criado.
    - content: Conteúdo a ser escrito no arquivo.
    Retorno:
    - Uma mensagem de sucesso ou erro.
    """
    try:
        with open(path, 'w') as file:
            file.write(content)
        return f"Arquivo '{path}' criado com sucesso!"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    if len(sys.argv) > 1:
        slaveIps = ['192.168.100.196', '192.168.100.197']
        slaveHostnames = ["cluster-1","cluster-2"]
        slavePasswords = ["cluster-1","cluster-2"]
        sshClients = connectToSlaves(slaveIps,slaveHostnames,slavePasswords)

        cmd_name = sys.argv[1]

        if cmd_name == 'listFiles':
            if len(sys.argv) > 2:
                directory = sys.argv[2]
                print(listFiles(directory))
            else:
                print("Diretório não especificado.")

        elif cmd_name == 'listFilesFilter':
            if len(sys.argv) > 2:
                directory = sys.argv[2]
                filter = sys.argv[3] if len(sys.argv) > 3 else ""
                print(listFilesFilter(directory, filter))
            else:
                print("Diretório não especificado.")

        elif cmd_name == 'copyFileOrDirectory':            
            if len(sys.argv) > 3:
                source = sys.argv[2]
                destination = sys.argv[3]
                print(copyFileOrDirectory(source, destination))
            else:
                print("Caminhos não especificados.")
        
        elif cmd_name == 'moveFileOrDirectory':
            if len(sys.argv) > 3:
                source = sys.argv[2]
                destination = sys.argv[3]
                print(moveFileOrDirectory(source, destination))
            else:
                print("Caminhos não especificados.")

        elif cmd_name == 'listFilesSlaves':
            if len(sys.argv) > 2:
                directory = sys.argv[2]
                results = listFilesSlaves(sshClients, slaveIps, directory)
                for ip, result in results.items():
                    print(f"Nó {ip} - Output:\n{result['output']}")
                    if result['error']:
                        print(f"Erro no nó {ip}:\n{result['error']}")
            else:
                print("Diretório não especificado.")

        elif cmd_name == 'createFile':
            if len(sys.argv) > 3:
                path = sys.argv[2]
                content = sys.argv[3] if len(sys.argv) > 3 else ""
                print(createFile(path, content))
            else:
                print("Caminho do arquivo não especificados.")

        else:
            print(f"Comando '{cmd_name}' não reconhecido.")
    
    else:
        print("Comandos disponíveis:")
        print("listFiles <diretório>")
        print("listFilesFilter <diretório> <filtro>")
        print("copyFileOrDirectory <origem> <destino>")
        print("moveFileOrDirectory <origem> <destino>")
        print("setPermissions <caminho> <permissões>")
        print("listFilesSlaves <diretório>")        
        print("createFile <caminho> <conteúdo>")  

if __name__ == "__main__":
    main()