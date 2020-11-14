from ..base import Pipe
from ..config import read_config


config = read_config()

depth = config.get("preprocess", "depth")


class Normalizer(Pipe):
  """
  Normalizer normalizes or denormalizes tiles.
  """

  def __init__(self,
               name="Normalizer",
               mode="normalize",
               depth=depth):
    """
    Init and set attributes of a normalizer.

    Explicit Attributes
    -------------------
    name: str, optional
      Name of the spliter.
    mode: str, optional
      Mode of the level shifter, must in ["normalize", "denormalize"].
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
    if self.mode == "normalize":
      self.logs[-1] += self.formatter.message("Praticing {}-bit normalizing.".format(self.depth))
      for tile in X:
        tile = tile / (2 ** self.depth - 1)
        tiles.append(tile)
    elif self.mode == "denormalize":
      self.logs[-1] += self.formatter.message("Praticing {}-bit denormalizing.".format(self.depth))
      for tile in X:
        tile = tile * (2 ** self.depth - 1)
        tiles.append(tile)
    else:
      msg = "Invalid attribute %s for noarmlizer %s. Normalizer.mode should be set to \"normalize\" or \"recover\"." % (self.mode, self)
      self.logs[-1] += self.formatter.error(msg)
      raise AttributeError(msg)

    self.sended_ = tiles

    return self
