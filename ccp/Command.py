class Command:
  class Type:
      ADD = "ADD"
      SUB = "SUB"
      NEG = "NEG"
      EQ = "EQ"
      GT = "GT"
      LT = "LT"
      AND = "AND"
      OR = "OR"
      NOT = "NOT"
      PUSH = "PUSH"
      POP = "POP"

  def __init__(self, command):
      self.type = command[0].upper()
      self.args = command[1:]