import logging
import time

from repoadm.database import SessionLocal
from repoadm.services import (
    claim_next_job,
    complete_job_successfully,
    complete_job_with_failure,
    recover_interrupted_jobs,
)
from repoadm.worker.executor import DummyExecutor

logger = logging.getLogger(__name__)

class Worker:
    def __init__(
        self,
        executor: DummyExecutor,
        poll_interval: int
    ):
        self.executor = executor
        self.poll_interval = poll_interval
        self.running = True

    def stop(
        self,
        signum = None,
        frame = None,
    ) -> None:
        logger.info(
            "worker shutdown requested"
        )

        self.running = False

    def run(self) -> None:
        logger.info(
            "worker started"
        )

        with SessionLocal() as db:
            recovered = recover_interrupted_jobs(
                db
            )

        if recovered:
            logger.warning(
                "recovered %s interrupted jobs",
                recovered,
            )

        while self.running:

            with SessionLocal() as db:
                job = claim_next_job(db)

            if job is None:
                time.sleep(
                    self.poll_interval
                )
                continue

            logger.info(
                "job %s started",
                job.id,
            )

            try:
                result = self.executor.execute(
                    job.id
                )

            except Exception as e:
                logger.exception(
                    "job %s failed",
                    job.id
                )

                with SessionLocal() as db:
                    complete_job_with_failure(
                        db=db,
                        job_id=job.id,
                        error_message=str(e),
                    )

                continue

            with SessionLocal() as db:
                complete_job_successfully(
                    db = db,
                    job_id=job.id,
                    exit_code=result.exit_code,
                )

            logger.info(
                "job %s complited",
                job.id,
            )

        logger.info(
            "worker stopped"
        )
