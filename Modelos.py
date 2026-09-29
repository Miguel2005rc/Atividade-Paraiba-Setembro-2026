from typing import List, Optional
from pydantic import BaseModel, Field
class Fornecedor(BaseModel):
    razao_social: Optional[str] = None
    fantasia: Optional[str] = None
    cnpj: Optional[str] = None
class Faturado(BaseModel):
    nome_completo: Optional[str] = None
    cpf: Optional[str] = None
class Parcela(BaseModel):
    numero: int = 1

    data_vencimento: Optional[str] = None
    valor: Optional[float] = None
class NotaFiscal(BaseModel):
    fornecedor: Fornecedor
    faturado: Faturado
    numero_nota_fiscal: Optional[str] = None
    data_emissao: Optional[str] = None
    descricao_produtos: List[str] = Field(
        default_factory=list
    )
    quantidade_parcelas: int = 1
    parcelas: List[Parcela] = Field(
        default_factory=list
    )
    valor_total: Optional[float] = None
    tipo_despesa: List[str] = Field(
        default_factory=list
    )