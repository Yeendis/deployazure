#!/bin/bash

RG_NAME="rg-vm02"
LOCATION="eastus"
VM_NAME="vm-srv01"
IMAGE="Win2022Datacenter"
SIZE="Standard_B2s"
ADMIN_USER="adminuser"
ADMIN_PASSWORD="${ADMIN_PASSWORD}" 

az group create --name $RG_NAME --location $LOCATION

az vm create \
  --resource-group $RG_NAME \
  --name $VM_NAME \
  --image $IMAGE \
  --size $SIZE \
  --admin-username $ADMIN_USER \
  --admin-password $ADMIN_PASSWORD \
  --authentication-type password

az vm open-port --port 3389 --resource-group $RG_NAME --name $VM_NAME
