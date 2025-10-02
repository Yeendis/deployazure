#!/bin/bash
# Script para criar Resource Group no Azure
RG_NAME="rg-deploy1"
LOCATION="eastus"

az group create \
  --name $RG_NAME \
  --location $LOCATION
