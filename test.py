from fpeg.pipeline import Pipeline
from fpeg.codec import HuffmanCodec
from fpeg.utils.process import *
from fpeg.utils.io import Reader, Writer


if __name__ == "__main__":
  pipeline = Pipeline([
                      ("reader0", Reader()),
                      ("level shifter0", LevelShifter()),
                      ("normalizer0", Normalizer()),
                      ("color transformer0", ColorTransformer()),
                      ("spliter0", Spliter()),
                      ("codec0", HuffmanCodec()),
                      ("spliter1", Spliter()),
                      ("color transformer1", ColorTransformer()),
                      ("normalizer1", Normalizer()),
                      ("level shifter1", LevelShifter()),
                      ("writer0", Writer())
                      ],
                      params={
                      "reader0": {"flag": "color"},
                      "level shifter0": {"depth": 8},
                      "normalizer0": {"depth": 8},
                      "color transformer0": {"mode": "transform", "lossy": True},
                      "spliter0": {"tile_shape": (256, 256)},
                      "codec0": {"mode": "encode", "accelerated": False, "use_lut": False},
                      "spliter1": {"mode": "recover", "block_shape": (4, 5)},
                      "color transformer1": {"mode": "reverse transform", "lossy": True},
                      "normalizer1": {"mode": "denormalize", "depth": 8},
                      "level shifter1": {"mode": "reverse shift", "depth": 8},
                      "writer0": {"path": r"out/mudrock.jpg"}
                      })

  path = r"in/rosmontis.jpg"
  pipeline.recv(path)
  print(pipeline.get_log())
