import os
from lexico import LexicalAnalyzer
from sintatico import Parser
from tradutor import translate_to_python

current_directory = os.getcwd()
file_name = "codigo.txt"
file_path = os.path.join(current_directory, file_name)


with open(file_path, "r") as file:
    source_code = file.read()


tokens = LexicalAnalyzer(source_code)


parser = Parser(tokens)
code = parser.parse()


print("=== Código Original ===")
print(source_code)
print()


translated_code = translate_to_python(code)


print("=== Código Traduzido para Python ===")
print(translated_code)
print()


print("=== Execução do Código Traduzido ===")
exec(translated_code)
