from pydantic import BaseModel, Field


class TitleResponseSchema(BaseModel):
    title_id: str = Field(description='Идентификатор произведения', alias='titleId')
    title: str = Field(description='Название произведения')
    ordering: int
    region: str = Field(description='Регион произведения')
    language: str = Field(description='Язык произведения')
    types: str = Field(description='Тип произведения')
    attributes: str = Field(description='Атрибуты произведения')
    is_original_title: bool = Field(description='История произведения', alias='isOriginalTitle')


class TitlesResponseSchema(BaseModel):
    titles: list[TitleResponseSchema] = Field(description='Список произведений')
