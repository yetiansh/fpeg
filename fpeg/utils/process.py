import numpy as np

from ..base import Pipe
from ..config import read_config


config = read_config()

tile_shape = config.get("preprocess", "tile_shape")
depth = config.get("preprocess", "depth")


class Spliter(Pipe):
  """
  Spliter splits each channels of image to tiles.
  """

  def __init__(self,
               name="Spliter",
               mode="split",
               tile_shape=tile_shape,
               block_shape=()):
    """
    Init and set attributes of a spliter.

    Explicit Attributes
    -------------------
    name: str, optional
      Name of the spliter.
    mode: str, optional
      Mode of spliter, must in ["split", "recover"]
    tile_shape: tuple of int, optional
      Shape of tiles that spliter tries to split.
    block_shape: tuple of int, optional
      Shape used to concatenate tiles together.
    """
    super().__init__()

    self.name = name
    self.mode = mode
    self.tile_shape = tile_shape
    self.block_shape = block_shape

  def recv(self, X, **params):
    self.logs.append("")
    self.logs[-1] += self.formatter.message("Receiving data.")
    self.received_ = X

    if self.mode == "split":
      self.logs[-1] += self.formatter.message("Splitting data into tiles with shape {}.".format(self.tile_shape))

      tiles = []
      shape = X[0].shape
      row_indices = np.arange(self.tile_shape[0], shape[0], self.tile_shape[0], dtype=int)
      col_indices = np.arange(self.tile_shape[1], shape[1], self.tile_shape[1], dtype=int)
      self.logs[-1] += self.formatter.message("Splitting {} shaped image by indices {}.".format(shape, (tuple(row_indices), tuple(col_indices))))

      channel_tiles = []
      n_channels = shape[2]
      for i in range(n_channels):
        channel = X[0][:, :, i]
        splits = []
        for row_splits in np.array_split(channel, row_indices, axis=0):
          splits.extend(np.array_split(row_splits, col_indices, axis=1))
        channel_tiles.append(splits)
      
      n_tiles = len(channel_tiles[0])
      for i in range(n_tiles):
        tile = np.array([splits[i] for splits in channel_tiles])
        tile = np.swapaxes(tile, 0, 1)
        tile = np.swapaxes(tile, 1, 2)
        tiles.append(tile)

      self.sended_ = tiles
    elif self.mode == "recover":
      self.logs[-1] += self.formatter.message("Concatenating tiles with shape {}.".format(self.block_shape))

      n_channels = X[0].shape[2]
      image = []
      for i in range(n_channels):
        channel_tiles = [tile[:, :, i] for tile in X]
        channel = []
        for k in range(self.block_shape[0]):
          row_block = []
          for l in range(self.block_shape[1]):
            row_block.append(channel_tiles[k * self.block_shape[1] + l])
          channel.append(row_block)

        image.append(np.block(channel))

      image = np.array(image)
      image = np.swapaxes(image, 0, 1)
      image = np.swapaxes(image, 1, 2)
      self.sended_ = [image]
    else:
      msg = "Invalid attribute %s for spliter %s. Spliter.mode should be set to \"split\" or \"recover\"." % (self.mode, self)
      self.logs[-1] += self.formatter.error(msg)
      raise AttributeError(msg)

    return self


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
      Mode of the level shifter, must in ["shift", "recover"].
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
      self.logs[-1] += self.formatter.message("Praticing {}-bit DC level shifting.".format(self.depth))
      for tile in X:
        tile = tile - 2 ** (self.depth - 1)
        tiles.append(tile)
    elif self.mode == "recover":
      self.logs[-1] += self.formatter.message("Recover image from {}-bit DC level shifting.".format(self.depth))
      for tile in X:
        tile = tile + 2 ** (self.depth - 1)
        tiles.append(tile)
    else:
      msg = "Invalid attribute %s for level shifter %s. LevelShifter.mode should be set to \"shift\" or \"recover\"." % (self.mode, self)
      self.logs[-1] += self.formatter.error(msg)
      raise AttributeError(msg)

    self.sended_ = tiles

    return self


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
      Mode of the level shifter, must in ["normalize", "recover"].
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
        tile = tile / (2 ** self.depth)
        tiles.append(tile)
    elif self.mode == "recover":
      self.logs[-1] += self.formatter.message("Praticing {}-bit denormalizing.".format(self.depth))
      for tile in X:
        tile = tile * (2 ** self.depth)
        tiles.append(tile)
    else:
      msg = "Invalid attribute %s for noarmlizer %s. Normalizer.mode should be set to \"normalize\" or \"recover\"." % (self.mode, self)
      self.logs[-1] += self.formatter.error(msg)
      raise AttributeError(msg)

    self.sended_ = tiles

    return self
