import cv2
from ..base import BasePipe

class Reader(BasePipe):
  """
  Reader
  """

  def __init__(self):
    pass

  def recieve(self, X):
    if iterable(X):
      self.queue = tuple(x for x in X)
    else:
      self.queue = (X,)


class Writer(BasePipe):
  """
  Writer 
  """  

  def __init__(self):
    pass