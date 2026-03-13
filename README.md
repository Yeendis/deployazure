deployazure
Projeto de automação de deploy de recursos no Azure utilizando GitHub Actions para integração contínua e entrega automatizada.
Visão geral
Este repositório foi criado com o objetivo de demonstrar uma pipeline CI/CD para provisionamento de recursos no Microsoft Azure a partir do GitHub.
Atualmente, o projeto está estruturado para:
validar scripts antes do deploy
executar testes automatizados
autenticar no Azure via GitHub Actions
criar uma VM Windows Server com Azure CLI
---
Objetivo
Automatizar o processo de deploy de infraestrutura no Azure com mais segurança, padronização e rastreabilidade, reduzindo erros manuais e garantindo validações antes da execução em ambiente real.
---
Tecnologias utilizadas
GitHub Actions
Azure CLI
Bash
Python 3.11
Pytest
---
Estrutura do projeto
```text
.github/
└── workflows/
    └── deployvmwindows.yml

scripts/
├── create-vm-windowsrv.sh
└── validate.sh

tests/
├── test_create_vm_windowsrv.py
└── test_dummy.py

README.md
```
> Observação: após a criação do teste funcional real, o arquivo `test_dummy.py` pode ser removido, pois deixa de ser necessário.
---
Fluxo da pipeline
A pipeline está dividida em duas etapas principais:
1. CI
Responsável por validar o repositório antes do deploy:
checkout do código
configuração do Python
instalação das dependências
validação dos scripts
execução dos testes automatizados
2. Deploy
Executada somente após a etapa de CI ser concluída com sucesso:
checkout do código
autenticação no Azure
validação do login
permissão de execução do script
criação da VM Windows no Azure
---
Pré-requisitos
Antes de usar este projeto, você precisa ter:
uma conta no Microsoft Azure
uma subscription ativa no Azure
um repositório no GitHub
permissão para criar um Service Principal
permissão para cadastrar Secrets no GitHub
---
Configuração da autenticação no Azure
1. Criar um Service Principal
No terminal com Azure CLI autenticado, execute:
```bash
az ad sp create-for-rbac --name "github-actions-sp" \
  --role contributor \
  --scopes /subscriptions/<ID_DA_SUA_SUBSCRIPTION> \
  --sdk-auth
```
Esse comando irá retornar um JSON com as credenciais que serão usadas no GitHub Actions.
---
2. Criar o secret `AZURE_CREDENTIALS` no GitHub
No repositório do GitHub, acesse:
Settings > Secrets and variables > Actions
Clique em New repository secret e crie um secret com o nome:
```text
AZURE_CREDENTIALS
```
Cole nele o conteúdo JSON retornado pelo comando anterior.
---
3. Criar o secret `ADMIN_PASSWORD`
Ainda em:
Settings > Secrets and variables > Actions
Crie outro secret com o nome:
```text
ADMIN_PASSWORD
```
Defina uma senha forte para o usuário administrador da VM Windows.
Exemplo de senha com boa complexidade:
```text
SenhaForte@123
```
> Use uma senha que atenda às políticas do Azure para VMs Windows.
---
Configuração do script de deploy
O script principal de criação da VM está em:
```text
scripts/create-vm-windowsrv.sh
```
Você pode alterar os parâmetros de acordo com o seu ambiente:
```bash
RG_NAME="rg-vm02"
LOCATION="eastus"
VM_NAME="vm-srv01"
IMAGE="Win2022Datacenter"
SIZE="Standard_B2s"
ADMIN_USER="adminuser"
```
Parâmetros configuráveis
`RG_NAME`: nome do Resource Group
`LOCATION`: região do Azure
`VM_NAME`: nome da máquina virtual
`IMAGE`: imagem da VM
`SIZE`: tamanho da VM
`ADMIN_USER`: usuário administrador
`ADMIN_PASSWORD`: senha recebida via secret
---
Exemplo do script de criação da VM
```bash
#!/bin/bash
set -euo pipefail

RG_NAME="rg-vm02"
LOCATION="eastus"
VM_NAME="vm-srv01"
IMAGE="Win2022Datacenter"
SIZE="Standard_B2s"
ADMIN_USER="adminuser"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-}"

if [ -z "$ADMIN_PASSWORD" ]; then
  echo "Erro: variável ADMIN_PASSWORD não definida."
  exit 1
fi

az group create --name "$RG_NAME" --location "$LOCATION"

az vm create \
  --resource-group "$RG_NAME" \
  --name "$VM_NAME" \
  --image "$IMAGE" \
  --size "$SIZE" \
  --admin-username "$ADMIN_USER" \
  --admin-password "$ADMIN_PASSWORD" \
  --authentication-type password

az vm open-port --port 3389 --resource-group "$RG_NAME" --name "$VM_NAME"
```
---
Workflow de deploy
O workflow está localizado em:
```text
.github/workflows/deployvmwindows.yml
```
Exemplo de estrutura do pipeline:
```yaml
name: CI CD Pipeline Azure

on:
  push:
    branches: [ main ]

  pull_request:
    branches: [ main ]

  workflow_dispatch:

jobs:
  CI:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout código
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Instalar dependências
        run: |
          python -m pip install pytest

      - name: Validar scripts
        run: |
          chmod +x scripts/validate.sh
          ./scripts/validate.sh

      - name: Executar testes
        run: |
          pytest -v

  Deploy:
    needs: CI
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - name: Checkout código
        uses: actions/checkout@v4

      - name: Login Azure
        uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Verificar login
        run: az account show

      - name: Permissão script
        run: chmod +x scripts/create-vm-windowsrv.sh

      - name: Criar VM Windows
        env:
          ADMIN_PASSWORD: ${{ secrets.ADMIN_PASSWORD }}
        run: |
          ./scripts/create-vm-windowsrv.sh
```
---
Validação de scripts
O arquivo `scripts/validate.sh` pode ser usado para verificar a sintaxe do script Bash antes de executar o deploy.
Exemplo:
```bash
#!/bin/bash
set -euo pipefail

bash -n scripts/create-vm-windowsrv.sh
echo "Validação concluída com sucesso."
```
---
Testes automatizados
O projeto pode conter testes funcionais para validar o comportamento do script sem criar recursos reais no Azure durante a etapa de CI.
Exemplo de cobertura esperada:
falha quando `ADMIN_PASSWORD` não está definida
execução dos comandos `az` na ordem correta
validação dos parâmetros usados na criação da VM
Executar testes localmente
```bash
pytest -v
```
---
Como executar o pipeline manualmente
Acesse a aba Actions no seu repositório GitHub
Selecione o workflow desejado
Clique em Run workflow
---
Como funciona o deploy
Quando o workflow é executado:
o código é baixado no runner do GitHub
os scripts são validados
os testes são executados
o GitHub Actions autentica no Azure usando `AZURE_CREDENTIALS`
o script `create-vm-windowsrv.sh` é executado
a VM Windows é criada no Azure
a porta 3389 é liberada para acesso RDP
---
Boas práticas adotadas
separação entre CI e Deploy
uso de Secrets para dados sensíveis
validação prévia antes do deploy
testes automatizados
uso de `set -euo pipefail` nos scripts Bash
parametrização básica do ambiente
---
Reflexão técnica
Decisões técnicas
Foi escolhido o GitHub Actions pela integração nativa com o GitHub e pela facilidade de configuração de pipelines CI/CD.
A separação entre as etapas de CI e Deploy foi definida para garantir que o provisionamento no Azure só aconteça após a validação do código, da sintaxe dos scripts e da execução dos testes.
O uso de Azure CLI foi adotado por ser simples, direto e adequado para automação inicial de infraestrutura em scripts Bash.
---
Impacto da ausência de testes automatizados
Sem testes automatizados, alterações incorretas poderiam seguir para o deploy e causar problemas como:
falhas na criação de recursos
uso incorreto de parâmetros
scripts quebrados em produção
indisponibilidade de serviços
perda de tempo na identificação de erros manuais
---
Evolução para Continuous Delivery
Este pipeline pode evoluir para um modelo mais completo de entrega contínua, incluindo:
deploy automático após aprovação
ambientes separados para DEV, QA e PROD
uso de Terraform para infraestrutura como código
aprovação manual antes de produção
rollback automatizado
análise de segurança e compliance no pipeline
---
Riscos mitigados pela CI
A etapa de CI ajuda a reduzir riscos como:
erros humanos em deploy manual
falhas de sintaxe em scripts
mudanças sem validação
problemas de integração
execução de deploy com código inconsistente
---
Melhorias futuras
Algumas evoluções possíveis para o projeto:
substituir scripts Bash por Terraform
criar múltiplos workflows por ambiente
adicionar aprovação manual no deploy de produção
publicar logs e artefatos da pipeline
adicionar testes mais completos de integração
restringir regras de firewall e acesso RDP
usar variáveis de ambiente mais flexíveis
incluir monitoramento e tagging de recursos
---
Troubleshooting
Erro: `Please run 'az login' to setup account`
Verifique se o secret `AZURE_CREDENTIALS` foi criado corretamente e contém o JSON completo gerado pelo Azure CLI.
Erro: `argument --admin-password: expected one argument`
Verifique se o secret `ADMIN_PASSWORD` foi cadastrado no GitHub e se o script está recebendo a variável corretamente.
Erro de permissão ao executar script
Garanta que o workflow execute:
```bash
chmod +x scripts/create-vm-windowsrv.sh
```
Erro de sintaxe no script
Execute a validação localmente com:
```bash
bash -n scripts/create-vm-windowsrv.sh
```
---
Segurança
Este projeto utiliza secrets do GitHub para armazenar credenciais sensíveis.
Nunca salve diretamente no código:
senhas
credenciais do Azure
chaves de acesso
arquivos JSON sensíveis
Sempre utilize:
`Settings > Secrets and variables > Actions`
---
Conclusão
Este projeto demonstra uma implementação inicial de CI/CD para Azure com GitHub Actions, aplicando boas práticas de automação, validação e segurança.
A proposta é servir como base para evolução futura em direção a uma esteira mais robusta de entrega contínua e infraestrutura como código.
---
Autor
Projeto desenvolvido para estudo e prática de automação de deploy no Azure com GitHub Actions.
