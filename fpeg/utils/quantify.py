__all__ = [
	"Quantizer"
]

from multiprocessing import Pool

import numpy as np

from ..base import Pipe
from ..config import read_config
from ..funcs import parse_marker

config = read_config()

D = config.get("jpeg2000", "D")
QCD = config.get("jpeg2000", "QCD")
delta_vb = config.get("jpeg2000", "delta_vb")
reserve_bits = config.get("jpeg2000", "reserve_bits")

min_task_number = config.get("accelerate", "codec_min_task_number")
max_pool_size = config.get("accelerate", "codec_max_pool_size")


class Quantizer(Pipe):
	"""
	Quantizer
	"""

	def __init__(self,
							 name="Quantizer",
							 mode="quantify",
							 irreversible=False,
							 accelerated=False,
							 D=D,
							 QCD=QCD,
							 delta_vb=delta_vb,
							 reserve_bits=reserve_bits):
		"""
		Init and set attributes of a quantizer.

		Explicit Attributes
		-------------------
		name: str, ofptional
			Name of the quantizer.
		mode: str, optional
			Mode of quantizer, must in ["quantify", "dequantify"].
		irreversible: bool, optional
			Whether the transform is lossy or lossless.
		accelerated: bool, optional
			Whether the process would be accelerated by subprocess pool.
		D: int, optional
			Number of resolution layers.
		QCD: str, optional
			Quantization default used to specify epsilon_b and mu_b of subband with lowest resolution.
		delta_vb: float, optional
			Used in dequantization, ranges from 0 to 1.

		Implicit Attributes
		-------------------
		epsilon_b: int
			Epsilon used to determine the quantization step of subband with lowest resolution, ranges from 0 to 2^5.
		mu_b: int
			Mu used to determine the quantization step of subband with lowest resolution, ranges from 0 to 2^11.
		min_task_number: int
			Minimun task number to start a pool.
		max_pool_size: int
			Maximun size of pool.
		"""
		super().__init__()

		self.name = name
		self.mode = mode
		self.irreversible = irreversible
		self.accelerated = accelerated
		self.D = D
		self.QCD = QCD
		self.delta_vb = delta_vb
		self.reserve_bits = reserve_bits

		self.epsilon_b, self.mu_b = parse_marker(self.QCD)
		self.min_task_number = min_task_number
		self.max_pool_size = max_pool_size

	def recv(self, X, **params):
		self.logs.append("")
		self.logs[-1] += self.formatter.message("Receiving data.")
		self.received_ = X
		self.accelerate(**params)

		try:
			self.irreversible = params["irreversible"]
			self.logs[-1] += self.formatter.message("\"irreversible\" is specified as {}.".format(self.irreversible))
		except KeyError:
			self.logs[-1] += self.formatter.warning(
				"\"irreversible\" is not specified, now set to {}.".format(self.irreversible))

		try:
			self.QCD = params["QCD"]
			self.logs[-1] += self.formatter.message("\"QCD\" is specified as {}.".format(self.QCD))
		except KeyError:
			self.logs[-1] += self.formatter.warning("\"QCD\" is not specified, now set to {}.".format(self.QCD))

		try:
			self.D = params["D"]
			self.logs[-1] += self.formatter.message("\"D\" is specified as {}.".format(self.D))
		except KeyError:
			self.logs[-1] += self.formatter.warning("\"D\" is not specified, now set to {}.".format(self.D))

		try:
			self.reserve_bits = params["reserve_bits"]
			self.logs[-1] += self.formatter.message("\"reserve_bits\" is specified as {}.".format(self.reserve_bits))
		except KeyError:
			self.logs[-1] += self.formatter.warning("\"reserve_bits\" is not specified, now set to {}.".format(self.reserve_bits))		

		self.epsilon_b, self.mu_b = parse_marker(self.QCD)

		delta_bs = []
		for i in range(self.D):
			delta_bs.append(2 ** -(self.epsilon_b + i - self.D) * (1 + self.mu_b / (2 ** 11)))

		if self.mode == "quantify":
			if self.irreversible:
				if self.accelerated:
					self.logs[-1] += self.formatter.message("Using multiprocess pool to accelerate quantify.")
					inputs = [[x, delta_bs] for x in X]
					with Pool(min(self.task_number, self.max_pool_size)) as p:
						X = p.starmap(_quantize, inputs)
				else:
					X = [_quantize(x, delta_bs) for x in X]
			else:
				if self.accelerated:
					self.logs[-1] += self.formatter.message("Using multiprocess pool to accelerate quantify.")
					inputs = [[x, self.reserve_bits, False] for x in X]
					with Pool(min(self.task_number, self.max_pool_size)) as p:
						X = p.starmap(_scale, inputs)
				else:
					X = [_scale(x, self.reserve_bits, False) for x in X]

		elif self.mode == "dequantify":
			try:
				self.D = params["delta_vb"]
				self.logs[-1] += self.formatter.message("\"delta_vb\" is specified as {}.".format(self.delta_vb))
			except KeyError:
				self.logs[-1] += self.formatter.warning("\"delta_vb\" is not specified, now set to {}.".format(self.delta_vb))

			if self.irreversible:
				if self.accelerated:
					self.logs[-1] += self.formatter.message("Using multiprocess pool to accelerate dequantify.")
					inputs = [[x, delta_bs, self.delta_vb] for x in X]
					with Pool(min(self.task_number, self.max_pool_size)) as p:
						X = p.starmap(_dequantize, inputs)
				else:
					X = [_dequantize(x, delta_bs, self.delta_vb) for x in X]
			else:
				if self.accelerated:
					self.logs[-1] += self.formatter.message("Using multiprocess pool to accelerate dequantify.")
					inputs = [[x, self.reserve_bits, True] for x in X]
					with Pool(min(self.task_number, self.max_pool_size)) as p:
						X = p.starmap(_scale, inputs)
				else:
					X = [_scale(x, self.reserve_bits, True) for x in X]

		else:
			msg = "Invalid attribute %s for quantizer %s. Quantizer.mode should be set to \"quantify\" or \"dequantify\"." % (self.mode, self)
			self.logs[-1] += self.formatter.error(msg)
			raise AttributeError(msg)

		self.sended_ = X

		return self


