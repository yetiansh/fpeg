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
               luts=[],
               task_number=0,
               accelerate=False
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
    luts: list of dicts, optional
      LUTs for decoding.
    task_number: int, optional
      Number of tasks for codec to handle.
    accelerate: bool, optional
      Whether the process would be accelerated by subprocess pool.

    Implicit Attributes
    -------------------
    min_task_number: int
      Minimun task number to start a pool.
    max_pool_size: int
      Maximun size of pool.
    pool: multiprocessing.Pool
      Multiprocess pool for accelerate processing.
    """
    super().__init__()

    self.name = name
    self.mode = mode
    self.dhts = dhts
    self.luts = luts
    self.task_number = task_number
    self.accelerate = accelerate

    self.min_task_number = min_task_number
    self.max_pool_size = max_pool_size
    self.pool = None
    

  def encode(self, X, **params):
    try:
      use_lut = bool(params["use_lut"])
      self.logs[-1] += self.formatter.message("\"use_lut\" is specified as true.")
    except KeyError:
      self.logs[-1] += self.formatter.warning("\"use_lut\" is not specified, now set to false.")
      use_lut = False

    if use_lut:
      try:
        self.logs[-1] += self.formatter.message("Converting DHTs to LUTs.")
        self.dhts = params["dhts"]
        self.luts = dht2lut(self.dht)
      except KeyError:
        msg = "\"dhts\" should be passed to the encode method since \"use_lut\" is specified as true."
        self.logs[-1] += self.formatter.error(msg)
        raise KeyError(msg)

    if self.accelerate:
      self.logs[-1] += self.formatter.message("Using multiprocess pool to accelerate encoding.")
      if use_lut:
        inputs = [[x, lut] for x, lut in zip(X, self.luts)]
      else:
        inputs = X
      X = self.pool.map(self._encode, inputs)
    else:
      if use_lut:
        X = [self._encode(x, lut) for x, lut in zip(X, self.luts)]
      else:
        X = [self._encode(x) for x in X]

    return X

  def decode(self, X, **params):
    try:
      self.dhts = params["dhts"]
      self.luts = dht2lut(self.dht)
    except KeyError as err:
      msg = "\"dhts\" should be passed to the decode method."
      self.logs[-1] += self.formatter.error(msg)
      raise KeyError(msg)
    
    if self.accelerate:
      self.logs[-1] += self.formatter.message("Using multiprocess pool to accelerate decoding.")
      inputs = [[x, lut] for x, lut in zip(X, self.luts)]
      X = self.pool.map(self._decode, inputs)
    else:
      X = [self._decode(x, lut) for x, lut in zip(X, self.luts)]

    return X

  def _encode(self, X,
              lut=None):
    """
    Implement canonical huffman encoding here.

    If lut is None, construct dhts and set self.dhts and self.luts.
    """
    return X

  def _decode(self, X, lut):
    """
    Implement canonical huffman deencoding here.
    """
    return X
