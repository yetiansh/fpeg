import numpy as np
from fpeg.utils import Quantizer
from fpeg.pipeline import Pipeline
from fpeg.funcs import cat_arrays_2d

if __name__ == "__main__":
	D = 2
	pipeline = Pipeline([("quantizer0", Quantizer()),
	                     ("quantizer1", Quantizer())],
	                    params={
		                    "quantizer0": {"mode": "quantify", "irreversible": True, "accelerated": False, "D": D},
		                    "quantizer1": {"mode": "dequantify", "irreversible": True, "accelerated": False, "D": D}
	                    })
	x = np.array([[1, -1, 2], [2, -1, -1], [3, -1, -2]])
	X = [[x, (x, x, x)]]
	pipeline.recv(X)
	in0 = pipeline.monitor.data[-1]["quantizer0"][0][0]
	out1 = pipeline.monitor.data[-1]["quantizer1"][1][0]
	print(2)
