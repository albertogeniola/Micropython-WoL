#!/bin/bash

MPY_CROSS_PATH="/Users/geniola/Desktop/micropython/mpy-cross/build/mpy-cross"

SRC_PATH="./src"
DST_PATH="../build"
if [[ -d $DST_PATH ]];
then
    rm -R $DST_PATH
fi

mkdir $DST_PATH
pushd $SRC_PATH

FILES=$(ls *.py)
for f in $FILES
do
    if [[ $f == boot.py ]]
    then
        continue
    fi

    if [[ $f == main.py ]]
    then
        continue
    fi

    echo "Compiling $f"
    target_f=${f%.py}.mpy
    $MPY_CROSS_PATH "$f" -o "$DST_PATH/$target_f"
done
popd