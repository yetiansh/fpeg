from inspect import signature, Parameter
from multiprocessing import Pool


class Pipe:
  """
  Base pipe class for all pipes.

  In FPEG, processors, transformers and encoders are pipes which can be filled into a pipeline to create brand new compress and decompress algorithms.

  References
  ----------
  [1] Lars Buitinck, Gilles Louppe, Mathieu Blondel et al. "API design for machine learning software: experiences from the scikit-learn project" in European Conference on Machine Learning and Principles and Practices of Knowledge Discovery in Databases (2013).
  """

  def recv_send(self, X, **params):
    """
    Recieve and send data.
    """
    return self.recv(X, **params).send()

  def recv(self, X, **params):
    """
    Just let subclass rewrite this method.

    Data recieved by the pipe are processed and stored when this recv method is called.
    """
    return self

  def send(self):
    """
    Send the recieved and processed data, add a log record and send the monitor a message.
    """
    self.send = True
    self.monitor.gather(*self.respond())

    return self.recieved_, self.sended_

  def respond(self):
    """
    Respond to the monitor.

    Pipe should support a monitor to trace its history of
    recieving and sending data.
    """
    if not self.send:
      msg = "Send method hasn't been called yet, do not send message to the monitor."
      self.logs[-1] += self.formatter.error(msg)
      raise RuntimeError(msg)

    self.send = False
    return (self.recieved_, self.sended_), self.logs[-1], self.get_params()

  def accelerate(self, **params):
    """
    Start a pool for subprocesses when number of tasks is more than a certain value.
    """
    try:
      self.task_number = params["task_number"]
    except KeyError as err:
      msg = "\"task_number\" must be passed to the accelerate method."
      self.logs[-1] += self.formatter.error(msg)
      raise err

    try:
      self.max_pool_size = params["max_pool_size"]
    except KeyError:
      pass

    try:
      self.accelerate = params["accelerate"]
    except KeyError:
      self.accelerate = self.accelerate or bool(self.task_number < self.min_task_number)

    if self.accelerate:
      self.pool = Pool(min(self.task_number, self.max_pool_size))

  def set_params(self, **params):
    if not params:
      return self

    valid_params = self.get_params()
    for key, value in params.items():
      if key not in valid_params:
        raise ValueError("Invalid parameter %s for pipe %s. "
                         "Check the list of available parameters "
                         "with `pipe.get_params().keys()`." %
                         (key, self))
      else:
        setattr(self, key, value)

  def get_params(self):
    out = {}
    for key in self._get_param_names():
      try:
        value = getattr(self, key)
      except AttributeError:
        value = None

      out[key] = value

    return out

  def _clear_record(self):
    init = self.__init__
    if init is object.__init__:
      return

    params = {}
    excluded_names = ["self", "name", "mode", "flag"]
    init_signature = signature(init)
    for key, val in init_signature.parameters.items():
      if key not in excluded_names and val.default is not Parameter.empty:
        params[key] = val.default

    self.setattr(**params)

  @classmethod
  def _get_param_names(cls):
    init = cls.__init__
    if init is object.__init__:
      return []

    init_signature = signature(init)
    parameters = [p for p in init_signature.parameters.values()
                  if p.name != 'self' and p.kind != p.VAR_KEYWORD]
    return sorted([p.name for p in parameters])

  def __repr__(self):
    """
    Pretty print the pipe.
    """
    return self.pprinter.print(self.get_params())


class Codec(Pipe):
  """
  Base class of encoders and decoders.

  In FPEG, coding and decoding methods like Huffman coding, Shannon coding and Entropy coding are implemented as codecs.
  """

  def recv(self, X, **params):
    """
    Recieve stream of data.
    """
    self.logs.append("")
    self.accelerate(**params)
    self.recieved_ = X
    if self.mode == "encode":
      self.sended_ = self.encode(X, **params)
    elif self.mode == "decode":
      self.sended_ = self.decode(X, **params)
    else:
      msg = "Invalid attribute %s for codec %s. Codec.mode should be set to \"encode\" or \"decode\"." % (self.mode, self)
      self.logs[-1] += self.formatter.error(msg)
      raise AttributeError(msg)

    return self


class Transformer(Pipe):
  """
  Base class of transformers and inverse-transformers.

  In FPEG, transforms and inverse transforms like fft, ifft, dwt and idwt are implemented as transformers.
  """

  def recv(self, X, **params):
    self.logs.append("")
    self.accelerate(**params)
    self.recieved_ = X
    if self.mode == "forward":
      self.sended_ = self.forward(X, **params)
    elif self.mode == "backward":
      self.sended_ = self.backward(X, **params)
    else:
      msg = "Invalid attribute %s for transformer %s. Transformer.mode should be set to \"forward\" or \"backward\"." % (self.mode, self)
      self.logs[-1] += self.formatter.error(msg)
      raise AttributeError(msg)

    return self
