from typing import List

from co.reader import Message

class Logger:

  def __init__ (self):
    self.queue: List[Message] = []

  def add_message (self, message: Message):
    self.queue.append(message)

  def print (self):
    for message in self.queue:
      print(f"{message.kind}({message.line}): {message.text}")
