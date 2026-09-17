import signal
from repoadm.worker import Worker, DummyExecutor
from repoadm.config import settings

def main() -> None:
    worker = Worker(
        executor=DummyExecutor(),
        poll_interval=(
            settings.poll_interval
        ),
    )

    signal.signal(
        signal.SIGTERM,
        worker.stop,
    )

    signal.signal(
        signal.SIGINT,
        worker.stop,
    )

    worker.run()

if __name__ == "__main__":
    main()
