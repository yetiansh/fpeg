import numpy as np

from ..base import Pipe
from ..config import read_config


class ColorTransformer(Pipe):
  """
  ColorTransformer 
  """

  def __init__(self,
               name="Color transformer",
               mode="transform",
               lossy=False):
    """
    Init and set attributes of a color transformer.

    Explicit Attributes
    -------------------
    name: str, ofptional
      Name of the spliter.
    mode: str, optional
      Mode of spliter, must in ["transform", "reverse transform"]
    lossy: bool, optional
      Whether the transform is lossy or lossless.
    """
    super().__init__()
    
    self.name = name
    self.mode = mode
    self.lossy = lossy

  def recv(self, X, **params):
    self.logs.append("")
    self.logs[-1] += self.formatter.message("Receiving data.")
    self.received_ = X

    if self.mode == "transform":
      x = X[0]
      B = x[:, :, 0]
      G = x[:, :, 1]
      R = x[:, :, 2]
      if self.lossy:
        """
        RGB color space to YCbCr color space.

        R, G, B range from -1/2 to 1/2.
        Y, Cb, Cr range from -1/2 to 1/2.
        """
        self.logs[-1] += self.formatter.message("Praticing ICT.")
        Y = 0.299 * R + 0.587 * G + 0.114 * B
        Cb = 0.5 * (B - Y) / (1 - 0.114)
        Cr = 0.5 * (R - Y) / (1 - 0.114)
        x = np.array([Y, Cb, Cr])
      else:
        """
        RGB color space to YDbDr color space.

        R, G, B range from -2^(depth-1) to 2^(depth-1)-1.
        Y ranges from -2^(depth-1) to 2^(depth-1)-1, Db, Dr range from 1-2^depth to 2^depth-1.
        """
        self.logs[-1] += self.formatter.message("Praticing RCT.")
        Y = np.floor((R + 2 * G + B) / 4)
        Db = B - G
        Dr = R - G
        x = np.array([Y, Db, Dr], dtype=int)

      x = np.swapaxes(x, 0, 1)
      x = np.swapaxes(x, 1, 2)
      self.sended_ = [x]
    elif self.mode == "reverse transform":
      x = X[0]
      if self.lossy:
        """
        YCbCr color space to RGB color space.
        """
        self.logs[-1] += self.formatter.message("Praticing IICT.")
        Y = x[:, :, 0]
        Cb = x[:, :, 1]
        Cr = x[:, :, 2]
        R = Y + 1.402 * Cr
        B = Y + 1.772 * Cb
        G = Y - 0.344136 * Cb - 0.714136 * Cr
        x = np.array([B, G, R])
      else:
        """
        YDbDr color space to RGB color space.
        """
        self.logs[-1] += self.formatter.message("Praticing IRCT.")
        Y = x[:, :, 0]
        Db = x[:, :, 1]
        Dr = x[:, :, 2]
        G = Y - np.floor((Db + Dr) / 4)
        B = Db + G
        R = Dr + G
        x = np.array([B, G, R], dtype=int)

      x = np.swapaxes(x, 0, 1)
      x = np.swapaxes(x, 1, 2)
      self.sended_ = [x]
    else:
      msg = "Invalid attribute %s for color transformer %s. ColorTransformer.mode should be set to \"transform\" or \"reverse transform\"." % (self.mode, self)
      self.logs[-1] += self.formatter.error(msg)
      raise AttributeError(msg)

    return self
