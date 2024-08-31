#!/usr/bin/env python3

import sys

commands = {}

def command(name):
    def decorator(func):
        commands[name] = func
        return func
    return decorator

@command('executeA')
def execute_a():
    print("Executando ação A")

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
