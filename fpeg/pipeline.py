from .base import Pipe
from .monitor import Monitor


class Pipeline:
  """
  Pipeline.
  """
  def __init__(self,
               pipes=None,
               monitor=None,
               testers=None,
               logger=None):
    self._set_pipes(pipes)
    self._check_pipes()
    self._set_monitor(monitor)
    self._set_testers(testers)
    self._set_logger(logger)

  def recv_send(X, **params):
    pass

  def _set_pipes(pipes):
    if not pipes:
      raise ValueError("Can not construct an empty pipeline.")
    for name, pipe in pipes:
      pass

  def _check_pipes():
    """
    Check whether the connection of pipes is legal.
    """
    pass

  def _set_monitor():
    """
    
    """
    pass

  def _iter():
    """
    Send data to a pipe and collect it.
    """
    pass
