import pickle
import numpy as np
import cv2

from fpeg.pipeline import Pipeline
from fpeg.codec import EBCOTCodec
from fpeg.transformer import DWTransformer, PCATransformer
from fpeg.metrics import PSNRTester
from fpeg.utils import *


if __name__ == "__main__":
  D = 3
  pipeline = Pipeline([
                      ("reader0", Reader()),
                      ("level shifter0", LevelShifter()),
                      ("normalizer0", Normalizer()),
                      ("color transformer0", ColorTransformer()),
                      ("spliter0", Spliter()),
                      ("dw transformer0", DWTransformer()),
                      ("quantizer0", Quantizer()),
                      ("ebcot codec0", EBCOTCodec())
                      ],
                      params={
                      "reader0": {"flag": "color"},
                      "level shifter0": {"mode": "shift", "depth": 8},
                      "normalizer0": {"mode": "normalize", "depth": 8},
                      "color transformer0": {"mode": "transform", "lossy": True},
                      "spliter0": {"tile_shape": (256, 256)},
                      "dw transformer0": {"mode": "forward", "lossy": True, "D": D},
                      "quantizer0": {"mode": "quantify", "irreversible": True, "D": D},
                      "ebcot codec0": {"mode": "encode", "accelerated": False, "tile_shape": (256, 256), "D": D}
                      })

  path = r"in/penguim.jpg"
  pipeline.recv(path)
  out = pipeline.monitor.data[-1]["ebcot codec0"]
  print(pipeline.get_log())
  pickle.dump(out, open(r"out.bin", "wb"))

  out = pickle.load(open(r"out.bin", "rb"))[1]
  pipeline1 = Pipeline([
                      ("ebcot codec1", EBCOTCodec()),
                      ("quantizer1", Quantizer()),
                      ("dw transformer1", DWTransformer()),
                      ("spliter1", Spliter()),
                      ("color transformer1", ColorTransformer()),
                      ("normalizer1", Normalizer()),
                      ("level shifter1", LevelShifter()),
                      ("writer0", Writer())
                      ],
                      params={
                      "ebcot codec1": {"mode": "decode", "accelerated": False, "D": D},
                      "quantizer1": {"mode": "dequantify", "irreversible": True, "accelerated": False, "D": D},
                      "dw transformer1": {"mode": "backward", "lossy": True, "D": D},
                      "spliter1": {"block_shape": (1, 1), "mode": "recover"},
                      "color transformer1": {"mode": "reverse transform", "lossy": True},
                      "normalizer1": {"mode": "denormalize", "depth": 8},
                      "level shifter1": {"mode": "reverse shift", "depth": 8},
                      "writer0": {"path": r"out/out1.jpg"}
                      })

  pipeline1.recv(out)
  print(pipeline1.get_log())

  out1 = pipeline1.monitor.data
  pickle.dump(out1, open(r"out1.bin", "wb"))

  out2 = pickle.load(open(r"out1.bin", "rb"))
  ebcot_input0 = out2[0]["ebcot codec0"][0]
  ebcot_output1 = out2[1]["ebcot codec1"][1]
  for tile0, tile1 in zip(ebcot_input0, ebcot_output1):
    for subbands0, subbands1 in zip(tile0, tile1):
      if isinstance(subbands0, tuple):
        print([np.max(np.abs((subband0 - subband1))) for subband0, subband1 in zip(subbands0, subbands1)])
        # print([np.abs((subband0 - subband1)) for subband0, subband1 in zip(subbands0, subbands1)])
      else:
        print(np.max(np.abs((subbands0 - subbands1))))
        # print(np.abs((subbands0 - subbands1)))

  quantizer_input0 = out2[0]["quantizer0"][0]
  quantizer_output0 = out2[0]["quantizer0"][1]
  quantizer_input1 = out2[1]["quantizer1"][0]
  quantizer_output1 = out2[1]["quantizer1"][1]
  for tile0, tile1 in zip(quantizer_input0, quantizer_output1):
    for subbands0, subbands1 in zip(tile0, tile1):
      if isinstance(subbands0, tuple):
        print([np.max(np.abs((subband0 - subband1))) for subband0, subband1 in zip(subbands0, subbands1)])
        # print([np.abs((subband0 - subband1)) for subband0, subband1 in zip(subbands0, subbands1)])
      else:
        print(np.max(np.abs((subbands0 - subbands1))))
        # print(np.abs((subbands0 - subbands1)))
  # #
  # # dwtransformer_input0 = pipeline.monitor.data[-1]["dw transformer0"][0]
  # # dwtransformer_output1 = pipeline.monitor.data[-1]["dw transformer1"][1]
  # # for tile0, tile1 in zip(dwtransformer_input0, dwtransformer_output1):
  # #   print(np.max(np.abs((tile0 - tile1))))
  # #   print(np.abs((tile0 - tile1)))
  # #
  # # colortransformer_input0 = pipeline.monitor.data[-1]["color transformer0"][0]
  # # colortransformer_output1 = pipeline.monitor.data[-1]["color transformer1"][1]
  # # for tile0, tile1 in zip(colortransformer_input0, colortransformer_output1):
  # #   print(np.max(np.abs((tile0 - tile1))))
  # #   print(np.abs((tile0 - tile1)))