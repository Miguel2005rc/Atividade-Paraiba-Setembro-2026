PROJETO 
1. OBJETIVO
Sistema web desenvolvido em Python com FastAPI
para processamento de notas fiscais em PDF
utilizando agentes de inteligência artificial.

O sistema recebe uma nota fiscal em PDF e utiliza
agentes de IA para interpretar os dados.

O sistema identifica:

- Fornecedor
- Razão Social
- Nome Fantasia
- CNPJ
- Faturado
- Nome Completo
- CPF
- Número da Nota Fiscal
- Data de Emissão
- Produtos
- Quantidade de Parcelas
- Data de Vencimento
- Valor das Parcelas
- Valor Total
- Classificação da Despesa

2. AGENTES
AGENTE 1
Nome:
ExtractorAgent
Responsabilidade:
Interpretar o PDF da nota fiscal e extrair
as informações estruturadas.

AGENTE 2
Nome:
ClassifierAgent
Responsabilidade:
Interpretar os produtos e classificar
o tipo de despesa.

3. FLUXO
Usuário
↓
Login
↓
Upload do PDF
↓
Agente 1
↓
Extração das informações
↓
Agente 2
↓
Classificação da despesa
↓
JSON final
↓
Tela Web

4. ESTRUTURA

main.py
extrator.py
classificar.py
modelos.py
index.html
login.html
requirements.txt
README.txt
.env

6. HOSPEDAGEM
O projeto possui Procfile preparado para
serviços de hospedagem como Render.

7. CATEGORIAS DE DESPESA

INSUMOS AGRÍCOLAS
MANUTENÇÃO E OPERAÇÃO
RECURSOS HUMANOS
SERVIÇOS OPERACIONAIS
INFRAESTRUTURA E UTILIDADES
ADMINISTRATIVAS
SEGUROS E PROTEÇÃO
IMPOSTOS E TAXAS
INVESTIMENTOS

8. EXEMPLOS
Óleo Diesel
→ MANUTENÇÃO E OPERAÇÃO

Material Hidráulico
→ INFRAESTRUTURA E UTILIDADES

Sementes
→ INSUMOS AGRÍCOLAS

Fertilizantes
→ INSUMOS AGRÍCOLAS

Frete
→ SERVIÇOS OPERACIONAIS

Seguro Agrícola
→ SEGUROS E PROTEÇÃO

9. LIMITE DO PDF
O sistema permite PDF de até 50 MB.

10. PROCESSAMENTO EM TEMPO REAL
A interface consulta o servidor enquanto
o processamento está acontecendo.
Mensagens apresentadas:
Enviando PDF
Agente 1 processando
Agente 2 classificando
Processamento concluído