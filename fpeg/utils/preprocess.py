from math import ceil
import numpy as np
from ..base import Pipe
from ..config import read_config
from .format import Formatter
from .pprint import Pprinter
from .monitor import Monitor


config = read_config()

tile_shape = config.get("preprocess", "tile_shape")
fmt = config.get("log", "fmt")


class Spliter(Pipe):
  """
  Spliter splits channels of image to tiles.
  """

  def __init__(self,
               name="Spliter",
               tile_shape=tile_shape):
    """
    Init and set attributes of a spliter.

    Explicit Attributes
    -------------------
    name: str, optional
      Name of the spliter.
    
    Implicit Attributes
    -------------------
    logs: str
      Log messages of recieving and sending data.
    formatter: Formatter
      Formatter for generating log messages.
    pprinter: fpeg.utils.pprint.Pprinter
      Pretty printer for printing reader.
    monitor: fpeg.utils.monitor.Monitor
    """
    self.name = name
    self.tile_shape = tile_shape

    self.logs = []
    self.formatter = Formatter(fmt=fmt)
    self.pprinter = Pprinter()
    self.monitor = Monitor()

  def recv(self, X, **params):
    self.logs.append("")
    self.recieved_ = X
    shape = X[0].shape
    row_indices = np.arange(self.tile_shape[0], shape[0], self.tile_shape[0], dtype=int)
    col_indices = np.arange(self.tile_shape[1], shape[1], self.tile_shape[1], dtype=int)

    tiles = []
    for x in X:
      for row_splits in np.array_split(x, row_indices, axis=0):
        tiles.extend(np.array_split(row_splits, col_indices, axis=1))

    self.sended_ = tiles

    return self

  def accelerate(self, **params):
    """
    Block this unused method from Pipe.
    """
    pass
