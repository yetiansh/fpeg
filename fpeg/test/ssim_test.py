import cv2
from fpeg.metrics import ssim, mssim

if __name__ == "__main__":
  origin = cv2.imread('penguim.jpg')
  compressed = cv2.imread('out.jpg')
  X = [origin[:, :, 0], origin[:, :, 2], origin[:, :, 2]]
  Y = [compressed[:, :, 0], compressed[:, :, 2], compressed[:, :, 2]]
  print(mssim(X, Y))
  print(ssim(X, Y))

