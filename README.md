# FPEG

Fudan Photographic Expert Group (FPEG) is a method of lossy compression for digital images developed by Fudan undergraduate students.

This repository is a a python implementation of FPEG and JPEG2000.



## Code Organization

```bash
FPEG
|   LICENSE
|   README.md
|   source.py
|   test.py
|
\---fpeg
    |   app.py
    |   base.py
    |   config.dat
    |   config.py
    |   fpeg.py
    |   jpeg.py
    |   pipeline.py
    |   __init__.py
    |
    +---codec
    |       huffman_codec.py
    |       shannon_codec.py
    |       __init__.py
    |
    +---metrics
    |       __init__.py
    |
    +---test
    |       __init__.py
    |
    +---transformer
    |       __init__.py
    |
    \---utils
            format.py
            io.py
            lut.py
            monitor.py
            preprocess.py
            __init__.py
```



## To Contribute

Codecs, transformers, processors are all pipes in FPEG. 

A certain codec, like huffman codec, is a subclass of Pipe (and Codec). To implement a codec is to implement the \_\_init\_\_, encode and decode methods. Put what the codec need and what the monitor should know in \_\_init\_\_'s signature, such as Define Huffman Table (DHT) for encoding and decoding. After that, you can set what should not be known by monitor, such as its log and formatter.

In encode and decode methods, the codec should first clear its history information, i.e. the DHTs used in processing former data, using self._clear_record method. Moreover, encode and decode methods should support parallel computing using python’s implementation subprocess pool. **Refer to the code of HuffmanCodec for more information and follow a unified code specification** (make other codec similar to HuffmanCodec).



## TODO

- [ ] Codecs
	- [ ] Huffman encoding
	- [ ] Shannon encoding
	- [ ] Arithmetic encoding

- [ ] Transformers
	- [ ] DWT and IDWT transformer
	- [ ] DCT and IDCT transformer
- [ ] Utils
	- [ ] Preprocess
		- [x] Spliter
		- [ ] DC Shifter (?)
		- [ ] Color transformer (?)
		- [ ] …
	- [ ] Postprocess
		- [ ] …
	- [ ] IO
		- [x] Reader
		- [ ] Writer
	- [x] Formatter
	- [x] pprint
- [ ] Metrics
	- [ ] Entropy
	- [ ] SNR (?)
	- [ ] PSNR (?)
	- [ ] …
- [x] Monitor
- [x] Pipeline