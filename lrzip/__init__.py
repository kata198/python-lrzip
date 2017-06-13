#!/usr/bin/env python
'''
    Copyright (c) 2017 Timothy Savannah, All Rights Reserved

    Code is licensed under terms of LGPL v3

    Requires lrzip to be installed.
'''

import _lrzip
 

__version__ = '1.0.0'
__version_tuple__ = (1, 0, 0)

__all__ = ('compress', 'decompress', 'LRZIP_MODE_COMPRESS_NONE', 'LRZIP_MODE_COMPRESS_ZPAQ', 'LRZIP_MODE_COMPRESS_BZIP2', 'LRZIP_MODE_COMPRESS_ZLIB', 'LRZIP_MODE_COMPRESS_LZO', 'LRZIP_MODE_COMPRESS_LZMA', 'LRZIP_MODE_COMPRESS_BZ2')

def decompress(data):
    '''
        decompress - Decompress some lrzip-compressed data

        @param data <bytes> - lrzip compressed data (any compression format)

        @return bytes - Decompressed data
    '''
    if not issubclass(data.__class__, bytes):
        raise ValueError('Data must be bytes for decompressing')

    ffi = _lrzip.ffi

    buff = ffi.from_buffer(data)

    decompressedDataSizePtr = ffi.new('size_t*', 1)

    decompressedData = _lrzip.lib.doDecompress(buff , len(data), decompressedDataSizePtr)

    decompressedDataSize = ffi.unpack(decompressedDataSizePtr, 1)[0]

    ret = ffi.unpack(decompressedData, decompressedDataSize)

    # Manually free because we didn't create through cffi
    _lrzip.lib._do_free(decompressedData)

    return ret


# NOTE: These compress modes are pulled from the enum in Lrzip.h

# LRZIP_MODE_COMPRESS_NONE - No additional compression (only rzip)
LRZIP_MODE_COMPRESS_NONE = 4
# LRZIP_MODE_COMPRESS_LZO - LZO compression
LRZIP_MODE_COMPRESS_LZO = 5
# LRZIP_MODE_COMPRESS_ZLIB - zlib/gz compression
LRZIP_MODE_COMPRESS_ZLIB = 6
# LRZIP_MODE_COMPRESS_BZIP2 - bzip2/bz2 compression
LRZIP_MODE_COMPRESS_BZIP2 = 7
# LRZIP_MODE_COMPRESS_LZMA - lzma/xz compression (default)
LRZIP_MODE_COMPRESS_LZMA = 8
# LRZIP_MODE_COMPRESS_ZPAQ - zpaq compression (default)
LRZIP_MODE_COMPRESS_ZPAQ = 9

# _ALL_COMPRESS_MODES - All valid modes
_ALL_COMPRESS_MODES = (LRZIP_MODE_COMPRESS_NONE, LRZIP_MODE_COMPRESS_LZO, LRZIP_MODE_COMPRESS_ZLIB, LRZIP_MODE_COMPRESS_BZIP2, LRZIP_MODE_COMPRESS_LZMA, LRZIP_MODE_COMPRESS_ZPAQ)

def compress(data, compressMode='lzma'):
    '''
        compress - Compress some data with lrzip

        @param data <bytes> - data to compress

        @param compressMode <int/str> - Mode to compress.
            
            'lzma' / LRZIP_MODE_COMPRESS_LZMA - lzma compression (default)

            'none' / LRZIP_MODE_COMPRESS_NONE - No compression, only rzip step
            'gz' / LRZIP_MODE_COMPRESS_ZLIB   - zlib compression, only rzip step
            'bzip2' / LRZIP_MODE_COMPRESS_BZ2 - bzip2 compression, only rzip step
            'zpaq' / LRZIP_MODE_COMPRESS_ZPAQ - zpaq compression, only rzip step

        @return bytes - Decompressed data
    '''
    if not issubclass(data.__class__, bytes):
        raise ValueError('Data must be bytes for compressing')

    if compressMode in _ALL_COMPRESS_MODES:
        lrzipMode = compressMode
    else:
        if compressMode in ('lzma', 'xz'):
            lrzipMode = LRZIP_MODE_COMPRESS_LZMA
        elif compressMode == 'lzo':
            lrzipMode = LRZIP_MODE_COMPRESS_LZO
        elif compressMode in ('gz', 'zlib'):
            lrzipMode = LRZIP_MODE_COMPRESS_ZLIB
        elif compressMode in ('bz2', 'bzip2'):
            lrzipMode = LRZIP_MODE_COMPRESS_BZIP2
        elif compressMode == 'zpaq':
            lrzipMode = LRZIP_MODE_COMPRESS_ZPAQ
        elif compressMode in ('none', None, 'rzip'):
            lrzipMode = LRZIP_MODE_COMPRESS_NONE
        else:
            raise ValueError('Unknown compress mode: %s. See LRZIP_MODE_* variables for options.' %(repr(compressMode), ))

    ffi = _lrzip.ffi

    buff = ffi.from_buffer(data)

    compressedDataSizePtr = ffi.new('size_t*', 1)

    compressedData = _lrzip.lib.doCompress(buff , len(data), lrzipMode, compressedDataSizePtr)

    compressedDataSize = ffi.unpack(compressedDataSizePtr, 1)[0]

    ret = ffi.unpack(compressedData, compressedDataSize)

    # Manually free because we didn't create through cffi
    _lrzip.lib._do_free(compressedData)

    return ret
