from .base import *
# from .codec import *
# from .transformer import *
from .utils.monitor import Monitor
from .utils.format import Formatter


config = read_config()

time_format = config.get("log", "time_format")
pprint_option = config.get_section("print")


class Pipeline:
  """
  Pipeline.
  """

  def __init__(self, steps, *,
               name="Pipeline",
               params={},
               monitor=Monitor(),
               formatter=Formatter(fmt=time_format),
               testers=[]):
    """
    Init pipeline.
    """
    self.steps = steps

    self.name = name
    self.params = params
    self.monitor = monitor
    self.formatter = formatter

    self.names = []
    self.pipes = []
    self.setted = False
    self._set_up()

  def recv(self, X):
    if not self.setted:
      self._set_pipe_params()

    self.received_ = X
    self.monitor.prepare()
    for name, pipe in zip(self.names, self.pipes):
      X = pipe.recv_send(X, **self.params[name])

    self.sended_ = X

    # Pipes' explicit attributes are cleared, need to be setted.
    self.setted = False

  def _set_up(self):
    if not len(self.steps):
      msg = "Can not construct an empty pipeline."
      raise ValueError(msg)

    for name, pipe in self.steps:
      if name not in self.params:
        # raise error here
        raise ValueError("Invalid pipe name \'{}\'. "
                         "Should be in {}".format(name,
                                                  list(self.params.keys())
                                                  )
                         )

      self.names.append(name)
      self.pipes.append(pipe)
    
    self._set_pipe_params()
    self._check()

  def _set_pipe_params(self):
    for i in range(len(self.names)):
      self.pipes[i].set_params(**self.params[self.names[i]],
                               **{
                               "name": self.names[i],
                               "monitor": self.monitor,
                               "formatter": self.formatter
                               })

    # Now pipes' attributes are setted.
    self.setted = True

  def _check(self):
    """
    Check whether the connection of pipes is legal.

    Raise ValueError if any rules are violated.

    Not implemented.
    """
    pass

  def set_pipe_params(self, **params):
    """
    Set pipe parameters before receiving.
    """
    for name in params:
      if name not in self.params:
        raise ValueError("Invalid pipe name \'{}\'. "
                         "Should be in {}".format(name, self.names))

      for sub_name in params[name]:
        index = self.names.index(name)
        valid_names = self.pipes[index]._get_param_names()
        self.params[name][sub_name] = params[name][sub_name]

    self._set_pipe_params()

  def get_log(self):
    """
    Return log of last receiving.
    """
    logs = ""
    for name, log in zip(self.names, self.monitor.logs[-1]):
      logs += name + ": \n" + log

    return logs
