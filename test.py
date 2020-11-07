from fpeg.pipeline import Pipeline
from fpeg.codec import HuffmanCodec
from fpeg.utils.preprocess import Spliter
from fpeg.utils.io import Reader

if __name__ == "__main__":
  pipeline = Pipeline([
                      ("reader0", Reader()),
                      ("spliter0", Spliter()),
                      ("codec0", HuffmanCodec())
                      ],
                      params={
                      "reader0": {"flag": "color"},
                      "spliter0": {"tile_shape": (256, 256)},
                      "codec0": {
                        "mode": "encode",
                        "dhts": [],
                        "accelerated": True
                       }
                      })

  pipeline.set_pipe_params(**{
                           "codec0": {
                              "use_lut": True,
                           }
                           })

  path = r"in/mudrock.jpg"
  pipeline.recv(path)
  print(pipeline.get_log())

  pipeline.set_pipe_params(**{
                           "codec0": {
                              "accelerated": False
                           }
                           })

  path = r"in/rosmontis.jpg"
  pipeline.recv(path)
  print(pipeline.get_log())

  pipeline.set_pipe_params(**{
                          "codec0": {
                            "mode": "decode",
                            "dhts": [],
                            "accelerated": True
                          }
                          })

  path = r"in/mudrock.jpg"
  pipeline.recv(path)
  print(pipeline.get_log())

  pipeline.set_pipe_params(**{
                           "codec0": {
                              "accelerated": False
                           }
                           })


  path = r"in/rosmontis.jpg"
  pipeline.recv(path)
  print(pipeline.get_log())
