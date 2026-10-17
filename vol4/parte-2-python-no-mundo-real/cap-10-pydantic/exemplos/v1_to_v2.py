"""O que mudou do Pydantic v1 para o v2 (e o que o código antigo ainda faz)."""
import warnings

from pydantic import BaseModel, ConfigDict, field_validator


class User(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str

    @field_validator("name")
    @classmethod
    def upper(cls, value):
        return value.upper()


user = User.model_validate({"name": "  ana  "})
print("v2: model_validate, model_dump, model_dump_json, model_json_schema, model_config, field_validator")
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    user.dict()
    User.parse_obj({"name": "x"})
    user.json()
print("os nomes do v1 ainda existem, mas AVISAM (obsoletos):", sorted({w.category.__name__ for w in caught}), len(caught), "avisos")
print()
for old, new in (("obj.dict()", "obj.model_dump()"), ("obj.json()", "obj.model_dump_json()"), ("Model.parse_obj(d)", "Model.model_validate(d)"),
                 ("Model.parse_raw(s)", "Model.model_validate_json(s)"), ("Model.schema()", "Model.model_json_schema()"),
                 ("class Config: ...", "model_config = ConfigDict(...)"), ("@validator('x')", "@field_validator('x') + @classmethod"),
                 ("@root_validator", "@model_validator(mode='before' | 'after')"), ("Optional[int] = None é opcional", "int | None SEM default é OBRIGATÓRIO (aceita None)"),
                 ("orm_mode = True", "from_attributes=True"), ("pydantic.BaseSettings", "pydantic_settings.BaseSettings (outro pacote)")):
    print(f"  {old:<36} -> {new}")
print("\no motor de validação foi reescrito em Rust (pydantic-core): em geral muito mais rápido que o v1, com mensagens de erro melhores.")
