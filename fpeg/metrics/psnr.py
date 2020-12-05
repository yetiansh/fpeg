__all__ = [
	"psnr",
	"PSNRTester"
]

import numpy as np
from fpeg.tester import Tester


def psnr(X, Y=None, normalize=True):
	# 这里输入的是（0,255）的灰度或彩色图像，如果是彩色图像，则numpy.mean相当于对三个通道计算的结果再求均值
	if Y is not None:
		if normalize:
			mses = [np.mean((x / 255. - y / 255.) ** 2) for x, y in zip(X, Y)]
			PIXEL_MAX = 1.0
			return [20 * np.log10(PIXEL_MAX / np.sqrt(mse)) for mse in mses]  # 将对数中pixel_max的平方放了下来
		else:
			return [np.mean((x-y)**2) for x, y in zip(X, Y)]
	else:
		return None


class PSNRTester(Tester):
	def __init__(self,
	             Y=None,
	             normalize=True):
		super().__init__(psnr,
		                 Y=Y,
		                 normalize=normalize)
