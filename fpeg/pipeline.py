from .base import *
# from .codec import *
# from .transformer import *
from .utils.monitor import Monitor
from .utils.format import Formatter
# from .utils.pprint import Pprinter


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
               # pprinter=Pprinter(**pprint_option),
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
      self._set_pipes()

    self.received_ = X
    self.monitor.prepare()
    for name, pipe in zip(self.names, self.pipes):
      X = pipe.recv_send(X, **self.params[name])

    self.sended_ = X

    # Pipes' record are cleared, need to be setted.
    self.setted = False

  def _set_up(self):
    if not len(self.steps):
      msg = "Can not construct an empty pipeline."
      raise ValueError(msg)

    for name, pipe in self.steps:
      if name not in self.params:
        # raise error here
        pass

      self.names.append(name)
      self.pipes.append(pipe)
    
    self._set_pipes()
    self._check()

  def _set_pipes(self):
    for i in range(len(self.names)):
      self.pipes[i].set_params(**self.params[self.names[i]],
                                  **{
                                    "name": self.names[i],
                                    "monitor": self.monitor,
                                    "formatter": self.formatter
                                  })

    self.setted = True

  def _check(self):
    """
    Check whether the connection of pipes is legal.
    """
    pass

  def set_params(self, **params):
    self.params = params
    self._set_pipes()
