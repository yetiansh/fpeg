__all__ = [
  "Tester"
]


from pprint import PrettyPrinter
from .config import read_config

config = read_config()

pprint_option = config.get_section("pprint")


class Tester:
  def __init__(self, func, **kwargs):
    self.func = func
    self.kwargs = kwargs

    self.pprinter = PrettyPrinter(**pprint_option)

  def eval(self, X):
    return self.func(X, **self.kwargs)

  def set_params(self, **params):
    for name in params:
      if name in self.kwargs:
        self.kwargs[name] = params[name]

  def __repr__(self):
    return "Tester with attributes: " + self.pprinter.pformat({"func": self.func, "kwargs": self.kwargs})
