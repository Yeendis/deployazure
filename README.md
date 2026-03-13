# deployazure
Deploy de Recursos no Azure usando Actions
1: Faça o deploy de um application service no azure com comando a baixo
( az ad sp create-for-rbac --name "github-actions-sp" --role contributor \
    --scopes /subscriptions/<ID_DA_SUA_SUBSCRIPTION> \
    --sdk-auth"
pegue a saida do arquivo json e vá para passo 2
2: Crie uma secrete key indo em setting/secrets and variables/actions
e cria uma nova entrada. coloque um nome para secrete key e cole o json 
3: vá em deployazure/script escolha o script para deploy e altereo conforme seu ambiente. 
4: ir no actions e selecionar o .yml que desejar, e então clicar em run workflow

--------------------------------------------------------------------------------------------
Reflexão Técnica
Decisões técnicas

Foi escolhido GitHub Actions pela integração nativa com o GitHub e facilidade de automação de pipelines CI/CD.

A separação entre CI e Deploy foi feita para garantir que o deploy só aconteça após validação.

-Impacto da ausência de testes automatizados

Sem testes automatizados erros poderiam ser enviados para produção causando falhas de infraestrutura e indisponibilidade de serviços.

-Evolução para Continuous Delivery

O pipeline pode evoluir para:

Deploy automático após aprovação
Deploy em ambientes DEV/QA/PROD
Infraestrutura como código completa
Terraform integration

-Riscos mitigados pela CI

Erros humanos em deploy manual
Scripts quebrados
Falhas de sintaxe
Problemas de integração
Deploy sem validação
