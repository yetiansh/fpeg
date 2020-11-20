import os
import pickle


absdir = os.path.split(os.path.abspath(__file__))[0]
config_path = os.path.join(absdir, "config.dat")


class Config:
  def __init__(self, 
               path=None):
    if path is not None:
      self.path = path
      self.read(path)
    else:
      self.path = None
      self.config = {}

  def get(self, section, item):
    if section in self.config:
      if item in self.config[section]:
        return self.config[section][item]

    return None

  def set(self, section, item, value):
    if section in self.config:
      if item not in self.config[section]:
        self.config[section][item] = value

  def add_section(self, section):
    if section in self.config:
      return

    self.config[section] = {}

  def get_section(self, section):
    if section not in self.config:
      return {}

    return self.config[section]

  def read(self,
           path=None):
    if path is None:
      path = self.path

    self.config = pickle.load(open(path, "rb"))

  def write(self,
            path=None):
    if path is None:
      path = self.path

    pickle.dump(self.config, open(path, "wb"))


def read_config():
  return Config(config_path)


if __name__ == "__main__":
  from funcs import *

  config = Config()

  config.add_section("accelerate")
  config.set("accelerate", "codec_min_task_number", 10)
  config.set("accelerate", "codec_max_pool_size", 10)

  config.add_section("log")
  config.set("log", "time_format", "%Y-%m-%d %H:%M:%S")

  config.add_section("pprint")
  config.set("pprint", "indent", 2)
  config.set("pprint", "width", 80)

  config.add_section("io")
  config.set("io", "read_dir", os.path.abspath(os.path.join(absdir, "..", "in")))
  config.set("io", "write_dir", os.path.abspath(os.path.join(absdir, "..", "out")))
  config.set("io", "default_filename", "foobar.jpg")

  config.add_section("jpeg2000")
  config.set("jpeg2000", "D", 3)
  config.set("jpeg2000", "G", 1)
  config.set("jpeg2000", "QCD", "1000011111111")
  config.set("jpeg2000", "delta_vb", 0.5)
  config.set("jpeg2000", "tile_shape", (256, 256))
  config.set("jpeg2000", "depth", 8)
  config.set("jpeg2000", "mq_table", mq_table())
  config.set("jpeg2000", "dwt_coeffs", dwt_coeffs())

  config.write(config_path)
