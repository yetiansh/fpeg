def dwt(tiles,lossy=True):
        """
        Run the 2-DWT (using Haar family) from the pywavelet library
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




        if lossy:
            wavelet = pywt.Wavelet('DB97', [dec_lo97, dec_hi97, ec_lo97, rec_hi97])
        else:
            wavelet = pywt.Wavelet('LG53', [dec_lo53, dec_hi53, rec_lo53, rec_hi53])

        for tile in tiles:
            # library function returns a tuple: (cA, (cH, cV, cD)), respectively LL, LH, HH, HL coefficients
            [cA3, (cH3, cV3, cD3), (cH2, cV2, cD2), (cH1, cV1, cD1)] = pywt.wavedec2(tile.y_tile, wavelet, level=3)
            tile.y_coeffs = [cA3, (cH3, cV3, cD3), (cH2, cV2, cD2), (cH1, cV1, cD1)]
            [cA3, (cH3, cV3, cD3), (cH2, cV2, cD2), (cH1, cV1, cD1)] = pywt.wavedec2(tile.Cb_tile, wavelet, level=3)
            tile.Cb_coeffs = [cA3, (cH3, cV3, cD3), (cH2, cV2, cD2), (cH1, cV1, cD1)]
            [cA3, (cH3, cV3, cD3), (cH2, cV2, cD2), (cH1, cV1, cD1)] = pywt.wavedec2(tile.Cr_tile, wavelet, level=3)
            tile.Cr_coeffs = [cA3, (cH3, cV3, cD3), (cH2, cV2, cD2), (cH1, cV1, cD1)]

        return tiles