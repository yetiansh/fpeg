from multiprocessing import Pool

from ..base import Codec
from ..config import read_config
from ..utils.lut import dht2lut


config = read_config()

min_task_number = config.get("accelerate", "codec_min_task_number")
max_pool_size = config.get("accelerate", "codec_max_pool_size")


class HuffmanCodec(Codec):
  """
  Canonical Huffman Codec.

  HuffmanCodec uses Define Huffman Table (DHT) to store the huffman tree and pass to another HuffmanCodec for decoding, and use Look Up Table (LUT) to decode data.
  """

  def __init__(self,
               name="Huffman Codec",
               mode="encode",
               dhts=[],
               accelerated=False
               ):
    """
    Init and set attributes of a canonical huffman codec.

    Explicit Attributes
    -------------------
    name: str, optional
      Name of the codec.
    mode: str, optional
      Mode of the codec, must in ["encode", "decode"].
    dhts: list of lists, optional
      DHTs that store huffman trees for encoding and decoding.
    accelerated: bool, optional
      Whether the process would be accelerated by subprocess pool.

    Implicit Attributes
    -------------------
    min_task_number: int
      Minimun task number to start a pool.
    max_pool_size: int
      Maximun size of pool.
    """
    super().__init__()

    self.name = name
    self.mode = mode
    self.dhts = dhts
    self.accelerated = accelerated

    self.min_task_number = min_task_number
    self.max_pool_size = max_pool_size
    

  def encode(self, X, **params):
    self.logs[-1] += self.formatter.message("Trying to encode received data.")
    try:
      use_lut = bool(params["use_lut"])
      self.logs[-1] += self.formatter.message("\"use_lut\" is specified as " + str(use_lut) + ".")
    except KeyError:
      self.logs[-1] += self.formatter.warning("\"use_lut\" is not specified, now set to False.")
      use_lut = False

    if use_lut:
      try:
        self.logs[-1] += self.formatter.message("Converting DHTs to LUTs.")
        self.dhts = params["dhts"]
        self.luts = dht2lut(self.dhts)
      except KeyError:
        msg = "\"dhts\" should be passed to the encode method since \"use_lut\" is specified as True."
        self.logs[-1] += self.formatter.error(msg)
        raise KeyError(msg)

    if self.accelerated:
      self.logs[-1] += self.formatter.message("Using multiprocess pool to accelerate encoding.")
      if use_lut:
        inputs = [[x, lut] for x, lut in zip(X, self.luts)]
      else:
        inputs = [[x, []] for x in X]
      with Pool(min(self.task_number, self.max_pool_size)) as p:
        X = p.starmap(_encode, inputs)
    else:
      if use_lut:
        X = [_encode(x, lut) for x, lut in zip(X, self.luts)]
      else:
        X = [_encode(x, []) for x in X]

    return X

  def decode(self, X, **params):
    self.logs[-1] += self.formatter.message("Trying to decode received data.")
    try:
      self.dhts = params["dhts"]
      self.luts = dht2lut(self.dhts)
    except KeyError:
      msg = "\"dhts\" should be passed to the decode method."
      self.logs[-1] += self.formatter.error(msg)
      raise KeyError(msg)
    
    if self.accelerated:
      self.logs[-1] += self.formatter.message("Using multiprocess pool to accelerate decoding.")
      inputs = [[x, lut] for x, lut in zip(X, self.luts)]
      with Pool(min(self.task_number, self.max_pool_size)) as p:
        X = p.map(_decode, inputs)
    else:
      X = [_decode(x, lut) for x, lut in zip(X, self.luts)]

    return X


def _encode(X, lut):
  """
  Implement canonical huffman encoding here.

  If lut is None, construct dhts and set self.dhts and self.luts.
  """
  return X


def _decode(X, lut):
  """
  Implement canonical huffman deencoding here.
  """
  return X
