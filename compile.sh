#!/bin/bash

cd `dirname ${BASH_SOURCE[0]}`

pushd lrzip

echo "Compiling lrzip compression shared lib..."
python build_lrzip_compress.py
echo "Compiling lrzip decompression shared lib..."
python build_lrzip_decompress.py

popd
