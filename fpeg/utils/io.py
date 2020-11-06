import cv2
from ..base import Pipe
from ..config import read_config


config = read_config()


class Reader(Pipe):
  """
  Reader of images.
  """

  def __init__(self,
               name="Image Reader",
               flag="color"):
    """
    Init and set attributes of a image reader.

    Explicit Attributes
    -------------------
    name: str, optional
      Name of the reader.
    flag: str, optional
      Flag used in cv2.imread, must in ["color", "grayscale", "unchanged"]
    """
    super().__init__()

    self.name = name
    self.flag = flag

  def recv(self, path, **params):
    self.logs.append("")
    self.logs[-1] += self.formatter.message("Receiving data.")
    self.received_ = path
    self.logs[-1] += self.formatter.message("Reading '{}' with flag '{}'.".format(path, self.flag))
    if self.flag == "color":
      X = cv2.imread(path, cv2.IMREAD_COLOR)
    elif self.flag == "grayscale":
      X = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    elif self.flag == "unchanged":
      X = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    else:
      msg = "Invalid flag of {}."
      self.logs[-1] += self.formatter.error(msg)
      raise ValueError(msg)
      
    if X is None:
      msg = "File path is invalid."
      self.logs[-1] += self.formatter.error(msg)
      raise ValueError(msg)

    self.sended_ = []
    if len(X.shape) == 3:
      for i in range(X.shape[2]):
        self.sended_.append(X[:, :, i])
    else:
      self.sended_.append(X[:, :])

    return self


class Writer(Pipe):
  """
  Writer of images.
  """  

  def __init__(self,
               name="Image Writer"):
    """
    Init and set attributes of a image reader.

    Explicit Attributes
    -------------------
    name: str, optional
      Name of the reader.
    """
    super().__init__()

    self.name = name

  def recv(self, X, **params):
    self.logs.append("")
    self.logs[-1] += self.formatter.message("Receiving data.")
    self.received_ = X
    self.sended_ = X

    return self
