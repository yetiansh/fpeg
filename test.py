import numpy as np
# from fpeg.config import Config
from fpeg.utils import Spliter


spliter = Spliter()
X = np.random.rand(128, 128, 3)
spliter.recv_send(X)
print(spliter.logs, len(spliter.recieved_), len(spliter.sended_))
