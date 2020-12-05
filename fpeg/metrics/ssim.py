__all__ = [
	"ssim",
	"mssim",
	"SSIMTester",
	"MSSIMTester"
]

import numpy as np
import cv2
from scipy.ndimage import uniform_filter, gaussian_filter
from skimage.util.dtype import dtype_range
from skimage.util import crop
from fpeg.tester import Tester


def ssim(X,
         Y=None,
         dynamic_range=None):
	if Y is not None:
		return [_ssim(x, y, 
		              dynamic_range=dynamic_range) for x, y in zip(X, Y)]
	else:
		return None


def _ssim(X, Y, dynamic_range=None):
	K = 0.01

	if dynamic_range is None:
		# 根据图像数据类型确定动态范围
		# 如果是 uint8 型则为 0 到 255
		# 如果是 float 型则为 -1 到 1
		dmin, dmax = dtype_range[X.dtype.type]
		dynamic_range = dmax - dmin


	ux = np.mean(X)
	uy = np.mean(Y)
	sigmax = (sum(sum((X-ux)**2))/(len(X)*len(X[0])-1))**0.5
	sigmay = (sum(sum((Y-uy)**2))/(len(Y)*len(Y[0])-1))**0.5
	sigmaxy = sum(sum((X-ux)*(Y-uy))) / (len(X)*len(X[0])-1)
	C = (K*dynamic_range)**2

	ssim = (2*ux*uy+C)*(2*sigmaxy+C)/(ux**2+uy**2+C)/(sigmax**2+sigmay**2+C)

	return ssim


def mssim(X, Y=None,
				  win_size=None,
				  dynamic_range=None,
				  gaussian_weights=False,
				  full=False):
	if Y is not None:
		return [_mssim(x, y,
		               win_size=win_size,
		               dynamic_range=dynamic_range,
		               gaussian_weights=gaussian_weights,
		               full=full) for x, y in zip(X, y)]
	else:
		return None

def _mssim(X, Y,
           win_size=None,
           dynamic_range=None,
           gaussian_weights=False,
           full=False):
	# 下面三个参数都是原始论文中给定的
	K1 = 0.01
	K2 = 0.03
	sigma = 1.5

	# 计算方差和协方差时，采用无偏估计（除以 N-1）
	# 数学上虽然好看，但其实影响不大
	use_sample_covariance = True

	if win_size is None:
		# 两种计算均值的方式，第一种是计算高斯加权后的均值和方差、协方差
		# 第二种是直接计算这三个统计量
		# 两种方式对应的滑窗尺寸不同
		if gaussian_weights:
			win_size = 11  # 11 to match Wang et. al. 2004
		else:
			win_size = 7   # backwards compatibility

	if not (win_size % 2 == 1):
		# 滑窗边长必须是奇数，保证有中心像素
		raise ValueError('Window size must be odd.')

	if dynamic_range is None:
		# 根据图像数据类型确定动态范围
		# 如果是 uint8 型则为 0 到 255
		# 如果是 float 型则为 -1 到 1
		dmin, dmax = dtype_range[X.dtype.type]
		dynamic_range = dmax - dmin

	# 灰度图像为 2，彩色图像为3，
	# 但计算彩色图像的 MSSIM 时，其实是把它分解为各个通道的灰度图像分别计算，然后再求平均
	ndim = X.ndim

	# 确定到底采用哪种类型的滑窗
	if gaussian_weights:
		# sigma = 1.5 to approximately match filter in Wang et. al. 2004
		# this ends up giving a 13-tap rather than 11-tap Gaussian
		filter_func = gaussian_filter
		filter_args = {'sigma': sigma}

	else:
		filter_func = uniform_filter
		filter_args = {'size': win_size}

	# ndimage filters need floating point data
	# 把 uint8 型数据转为 float 型
	X = X.astype(np.float64)
	Y = Y.astype(np.float64)
	
	# 滑窗所覆盖的像素点的个数
	NP = win_size ** ndim

	# filter has already normalized by NP
	if use_sample_covariance:
		# filter 函数求的是在 NP 个点上的平均
		# 现在想要无偏估计，则需要乘以 NP 再重新除以 NP-1
		cov_norm = NP / (NP - 1)  # sample covariance
	else:
		cov_norm = 1.0  # population covariance to match Wang et. al. 2004

	# compute (weighted) means
	# 计算两幅图的平均图，ux，uy 的每个像素代表以它为中心的滑窗下所有像素的均值(加权) E(X), E(Y)
	ux = filter_func(X, **filter_args)
	uy = filter_func(Y, **filter_args)

	# compute (weighted) variances and covariances
	# 计算 E(X^2), E(Y^2)
	uxx = filter_func(X * X, **filter_args)
	uyy = filter_func(Y * Y, **filter_args)
	# 计算 E(XY)
	uxy = filter_func(X * Y, **filter_args)
	# sigma_x^2 = E(x^2)-E(x)^2，下文会给出推导
	vx = cov_norm * (uxx - ux * ux)
	# sigma_y^2 = E(y^2)-E(y)^2
	vy = cov_norm * (uyy - uy * uy)
	# cov(x,y) = E(xy)-E(x)E(y)，下文会给出推导
	vxy = cov_norm * (uxy - ux * uy)

	R = dynamic_range
	# paper 中的公式
	C1 = (K1 * R) ** 2
	C2 = (K2 * R) ** 2
	
	# paper 中的公式
	A1, A2, B1, B2 = ((2 * ux * uy + C1,
					   2 * vxy + C2,
					   ux ** 2 + uy ** 2 + C1,
					   vx + vy + C2))
	D = B1 * B2
	S = (A1 * A2) / D

	# to avoid edge effects will ignore filter radius strip around edges
	# 截去边缘部分，因为卷积得到的边缘部分的均值并不准确，是靠扩充边缘像素的方式得到的。
	pad = (win_size - 1) // 2

	# compute (weighted) mean of ssim
	# 计算 SSIM 的均值
	mssim = crop(S, pad).mean()

	if full:
		return mssim, S
	else:
		return mssim


class SSIMTester(Tester):
	def __init__(self,
	             Y=None,
	             dynamic_range=None):
		super().__init__(ssim,
		                 Y=Y,
		                 dynamic_range=dynamic_range)


class MSSIMTester(Tester):
	def __init__(self,
	             Y=None,
	             win_size=None,
	             dynamic_range=None,
	             gaussian_weights=False,
	             full=False):
		super().__init__(mssim,
		                 Y=Y,
		                 win_size=win_size,
		                 dynamic_range=dynamic_range,
		                 gaussian_weights=gaussian_weights,
		                 full=full)
