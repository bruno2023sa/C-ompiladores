import os
from Parser import Parser
from CodeWrite import CodeWriter
from Command import Command

def from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def main():
    import sys

    if len(sys.argv) != 2:
        print("caminho do arquivo")
        sys.exit(1)

    filename = sys.argv[1]


    if os.path.isdir(filename):
        output_filename = os.path.join(filename, f"{os.path.basename(filename)}.asm")

        for file_name in os.listdir(filename):
            if file_name.endswith(".vm"):
                input_file_path = os.path.join(filename, file_name)
                print(f"Compilando {input_file_path}")
                input_text = from_file(input_file_path)
                parser = Parser(input_text)
                output_filename = f"{os.path.splitext(input_file_path)[0]}.asm"
                code_writer = CodeWriter(output_filename)

                while parser.hasMoreCommands():
                    command = parser.nextCommand()
                    if command is not None:
                        if command.type == Command.Type.ADD:
                            code_writer.writeArithmeticAdd()
                        elif command.type == Command.Type.SUB:
                            code_writer.writeArithmeticSub()
                        elif command.type == Command.Type.PUSH:
                            code_writer.writePush(command.args[0], int(command.args[1]))
                        elif command.type == Command.Type.POP:
                            code_writer.writePop(command.args[0], int(command.args[1]))
                    else:
                        break
                code_writer.save()

    elif os.path.isfile(filename):
        if not filename.endswith(".vm"):
            print("Caminho.vm")
            sys.exit(1)
        else:
            input_text = from_file(filename)
            parser = Parser(input_text)
            output_filename = f"{os.path.splitext(filename)[0]}.asm"
            code_writer = CodeWriter(output_filename)

            while parser.hasMoreCommands():
                command = parser.nextCommand()
                if command is not None:
                    if command.type == Command.Type.ADD:
                        code_writer.writeArithmeticAdd()
                    elif command.type == Command.Type.SUB:
                        code_writer.writeArithmeticSub()
                    elif command.type == Command.Type.PUSH:
                        code_writer.writePush(command.args[0], int(command.args[1]))
                    elif command.type == Command.Type.POP:
                        code_writer.writePop(command.args[0], int(command.args[1]))
                else:
                    break
            code_writer.save()

if __name__ == "__main__":
    main()
