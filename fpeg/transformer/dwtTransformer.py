from multiprocessing import Pool

from ..base import Transformer
from ..config import read_config
from ..utils.lut import dht2lut
import pywt
import numpy as np
config = read_config()

min_task_number = config.get("accelerate", "codec_min_task_number")
max_pool_size = config.get("accelerate", "codec_max_pool_size")
''' name="dwtTransformer",'''
class dwtTransformer(Transformer):
    def __init__(self,
              lossy=True,
              level=3,
              ifidwt=False,
              tiles=[],
                   ):
            """
            Init and set attributes of a canonical huffman codec.

            Explicit Attributes
            -------------------
            name: str, optional
              Name of the codec.
            mode: str, optional
              Mode of the codec, must in ["encode", "decode"].
            dhts: list of lists, optional
              DHTs that store huffman trees for encoding and decoding.
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

            '''self.name = name'''
            self.ifidwt = ifidwt
            self.tiles = tiles
            self.level = level
            self.lossy = lossy
            self.min_task_number = min_task_number
            self.max_pool_size = max_pool_size

    
    def dwt_idwt(self):
            """
            Run the dwt/idwt from the pywavelet library
            on every tile and save coefficient results in tile object
            """
            # loop through the tiles
            # Daubechies 9/7coefficients(lossy case)

            dec_lo97 = [0.6029490182363579, 0.2668641184428723, -0.07822326652898785, -0.01686411844287495,
                             0.02674875741080976]
            dec_hi97 = [1.115087052456994, -0.5912717631142470, -0.05754352622849957, 0.09127176311424948, 0]
            rec_lo97 = [1.115087052456994, 0.5912717631142470, -0.05754352622849957, -0.09127176311424948, 0]
            rec_hi97 = [0.6029490182363579, -0.2668641184428723, -0.07822326652898785, 0.01686411844287495,
                             0.02674875741080976]

            # Le Gall 5/3 coefficients (lossless case)
            dec_lo53 = [6/8, 2/8, -1/8]
            dec_hi53 = [1, -1/2, 0]
            rec_lo53 = [1, 1/2, 0]
            rec_hi53 = [6/8, -2/8, -1/8]




            if self.lossy:
                wavelet = pywt.Wavelet('DB97', [dec_lo97, dec_hi97, rec_lo97, rec_hi97])
            else:
                wavelet = pywt.Wavelet('LG53', [dec_lo53, dec_hi53, rec_lo53, rec_hi53])
            
            coff=[];

            if self.ifidwt == False:
                for i in range(np.array(self.tiles).shape[0]):
                    # library function returns a tuple: (cA, (cH, cV, cD)), respectively LL, LH, HH, HL coefficients
                    y_coeffs = pywt.wavedec2(self.tiles[i][:][:][0], wavelet, level= self.level)
                    
                    Cb_coeffs= pywt.wavedec2(self.tiles[i][:][:][1], wavelet, level=self.level)
                    
                    Cr_coeffs= pywt.wavedec2(self.tiles[i][:][:][2], wavelet, level=self.level)
                    
                    coff.append([y_coeffs,Cb_coeffs,Cr_coeffs]);
            else:
                for i in range(np.array(self.tiles).shape[0]):
                    
                    y_coeffs = pywt.waverec2(self.tiles[i][0][:], wavelet)
                    
                    Cb_coeffs= pywt.waverec2(self.tiles[i][1][:], wavelet)
                    
                    Cr_coeffs= pywt.waverec2(self.tiles[i][2][:], wavelet)
                    
                    coff_temp = np.array([y_coeffs,Cb_coeffs,Cr_coeffs])
                    coff_temp.transpose((2,1,0))
                    coff.append(coff_temp.tolist())

            return coff


