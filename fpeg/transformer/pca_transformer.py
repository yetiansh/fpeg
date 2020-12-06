__all__ = [
  "PCATransformer"
]


import numpy as np
from sklearn.decomposition import PCA
from ..base import Transformer
from ..config import read_config
from ..funcs.funcs import cat_arrays_2d, dcps_array_3d

config = read_config()

n_components = config.get("fpeg", "n_components")

min_task_number = config.get("accelerate", "transformer_min_task_number")
max_pool_size = config.get("accelerate", "transformer_max_pool_size")

class PCATransformer(Transformer):
  def __init__(self,
               name="pca transformer",
               mode="forward",
               n_components=n_components,
               accelerated=False):
    """
    Init and set attributes of a principle component analysis transformer.

    Explicit Attributes
    -------------------
    name: str, optional
      Name of the codec.
    mode: str, optional
      Mode of the codec, must in ["encode", "decode"].
    n_components: int, optional
      Number of principle components.
    accelerated: bool, optional
      Whether the process would be accelerated by subprocess pool.

    Implicit Attributes
    -------------------
    min_task_number: int
      Minimun task number to start a pool.
    max_pool_size: int
      Maximun size of pool.
    """
    super().__init__()

    self.name = name
    self.mode = mode
    self.accelerated = accelerated

    self.min_task_number = min_task_number
    self.max_pool_size = max_pool_size

  def forward(self, X, **params):
    pca = PCA(n_components=self.n_components)
    components = []
    for x in X:
      channel0, channel1, channel2 = dcps_array_3d(x)
      component0 = pca.fit_transform(channel0)
      cov0 = pca.components_
      mean0 = pca.mean_
      component1 = pca.fit_transform(channel1)
      cov1 = pca.components_
      mean1 = pca.mean_
      component2 = pca.fit_transform(channel2)
      cov2 = pca.components_
      mean2 = pca.mean_
      component = cat_arrays_2d([component0, component1, component2])
      cov = cat_arrays_2d([cov0, cov1, cov2])
      mean = np.array([mean0, mean1, mean2])
      components.append([component, cov, mean])

    return components

  def backward(self, X, **params):
    try:
      self.lossy = params["lossy"]
    except KeyError:
      pass

    try:
      self.n_components = params["n_components"]
    except KeyError:
      pass

    pca = PCA(n_components=self.n_components)
    tiles = []
    for x in X:
      component, cov, mean = x
      component0, component1, component2 = dcps_array_3d(component)
      cov0, cov1, cov2 = dcps_array_3d(cov)
      mean0, mean1, mean2 = mean[0], mean[1], mean[2]
      pca.components_ = cov0[:self.n_components, :self.n_components]
      pca.mean_ = mean0[:self.n_components]
      channel0 = pca.inverse_transform(component0[:, :self.n_components])
      pca.components_ = cov2[:self.n_components, :self.n_components]
      pca.mean_ = mean1[:self.n_components]
      channel1 = pca.inverse_transform(component1[:, :self.n_components])
      pca.components_ = cov2[:self.n_components, :self.n_components]
      pca.mean_ = mean2[:self.n_components]
      channel2 = pca.inverse_transform(component2[:, :self.n_components])

      tiles.append(cat_arrays_2d([channel0, channel1, channel2]))

    return tiles
