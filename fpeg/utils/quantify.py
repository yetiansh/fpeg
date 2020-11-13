import numpy as np

from ..base import Pipe
from ..config import read_config


config = read_config()


class Quantizer(Pipe):
  """
  Quantizer
  """
  def __init__(self,
               name="Quantizer",
               mode="quantify",
               reversible=True):
    """
    
    """
    super().__init__()
    
    self.name = name
    self.mode = mode
    self.reversible = reversible
