__all__ = [
	"DWTransformer"
]

import numpy as np
from pywt import wavedec2, Wavelet, waverec2

from ..base import Transformer
from ..config import read_config
from ..funcs.funcs import cat_arrays_2d, dcps_array_3d

config = read_config()

D = config.get("jpeg2000", "D")
dwt_coeffs = config.get("jpeg2000", "dwt_coeffs")

min_task_number = config.get("accelerate", "transformer_min_task_number")
max_pool_size = config.get("accelerate", "transformer_max_pool_size")


class DWTransformer(Transformer):
	"""
	Discrete Wavelet Transformer.
	"""

	def __init__(self,
	             name="dwt transformer",
	             mode="forward",
	             lossy=True,
	             D=D,
	             accelerated=False):
		"""
		Init and set attributes of a discrete wavelet transformer.

		Explicit Attributes
		-------------------
		name: str, optional
		  Name of the codec.
		mode: str, optional
		  Mode of the codec, must in ["encode", "decode"].
		lossy: bool, optional
      Whether the transform is loss or lossless.
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
		self.D = D
		self.lossy = lossy
		self.accelerated = accelerated

		self.db97_coeffs, self.lg53_coeffs = dwt_coeffs[0], dwt_coeffs[1]
		self.min_task_number = min_task_number
		self.max_pool_size = max_pool_size

	def forward(self, X, **params):
		try:
			self.lossy = params["lossy"]
		except KeyError:
			pass

		if self.lossy:
			# wavelet = Wavelet('DB97', self.db97_coeffs)
			wavelet = 'bior2.2'
		else:
			wavelet = Wavelet('LG53', self.lg53_coeffs)

		coeffs = []
		for x in X:
			channel0_coeff = wavedec2(x[:, :, 0], wavelet, level=self.D)
			channel1_coeff = wavedec2(x[:, :, 1], wavelet, level=self.D)
			channel2_coeff = wavedec2(x[:, :, 2], wavelet, level=self.D)
			a_coeff = cat_arrays_2d([channel0_coeff[0],
			                         channel1_coeff[0],
			                         channel2_coeff[0]])

			coeff = [a_coeff]
			for i in range(1, self.D + 1):
				h_coeff = cat_arrays_2d([channel0_coeff[i][0],
				                         channel1_coeff[i][0],
				                         channel2_coeff[i][0]])
				v_coeff = cat_arrays_2d([channel0_coeff[i][1],
				                         channel1_coeff[i][1],
				                         channel2_coeff[i][1]])
				d_coeff = cat_arrays_2d([channel0_coeff[i][2],
				                         channel1_coeff[i][2],
				                         channel2_coeff[i][2]])
				coeff.append((h_coeff, v_coeff, d_coeff))

			coeffs.append(coeff)

		return coeffs

	def backward(self, X, **params):
		try:
			self.lossy = params["lossy"]
		except KeyError:
			pass

		if self.lossy:
			# wavelet = Wavelet('DB97', self.db97_coeffs)
			wavelet = 'bior2.2'
		else:
			wavelet = Wavelet('LG53', self.lg53_coeffs)

		tiles = []
		for x in X:
			channel0_a_coeff, channel1_a_coeff, channel2_a_coeff = dcps_array_3d(x[0])

			channel0_coeff = [channel0_a_coeff]
			channel1_coeff = [channel1_a_coeff]
			channel2_coeff = [channel2_a_coeff]

			for i in range(1, len(x)):
				if i < self.D + 1:
					channel0_h_coeff, channel1_h_coeff, channel2_h_coeff = dcps_array_3d(x[i][0])
					channel0_v_coeff, channel1_v_coeff, channel2_v_coeff = dcps_array_3d(x[i][1])
					channel0_d_coeff, channel1_d_coeff, channel2_d_coeff = dcps_array_3d(x[i][2])
				else:
					channel0_h_coeff, channel1_h_coeff, channel2_h_coeff = dcps_array_3d(np.zeros_like(x[i][0]))
					channel0_v_coeff, channel1_v_coeff, channel2_v_coeff = dcps_array_3d(np.zeros_like(x[i][1]))
					channel0_d_coeff, channel1_d_coeff, channel2_d_coeff = dcps_array_3d(np.zeros_like(x[i][2]))

				channel0_coeff.append((channel0_h_coeff, channel0_v_coeff, channel0_d_coeff))
				channel1_coeff.append((channel1_h_coeff, channel1_v_coeff, channel1_d_coeff))
				channel2_coeff.append((channel2_h_coeff, channel2_v_coeff, channel2_d_coeff))

			channel0 = waverec2(channel0_coeff, wavelet)
			channel1 = waverec2(channel1_coeff, wavelet)
			channel2 = waverec2(channel2_coeff, wavelet)
			tiles.append(cat_arrays_2d([channel0, channel1, channel2]))

		return tiles
