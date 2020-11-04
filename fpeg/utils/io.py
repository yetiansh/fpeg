import cv2
from ..base import Pipe
from ..config import Config
from ..log import Formatter
from ..printer import Pprinter


config_path = r"config.ini"
config = Config(config_path)

fmt = config.get("log", "fmt")


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

    Implicit Attributes
    -------------------
    logs: str
      Log messages of recieving and sending data.
    formatter: Formatter
      Formatter for generating log messages.
    pprinter: fpeg.utils.pprint.Pprinter
      Pretty printer for printing reader.
    """
    self.name = name
    self.flag = flag

    self.logs = []
    self.formatter = Formatter(fmt=fmt)
    self.pprinter = Pprinter()

  def recv(self, path, **params):
    self.recieved_ = path
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
    for i in range(X.shape[2]):
      self.sended_.append(X[:, :, i])

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

    Implicit Attributes
    -------------------
    logs: str
      Log messages of recieving and sending data.
    formatter: Formatter
      Formatter for generating log messages.
    pprinter: fpeg.printer.Pprinter
      Pretty printer for printing reader.
    """
    self.name = name

    self.logs = []
    self.formatter = Formatter(fmt=fmt)
    self.pprinter = Pprinter()

  def recv(self, X, **params):
    self.recieved_ = X
    self.sended_ = X

    return self