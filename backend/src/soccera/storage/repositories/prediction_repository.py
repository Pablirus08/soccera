from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from soccera.storage.models.prediction import Prediction


class PredictionRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(
        self,
        match_id: int,
        model_name: str,
        model_version: str,
        prediction_type: str = "pre_match",
        minute: int | None = None,
    ) -> Prediction | None:
        stmt = select(Prediction).where(
            Prediction.match_id == match_id,
            Prediction.model_name == model_name,
            Prediction.model_version == model_version,
            Prediction.prediction_type == prediction_type,
            Prediction.minute.is_(minute) if minute is None else Prediction.minute == minute,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def upsert(
        self,
        match_id: int,
        model_name: str,
        model_version: str,
        prediction_type: str = "pre_match",
        minute: int | None = None,
        **fields: Any,
    ) -> Prediction:
        instance = self.get(match_id, model_name, model_version, prediction_type, minute)
        if instance is None:
            instance = Prediction(
                match_id=match_id,
                model_name=model_name,
                model_version=model_version,
                prediction_type=prediction_type,
                minute=minute,
                **fields,
            )
            self.session.add(instance)
        else:
            for key, value in fields.items():
                setattr(instance, key, value)
        self.session.flush()
        return instance

    def get_by_match(self, match_id: int) -> list[Prediction]:
        stmt = select(Prediction).where(Prediction.match_id == match_id)
        return list(self.session.execute(stmt).scalars())
