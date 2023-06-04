from odmantic import Model, Field


class Title(Model):
    titleId: str = Field(description='Идентификатор произведения')
    title: str = Field(description='Название произведения')
    ordering: int
    region: str = Field(description='Регион произведения')
    language: str = Field(description='Язык произведения')
    types: str = Field(description='Тип произведения')
    attributes: str = Field(description='Атрибуты произведения')
    isOriginalTitle: bool = Field(description='История произведения')


class Principal(Model):
    tconst: str = Field(description='Идентификатор произведения')
    ordering: int = Field(description='Порядковый номер произведения')
    nconst: str = Field(description='Идентификатор произведения')
    category: str = Field(description='Категория произведения')
    job: str = Field(description='Должность произведения')
    characters: str = Field(description='Название')


class Rating(Model):
    averageRating: float = Field(description='Средняя оценка')
    numVotes: int = Field(description='Количество голосов')
    tcost: str = Field(description='Идентификатор произведения')


class Basic(Model):
    tconst: str = Field(description='Идентификатор произведения')
    endYear: str = Field(description='Год выхода произведения')
    titleType: str = Field(description='Тип произведения')
    primaryTitle: str = Field(description='Название произведения')
    originalTitle: str = Field(description='Название произведения')
    isAdult: bool = Field(description='Возрастной рейтинг')
    startYear: str = Field(description='Год выхода произведения')
    genres: str = Field(description='Жанры произведения')
    runtimeMinutes: int = Field(description='Время выхода произведения')

