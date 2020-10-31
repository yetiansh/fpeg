from configparser import ConfigParser, ExtendedInterpolation
from multiprocessing import Pool
from ..base import Codec


config_path = r"config.ini"
config = ConfigParser()
config._interpolation = ExtendedInterpolation()
config.read(config_path)


class ShannonCodec(Codec):
  """
  
  """
  def __init__(self):
    pass