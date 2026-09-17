import time
from dataclasses import dataclass

@dataclass(slots=True)
class ExecutionResult:
    exit_code: int

class DummyExecutor:
    """
    Временный executor для проверки worker.
    потом заменить на RepoSyncExecutor.
    """
    def __init__(
        self,
        delay_seconds: int = 5,
        fail: bool = False,
    ):
        self.delay_seconds = delay_seconds
        self.fail = fail

    def execute(
            self,
            job_id: int,
    ) -> ExecutionResult:
        time.sleep(
            self.delay_seconds
        )

        if self.fail:
            raise RuntimeError(
                "dummy executor failure"
            )
        
        return ExecutionResult(
            exit_code=0,
        )
