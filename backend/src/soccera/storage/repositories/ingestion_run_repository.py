from datetime import datetime, timezone

from sqlalchemy.orm import Session

from soccera.storage.models.ingestion_run import IngestionRun


class IngestionRunRepository:
    def __init__(self, session: Session):
        self.session = session

    def start(
        self,
        source: str,
        job_type: str,
        entity_type: str,
        league_source_id: str | None = None,
        season_year: int | None = None,
    ) -> IngestionRun:
        run = IngestionRun(
            source=source,
            job_type=job_type,
            entity_type=entity_type,
            status="started",
            started_at=datetime.now(timezone.utc),
            league_source_id=league_source_id,
            season_year=season_year,
        )
        self.session.add(run)
        self.session.flush()
        return run

    def finish(self, run: IngestionRun, records_processed: int, error_message: str | None = None) -> None:
        run.finished_at = datetime.now(timezone.utc)
        run.records_processed = records_processed
        run.status = "failed" if error_message else "success"
        run.error_message = error_message
        self.session.flush()
