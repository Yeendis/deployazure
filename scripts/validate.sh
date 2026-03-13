#!/bin/bash

echo "Validando sintaxe do script..."

bash -n deployazure/scripts/create-vm-windowsrv.sh

if [ $? -ne 0 ]; then
    echo "Erro de sintaxe"
    exit 1
fi

echo "Validação OK"
