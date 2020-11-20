from time import strftime, localtime


class Formatter:
  def __init__(self,
               fmt="%Y-%m-%d %H:%M:%S"):
    self.fmt = fmt

  def message(self, msg):
    if not msg[-1] == '\n':
      msg += '\n'

    return strftime(self.fmt, localtime()) + " Message: " + msg

  def warning(self, msg):
    if not msg[-1] == '\n':
      msg += '\n'

    return strftime(self.fmt, localtime()) + " Warning: " + msg

  def error(self, msg):
    if not msg[-1] == '\n':
      msg += '\n'

    return strftime(self.fmt, localtime()) + " Error: " + msg
