import paramiko
import os
import shutil
import time
import sys

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
def listFiles(directory):
    try:
        files = os.listdir(directory)
        return  "\n".join(files)
    except Exception as e:
        return f"Error: {str(e)}"
    
# funcao para listar usando filtro de nome
def listFilesFilter(directory, filter=None):
    try:
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
        
        return  "\n".join(details_list)
    except Exception as e:
        return f"Error: {str(e)}"

# Função para listar arquivos em todos os nós escravos
def listFilesSlaves(sshClients, slaveIps, directory): 
    results = {}
    for slaveIp in slaveIps:
        output, error = executeSlave(sshClients, slaveIps, f"ls {directory}")
        results[slaveIp] = {"output": output, "error": error}
    return results

# Função para copiar arquivos/diretórios
def copyFileOrDirectory(source, destination): 
    try:
        if os.path.isdir(source):
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
        return "Copiado com sucesso!"
    except Exception as e:
        return f"Error: {str(e)}"

# Função para mover arquivos/diretórios
def moveFileOrDirectory(source, destination):
    try:
        shutil.move(source, destination)
        return "Movido com sucesso!"
    except Exception as e:
        return f"Error: {str(e)}"

# Função para definir permissões em arquivos/diretórios
def setPermissions(path, permissions):
    try:
        os.chmod(path, int(permissions, 8))
        return "Permissions updated"
    except Exception as e:
        return f"Error: {str(e)}"

# Função principal
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
                filter = sys.argv[3] if len(sys.argv) > 3 else None
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

        elif cmd_name == 'setPermissions':
            if len(sys.argv) > 3:
                path = sys.argv[2]
                permissions = sys.argv[3]
                print(setPermissions(path, permissions))
            else:
                print("Caminho e/ou permissões não especificados.")

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

if __name__ == "__main__":
    main()