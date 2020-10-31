import configparser


config_path = r"config.ini"
config = configparser.RawConfigParser()
config.add_section("accelerate")
config.set("accelerate", "codec_min_task_number", 10)
config.set("accelerate", "codec_max_pool_size", 30)

with open(config_path, 'w') as file:
  config.write(file)
