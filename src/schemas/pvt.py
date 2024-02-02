from pydantic import BaseModel, Field


class PvtRequest(BaseModel):
    """
    Схема для валидации запроса на расчет параметров расхода, плотности и вязкости смеси
    """

    P: float = Field(title="Давление, Па", gt=0)
    T: float = Field(title="Температура, К", gt=0)
    GammaOil: float = Field(title="Относительная плотность нефти, доли", gt=0)
    GammaGas: float = Field(title="Относительная плотность газа, доли", gt=0)
    GammaWat: float = Field(title="Относительная плотность воды, доли", gt=0)
    Wct: float = Field(title="Обводненности, доли", ge=0, le=1)
    Rp: int = Field(title="Газовый фактор, м3/т", gt=0)
    QLiq: float = Field(title="Объем жидкости, м3", gt=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "P": 40.5,
                "T": 296,
                "GammaOil": 0.8,
                "GammaGas": 0.7,
                "GammaWat": 1,
                "Wct": 0.5,
                "Rp": 100,
                "QLiq": 90,
            }
        }
    }


class PvtResponse(BaseModel):
    """
    Схема для валидации параметров расхода, плотности и вязкости смеси
    """

    QMix: float = Field(title="Расход смеси", gt=0)
    RhoMix: float = Field(title="Плотность смеси", gt=0)
    MuMix: float = Field(title="Вязкость смеси", gt=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "QMix": 30,
                "RhoMix": 40,
                "MuMix": 0.3,
            }
        }
    }
