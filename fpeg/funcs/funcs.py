__all__ = [
  "cat_arrays_2d",
  "dcps_array_3d"
]


import numpy as np


def cat_arrays_2d(*arrays_2d):
  if not len(arrays_2d):
    return None

  array_3d = np.array(arrays_2d)
  array_3d = np.swapaxes(array_3d, 0, 1)
  array_3d = np.swapaxes(array_3d, 1, 2)

  return array_3d


def dcps_array_3d(array_3d):
  return [arrays_3d[:, :, i] for i in range(arrays_3d.shape[2])]
