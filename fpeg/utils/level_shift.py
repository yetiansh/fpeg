__all__ = [
  "LevelShifter"
]

from ..base import Pipe
from ..config import read_config


config = read_config()

depth = config.get("preprocess", "depth")


class LevelShifter(Pipe):
  """
  LevelShifter pratices DC level shifting or recovering on tiles.
  """

  def __init__(self,
               name="Level shifter",
               mode="shift",
               depth=depth):
    """
    Init and set attributes of a level shifter.

    Explicit Attributes
    -------------------
    name: str, optional
      Name of the spliter.
    mode: str, optional
      Mode of the level shifter, must in ["shift", "reverse shift"].
    depth: int, optional
      Depth of image.
    """
    super().__init__()

    self.name = name
    self.mode = mode
    self.depth = depth

  def recv(self, X, **params):
    self.logs.append("")
    self.logs[-1] += self.formatter.message("Receiving data.")
    self.received_ = X

    tiles = []
    if self.mode == "shift":
      try:
        self.depth = params["depth"]
        self.logs[-1] += self.formatter.message("\"depth\" is specified as {}.".format(self.depth))
      except KeyError:
        self.logs[-1] += self.formatter.warning("\"depth\" is not specified, now set to {}.".format(self.depth))

      self.logs[-1] += self.formatter.message("Praticing {}-bit DC level shifting.".format(self.depth))

      for tile in X:
        tile = tile - 2 ** (self.depth - 1)
        tiles.append(tile)
    elif self.mode == "reverse shift":
      try:
        self.depth = params["depth"]
        self.logs[-1] += self.formatter.message("\"depth\" is specified as {}.".format(self.depth))
      except KeyError:
        self.logs[-1] += self.formatter.warning("\"depth\" is not specified, now set to {}.".format(self.depth))

      self.logs[-1] += self.formatter.message("Recovering image from {}-bit DC level shifting.".format(self.depth))
      for tile in X:
        tile = tile + 2 ** (self.depth - 1)
        tiles.append(tile)
    else:
      msg = "Invalid attribute %s for level shifter %s. LevelShifter.mode should be set to \"shift\" or \"reverse shift\"." % (self.mode, self)
      self.logs[-1] += self.formatter.error(msg)
      raise AttributeError(msg)

    self.sended_ = tiles

    return self
