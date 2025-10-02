#!/bin/bash

RG_NAME="rg-vm01"
LOCATION="eastus"
VM_NAME="vm-oo1"
IMAGE="Ubuntu2204"     
SIZE="Standard_B1s"  
ADMIN_USER="sidney.lima"

az group create --name $RG_NAME --location $LOCATION

az vm create \
  --resource-group $RG_NAME \
  --name $VM_NAME \
  --image $IMAGE \
  --size $SIZE \
  --admin-username $ADMIN_USER \
  --generate-ssh-keys \
  --authentication-type ssh

az vm open-port --port 22 --resource-group $RG_NAME --name $VM_NAME

