from fpeg.pipeline import Pipeline
from fpeg.utils.preprocess import Spliter
from fpeg.utils.io import Reader


spliter = Spliter(name="spliter0")
reader = Reader(name="reader0")

pipeline = Pipeline([
                    ("reader0", reader),
                    ("spliter0", spliter)
                    ],
                    params={
                      "reader0": {"flag": "grayscale"},
                      "spliter0": {"tile_shape": (128, 256)}
                    })


path = r"in/mudrock.png"
pipeline.recv(path)

path = r"in/rosmontis.png"
pipeline.recv(path)

for i in range(5):
  pipeline.set_params(**{
                        "reader0": {"flag": "grayscale"},
                        "spliter0": {"tile_shape": (128 + 4 ** i,
                          256 - 3 ** i)}
                      })
  pipeline.recv(path)

for pipe in pipeline.pipes:
  print(pipe)

for log in pipeline.monitor.logs:
  print(''.join(log))

for params in pipeline.monitor.params:
  print(params)
