from math import ceil
import numpy as np

from ..base import Pipe
from ..config import read_config
from .format import Formatter
from .monitor import Monitor


config = read_config()

tile_shape = config.get("preprocess", "tile_shape")


class Spliter(Pipe):
  """
  Spliter splits each channels of image to tiles.
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
    tile_shape: tuple of int, optional
      Shape of tiles that spliter tries to split.
    """
    super().__init__()

    self.name = name
    self.tile_shape = tile_shape

  def recv(self, X, **params):
    self.logs.append("")
    self.logs[-1] += self.formatter.message("Receiving data.")
    self.received_ = X
    self.logs[-1] += self.formatter.message("Splitting data into tiles with shape {}.".format(self.tile_shape))
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
