from logging import Formatter as _BaseFormatter


class Formatter:
  def __init__(self,
               fmt=None):
    self.fmt = fmt

  def error(self, msg):
    return "Error: " + msg + fmt

  def message(self, msg):
    return "Message: " + msg + fmt

  def warning(self, msg):
    return "Warning: " + msg + fmt
