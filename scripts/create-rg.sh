#!/bin/bash
# Script para criar Resource Group no Azure
RG_NAME="MeuResourceGroupTest"
LOCATION="eastus"

az group create \
  --name $RG_NAME \
  --location $LOCATION