def _quantize(tile, delta_bs):
	quantified_tile = [np.array(tile[0] * np.abs(tile[0]) / delta_bs[0], dtype=int)]
	for subbands, delta_b in zip(tile[1:], delta_bs):
		quantified_tile.append(tuple([np.array(np.sign(subband) * np.abs(subband) / delta_b, dtype=int) for subband in subbands]))

	return quantified_tile


def _dequantize(coeffs, delta_bs, delta_vb):
	dequantified_tile = [np.sign(coeffs[0]) * (coeffs[0] + delta_vb) * delta_bs[0]]
	for subbands, delta_b in zip(coeffs[1:], delta_bs):
		dequantified_tile.append(tuple([np.sign(subband) * (subband + delta_vb) * delta_b for subband in subbands]))

	return dequantified_tile


def _scale(tile, reserve_bits, compress):
	new_tile = []
	if compress:
		for subbands in tile:
			if isinstance(subbands, tuple):
				new_tile.append(tuple([np.array(subband / (10 ** reserve_bits), dtype=np.float64) for subband in subbands]))
			else:
				new_tile.append(np.array(subbands / (10 ** reserve_bits), dtype=np.float64))
	else:
		for subbands in tile:
			if isinstance(subbands, tuple):
				new_tile.append(tuple([np.array(subband * (10 ** reserve_bits), dtype=np.int64) for subband in subbands]))
			else:
				new_tile.append(np.array(subbands * (10 ** reserve_bits), dtype=np.int64))

	return new_tile
