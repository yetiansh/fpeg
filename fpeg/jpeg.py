from fpeg.pipeline import Pipeline
from fpeg.codec import EBCOTCodec
from fpeg.transformer import DWTransformer
from fpeg.utils import *


def jpeg2000_compress(args):
  if args.lossy:
    pipeline = Pipeline([
                        ("reader0", Reader()),
                        ("level shifter0", LevelShifter()),
                        ("normalizer0", Normalizer()),
                        ("color transformer0", ColorTransformer()),
                        ("spliter0", Spliter()),
                        ("dw transformer0", DWTransformer()),
                        ("quantizer0", Quantizer()),
                        ("ebcot codec0", EBCOTCodec()),
                        ("writer0", Writer())
                        ],
                        params={
                          "reader0": {"binary": False, "flag": "color"},
                          "level shifter0": {"mode": "shift", "depth": args.depth},
                          "normalizer0": {"mode": "normalize", "depth": args.depth},
                          "color transformer0": {"mode": "transform", "lossy": True},
                          "spliter0": {"tile_shape": args.tile_shape},
                          "dw transformer0": {"mode": "forward", "lossy": True, "D": args.level},
                          "quantizer0": {"mode": "quantify", "irreversible": True, "D": args.level},
                          "ebcot codec0": {"mode": "encode", "accelerated": args.accelerated, "tile_shape": args.tile_shape},
                          "writer0": {"path": args.output, "binary": True}
                        })
  else:
    pipeline = Pipeline([
                        ("reader0", Reader()),
                        ("level shifter0", LevelShifter()),
                        ("color transformer0", ColorTransformer()),
                        ("spliter0", Spliter()),
                        ("dw transformer0", DWTransformer()),
                        ("quantizer0", Quantizer()),
                        ("ebcot codec0", EBCOTCodec()),
                        ("writer0", Writer())
                        ],
                        params={
                          "reader0": {"binary": True},
                          "level shifter0": {"mode": "shift", "depth": args.depth},
                          "normalizer0": {"mode": "normalize", "depth": args.depth},
                          "color transformer0": {"mode": "transform", "lossy": False},
                          "spliter0": {"tile_shape": args.tile_shape},
                          "dw transformer0": {"mode": "forward", "lossy": False, "D": args.level},
                          "quantizer0": {"mode": "quantify", "irreversible": False, "D": args.level},
                          "ebcot codec0": {"mode": "encode", "accelerated": args.accelerated, "tile_shape": args.tile_shape},
                          "writer0": {"path": args.output, "binary": False}
                        })
  pipeline.recv(args.input)
  print(pipeline.get_log())


def jpeg2000_decompress(args):
  pipeline = Pipeline([
                      ("reader0", Reader()),
                      ("ebcot codec0", EBCOTCodec()),
                      ("quantizer0", Quantizer()),
                      ("dw transformer0", DWTransformer()),
                      ("spliter0", Spliter()),
                      ("color transformer0", ColorTransformer()),
                      ("normalizer0", Normalizer()),
                      ("level shifter0", LevelShifter()),
                      ("writer0", Writer())
                      ],
                      params={
                      "reader0": {"flag": "color"},
                      "ebcot codec0": {"mode": "encode", "accelerated": False, "tile_shape": (256, 256)},
                      "quantizer1": {"mode": "dequantify", "irreversible": True, "D": 5},
                      "dw transformer1": {"mode": "backward", "lossy": True, "D": 5},
                      "spliter1": {"block_shape": (4, 5), "mode": "recover"},
                      "color transformer1": {"mode": "reverse transform", "lossy": True},
                      "normalizer1": {"mode": "denormalize", "depth": 8},
                      "level shifter1": {"mode": "reverse shift", "depth": 8},
                      "writer0": {"path": args.output}
                      })
  pipeline.recv(args.input)
  print(pipeline.get_log())
