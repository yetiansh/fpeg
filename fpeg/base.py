from collections import defaultdict
from inspect import signature


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
    self.logger.log()
    self.monitor.gather(self.respond())

    return self.X_recieved_, self.X_sended_

  def respond(self):
    """
    Respond to the monitor.

    Pipe should support a monitor to trace its history of
    recieving and sending data.
    """
    if not self.send:
      raise RuntimeError("The send method hasn't been called yet. "
                         "Do not send message to the monitor.")
    self.send = False
    return (self.X_recieved_, self.X_sended_), self.log[-1], self.get_params()

  def accelerate(self, **params):
    """
    Start a pool for subprocesses when number of tasks is more than a certain value.
    """
    try:
      self.task_number = params["task_number"]
    except KeyError as err:
      msg = "Task number must be specified."
      self.logger.error(msg)
      raise err

    try:
      self.max_pool_size = params["max_pool_size"]
    except KeyError:
      pass

    try:
      self.accelerate = params["accelerate"]
    except KeyError:
      self.accelerate = self.accelerate or bool(task_number < self.min_task_number)

    if self.accelerate:
      self.pool = None
    else:
      self.pool = Pool(min(task_number, self.max_pool_size))

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
    names = self._get_record_names()
    params = {}
    for name in names:
      params[name] = []

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

  @classmethod
  def _get_record_names(cls):
    names = self._get_param_names()
    excluded_names = ["name", "mode"]
    return sorted([name for name in names if name not in excluded_names])

  def __repr__(self):
    """
    Pretty print the pipe.
    """
    return self.pretty_printer.print(self.get_params())


class Codec(Pipe):
  """
  Base class of encoders and decoders.

  In FPEG, coding and decoding methods like Huffman coding, Shannon coding and Entropy coding are implemented as codecs.
  """

  def recv(self, X, **params):
    """
    Recieve stream of data.
    """
    self.accelerate(**params)
    self.X_recieved_ = X
    if self.mode == "encode":
      self.X_sended_ = self.encode(X, **params)
    elif self.mode == "decode":
      self.X_sended_ = self.decode(X, **params)
    else:
      msg = "Invalid parameter %s for codec %s. "
            "Codec.mode should be set to \"encode\" "
            "or \"decode\"." % (self)
      self.logger.error(msg)
      raise ValueError(msg)

    return self


class Transformer(Pipe):
  """
  Base class of transformers and inverse-transformers.

  In FPEG, transforms and inverse transforms like fft, ifft, dwt and idwt are implemented as transformers.
  """

  def recv(self, X, **params):
    self.accelerate(**params)
    self.X_recieved_ = X
    if self.mode == "forward":
      self.X_sended_ = self.forward(X, **params)
    elif self.mode == "backward":
      self.X_sended_ = self.backward(X, **params)
    else:
      msg = "Invalid parameter %s for transformer %s. "
            "Transformer.mode should be set to \"forward\" "
            "or \"backward\"." % (self)
      self.logger.error(msg)
      raise ValueError(msg)

    return self
    

class Processor(Pipe):
  """
  Base class of preprocessor, postprocessor, stream organizer and decomposer.

  In FPEG, preprocess, postprocess, stream organization and decomposition methods are implemented as processors.
  """
  
  def recv(self, X, **params):
    self.accelerate(**params)
    self.X_recieved_ = X
    if self.mode == "process":
      self.X_sended_ = self.process(X, **params)
    elif self.mode == "inverse_process":
      self.X_sended_ = self.inverse_process(X, **params)
    else:
      raise ValueError("Invalid parameter %s for transformer %s. "
                       "Transformer.mode should be set to \"forward\" "
                       "or \"backward\"." %
                       (self))

    return self