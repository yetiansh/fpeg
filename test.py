from fpeg.pipeline import Pipeline
from fpeg.codec import HuffmanCodec
from fpeg.utils.process import Spliter, LevelShifter, Normalizer
from fpeg.utils.io import Reader, Writer


if __name__ == "__main__":
  pipeline = Pipeline([
                      ("reader0", Reader()),
                      ("spliter0", Spliter()),
                      ("level shifter0", LevelShifter()),
                      ("normalizer0", Normalizer()),
                      ("codec0", HuffmanCodec()),
                      ("normalizer1", Normalizer()),
                      ("level shifter1", LevelShifter()),
                      ("spliter1", Spliter()),
                      ("writer0", Writer())
                      ],
                      params={
                      "reader0": {"flag": "color"},
                      "spliter0": {"tile_shape": (256, 256)},
                      "codec0": {"mode": "encode", "accelerated": False, "use_lut": False},
                      "level shifter0": {"depth": 8},
                      "normalizer0": {"depth": 8},
                      "normalizer1": {"mode": "recover", "depth": 8},
                      "level shifter1": {"mode": "recover", "depth": 8},
                      "spliter1": {"mode": "recover", "block_shape": (4, 5)},
                      "writer0": {"path": r"out/mudrock.jpg"}
                      })

  path = r"in/mudrock.jpg"
  pipeline.recv(path)
  print(pipeline.get_log())
