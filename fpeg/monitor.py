class Monitor:
  """
  Monitor of pipes in a pipeline.

  Monitor gathers the data recieved and sended by pipes. When monitor is not waking, do not send data to it.
  """
  def __init__(self):
    self.data = []
    self.logs = []
    self.params = []
    self.waking = False
  
  def gather(self, name, data, log, params):
    if not self.waking:
      raise RuntimeError("Monitor is sleeping. Do not send message to the monitor.")

    self.data[-1][name] = data
    self.logs[-1][name] = log
    self.params[-1][name] = params
    self.sleep()

  def report(self):
    return self.data, self.logs

  def wake(self):
    self.waking = True

  def sleep(self):
    self.waking = False

  def prepare(self):
    self.data.append({})
    self.logs.append({})
    self.params.append({})
