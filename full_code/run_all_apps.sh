#!/bin/bash

ls -1 *.py|while read pyscript
do
    echo "running $pyscript"
    nohup streamlit run $pyscript > $pyscript.log 2>&1 &
    cat $pyscript.log
done