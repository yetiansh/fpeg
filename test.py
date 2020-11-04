import numpy as np
# from fpeg.config import Config
from fpeg.utils import Spliter


spliter = Spliter()
X = np.random.rand(150, 140, 3)
spliter.recv_send([X[:, :, 0], X[:, :, 1], X[:, :, 2]])
print(spliter.logs, len(spliter.recieved_), len(spliter.sended_))
