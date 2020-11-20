from fpeg.pipeline import Pipeline
from fpeg.codec import EBCOTCodec
from fpeg.transformer import DWTransformer
from fpeg.utils import *


if __name__ == "__main__":
  pipeline = Pipeline([
                      ("reader0", Reader()),
                      ("level shifter0", LevelShifter()),
                      ("normalizer0", Normalizer()),
                      ("color transformer0", ColorTransformer()),
                      ("spliter0", Spliter()),
                      ("dw transformer0", DWTransformer()),
                      ("quantizer0", Quantizer()),
                      ("codec0", EBCOTCodec()),
                      ],
                      params={
                      "reader0": {"flag": "color"},
                      "level shifter0": {"depth": 8},
                      "normalizer0": {"depth": 8},
                      "color transformer0": {"mode": "transform", "lossy": True},
                      "spliter0": {"tile_shape": (256, 256)},
                      "dw transformer0": {"mode": "forward", "lossy": True},
                      "quantizer0": {"mode": "quantify", "irreversible": False},
                      "codec0": {"mode": "encode", "accelerated": True}
                      })

  path = r"in/rosmontis.jpg"
  pipeline.recv(path)
  print(pipeline.get_log())
