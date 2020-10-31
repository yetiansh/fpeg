class Monitor:
  """
  Monitor of pipes in a pipeline.

  Monitor gathers the data recieved and sended by pipes. When monitor is not waking, do not send data to it.
  """
  def __init__(self):
    self.datas = []
    self.logs = []
    self.waking = False

  def gather(data, log):
    if not self.waking:
      raise RuntimeError("Monitor is sleeping. "
                         "Do not send message to the monitor.")
    self.datas.append(data)
    self.logs.append(log)
    self.waking = False

  def report():
    return self.data, self.log
