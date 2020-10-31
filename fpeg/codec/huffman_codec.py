from configparser import ConfigParser, ExtendedInterpolation
from multiprocessing import Pool
from ..base import Codec
from ..log import CodecLogger
from ..utils import dht2lut


config_path = r"config.ini"
config = ConfigParser()
config._interpolation = ExtendedInterpolation()
config.read(config_path)
print(config)

min_task_number = config.getint("accelerate", "codec_min_task_number")
max_pool_size = config.getint("accelerate", "codec_max_pool_size")


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
    Init and set the explicit attributes of a canonical huffman codec.

    Parameters / Explicit Attributes
    --------------------------------
    name: str, optional
      Name of the codec.
    mode: str, optional
      Mode of the codec, must in {"encode", "decode"}.
    dhts: list of lists, optional
      DHTs that store huffman trees for encoding and decoding.
    luts: list of dicts, optional
      LUTs for decoding.
    task_number: int, optional
      Number of tasks for codec to handle.
    accelerate: bool, optional
      Whether the process is accelerated by subprocess pool.

    Implicit Attributes
    -------------------
    min_task_number: int
      Minimun task number to start a pool.
    max_pool_size: int
      Maximun size of pool.
    logs: str
      Log messages of recieving and sending data.
    logger: CodecLogger
      logger for generating log messages.
    """
    self.name = name
    self.mode = mode
    self.dhts = dhts
    self.luts = luts
    self.task_number = task_number
    self.accelerate = accelerate
    self.min_task_number = min_task_number
    self.max_pool_size = max_pool_size
    self.logs = []
    self.logger = CodecLogger(name=name, 
                              mode=mode,
                              task_number=task_number,
                              accelerate=accelerate)

  def encode(self, X, **params):
    self._clear_record()
    try:
      use_lut = bool(params["use_lut"])
    except KeyError:
      use_lut = False

    if use_lut:
      try:
        self.dhts = params["dhts"]
        self.luts = dht2lut(self.dht)
      except KeyError:
        msg = "\"dhts\" should be passed to the encode method."
        self.logger.error(msg)
        raise KeyError(msg)

    if self.accelerate:
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
    self._clear_record()
    try:
      self.dhts = params["dhts"]
      self.luts = dht2lut(self.dht)
    except KeyError as err:
      msg = ""
      self.logger.error(msg)
      raise err
    
    if self.accelerate:
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

  def _decode(self, X,
              lut=None):
    """
    Implement canonical huffman deencoding here.
    """
    return X
