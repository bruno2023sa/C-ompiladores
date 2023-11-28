from Command import Command
class Parser:
    def __init__(self, input_text):
        self.commands = [Command(line.split()) for line in input_text.split('\n') if line.strip()]
        self.tokens = [line.split() for line in input_text.split('\n') if "//" not in line and line.strip() != ""]

    def command(self):
        return self.tokens.pop(0)

    def hasMoreCommands(self):
        return bool(self.tokens)

    def nextCommand(self):
        if self.commands:
          return self.commands.pop(0)
        else:
          return None