class Parser:
  def __init__(self, input_file):
      # Abre o arquivo de entrada e extrai os comandos
      self.file = open(input_file, "r")
      self.commands = [line.strip() for line in self.file.readlines() if line.strip() and not line.startswith("//")]

  def has_more_commands(self):
      # Verifica se ainda há comandos para processar
      return len(self.commands) > 0

  def advance(self):
      # Retorna e remove o próximo comando da lista de comandos
      return self.commands.pop(0)

  def command_type(self, command):
      # Determina o tipo do comando: C_ARITHMETIC, C_PUSH ou C_POP
      if command in {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}:
          return "C_ARITHMETIC"
      elif command.startswith("push"):
          return "C_PUSH"
      elif command.startswith("pop"):
          return "C_POP"

  def arg1(self, command):
      # Retorna o primeiro argumento do comando
      if self.command_type(command) == "C_ARITHMETIC":
          return command
      else:
          return command.split()[1]

  def arg2(self, command):
      # Retorna o segundo argumento do comando
      return int(command.split()[2])


class CodeWriter:
  def __init__(self, output_file):
      # Abre o arquivo de saída para escrever o código Assembly
      self.file = open(output_file, "w")
      # Contador para rótulos únicos em instruções de comparação
      self.label_counter = 0

  def write_arithmetic(self, command):
      # Escreve o código Assembly para comandos aritméticos e lógicos
      if command in {"add", "sub", "and", "or"}:
          self.write_binary_arithmetic(command)
      elif command in {"neg", "not"}:
          self.write_unary_arithmetic(command)
      elif command in {"eq", "gt", "lt"}:
          self.write_comparison(command)

  def write_push_pop(self, command, segment, index):
      # Escreve o código Assembly para comandos push e pop
      if command.startswith("push"):
          self.write_push(segment, index)
      elif command.startswith("pop"):
          self.write_pop(segment, index)

  def write_binary_arithmetic(self, command):
      # Escreve o código Assembly para operações binárias
      self.decrement_sp()
      self.write_pop_to_d()
      self.decrement_sp()
      self.write_arithmetic_command(command)
      self.increment_sp()

  def write_unary_arithmetic(self, command):
      # Escreve o código Assembly para operações unárias
      self.decrement_sp()
      self.write_arithmetic_command(command)
      self.increment_sp()

  def write_comparison(self, command):
      # Escreve o código Assembly para operações de comparação
      self.label_counter += 1
      label_true = f"TRUE_{self.label_counter}"
      label_end = f"END_{self.label_counter}"

      self.decrement_sp()
      self.write_pop_to_d()
      self.decrement_sp()
      self.write_arithmetic_command(command)
      self.write_goto(label_true)
      self.write_label(label_end)
      self.increment_sp()

  def write_push(self, segment, index):
      # Escreve o código Assembly para o comando push
      if segment == "constant":
          self.write_push_constant(index)
      else:
          self.write_push_segment(segment, index)

  def write_pop(self, segment, index):
      # Escreve o código Assembly para o comando pop
      if segment != "temp":
          self.decrement_sp()
          self.write_pop_to_d()
          self.write_address(segment, index)
          self.write_pop_d_to_m()
      else:
          self.decrement_sp()
          self.write_pop_to_d()
          self.write_address(segment, index)
          self.write_pop_d_to_m()

  def write_push_constant(self, index):
      # Escreve o código Assembly para push constant
      self.write_a_instruction(index)
      self.write_c_instruction("D", "A")
      self.write_push_d_to_stack()

  def write_push_segment(self, segment, index):
      # Escreve o código Assembly para push em outros segmentos
      self.write_address(segment, index)
      self.write_c_instruction("D", "M")
      self.write_push_d_to_stack()

  def write_arithmetic_command(self, command):
      # Escreve o código Assembly para comandos aritméticos e lógicos
      if command == "add":
          self.write_c_instruction("M", "D+M")
      elif command == "sub":
          self.write_c_instruction("M", "M-D")
      elif command == "neg":
          self.write_c_instruction("M", "-M")
      elif command == "eq":
          self.write_c_instruction("M", "D-M")
          self.write_c_instruction("D", "M")
          self.write_c_instruction("M", "-1")
          self.write_goto("TRUE")
      elif command == "gt":
          self.write_c_instruction("M", "D-M")
          self.write_c_instruction("D", "M")
          self.write_c_instruction("M", "-1")
          self.write_goto("TRUE")
      elif command == "lt":
          self.write_c_instruction("M", "D-M")
          self.write_c_instruction("D", "M")
          self.write_c_instruction("M", "-1")
          self.write_goto("TRUE")
      elif command == "and":
          self.write_c_instruction("M", "D&M")
      elif command == "or":
          self.write_c_instruction("M", "D|M")
      elif command == "not":
          self.write_c_instruction("M", "!M")

  def write_a_instruction(self, value):
      # Escreve uma instrução Assembly do tipo A
      self.file.write(f"@{value}\n")

  def write_c_instruction(self, dest, comp, jump=None):
      # Escreve uma instrução Assembly do tipo C
      if jump:
          self.file.write(f"{dest}={comp};{jump}\n")
      else:
          self.file.write(f"{dest}={comp}\n")

  def write_label(self, label):
      # Escreve uma instrução de label Assembly
      self.file.write(f"({label})\n")

  def write_goto(self, label):
      # Escreve uma instrução de goto Assembly
      self.file.write(f"@{label}\n")
      self.file.write("0;JMP\n")

  def write_push_d_to_stack(self):
      # Escreve o código Assembly para push D na pilha
      self.write_a_instruction("SP")
      self.write_c_instruction("A", "M")
      self.write_c_instruction("M", "D")
      self.increment_sp()

  def decrement_sp(self):
      # Decrementa o ponteiro da pilha (SP)
      self.write_a_instruction("SP")
      self.write_c_instruction("M", "M-1")

  def increment_sp(self):
      # Incrementa o ponteiro da pilha (SP)
      self.write_a_instruction("SP")
      self.write_c_instruction("M", "M+1")

  def write_pop_to_d(self):
      # Escreve o código Assembly para pop na variável D
      self.write_a_instruction("SP")
      self.write_c_instruction("A", "M")
      self.write_c_instruction("D", "M")

  def write_address(self, segment, index):
      # Escreve o código Assembly para acessar um endereço de memória
      if segment == "local":
          self.write_a_instruction("LCL")
      elif segment == "argument":
          self.write_a_instruction("ARG")
      elif segment == "this":
          self.write_a_instruction("THIS")
      elif segment == "that":
          self.write_a_instruction("THAT")
      elif segment == "temp":
          self.write_a_instruction("5")
      elif segment == "pointer":
          self.write_a_instruction("THIS" if index == 0 else "THAT")
      elif segment == "static":
          # Assume que os símbolos estáticos estão em RAM[16] até RAM[255]
          self.write_a_instruction(f"16")
      self.write_c_instruction("A", "M" if segment != "static" else "A")
      self.write_c_instruction("D", "A" if segment == "static" else "D")
      self.write_a_instruction(str(index))
      self.write_c_instruction("A", "D+A")

  def write_pop_d_to_m(self):
      # Escreve o código Assembly para armazenar D no endereço de memória apontado por M
      self.write_a_instruction("SP")
      self.write_c_instruction("A", "M")
      self.write_c_instruction("A", "M-1")
      self.write_c_instruction("A", "M")
      self.write_c_instruction("M", "D")

  def close(self):
      # Fecha o arquivo de saída
      self.file.close()


class VMTranslator:
  def __init__(self, input_file, output_file):
      self.parser = Parser(input_file)
      self.code_writer = CodeWriter(output_file)

  def translate(self):
      while self.parser.has_more_commands():
          command = self.parser.advance()
          command_type = self.parser.command_type(command)
          arg1 = self.parser.arg1(command)
          arg2 = self.parser.arg2(command)

          if command_type == "C_ARITHMETIC":
              self.code_writer.write_arithmetic(arg1)
          elif command_type in {"C_PUSH", "C_POP"}:
              self.code_writer.write_push_pop(command, arg1, arg2)

      self.code_writer.close()


if __name__ == "__main__":
  input_file = "BasicTest.vm"
  output_file = "BasicTest.asm"

  translator = VMTranslator(input_file, output_file)
  translator.translate()
