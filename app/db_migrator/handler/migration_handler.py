from abc import ABC, abstractmethod
import traceback


class MigrationHandler(ABC):

    def __init__(
            self,
            migrator_name: str
    ):
        self._migrator_name = migrator_name

    @abstractmethod
    def _make_migration(self) -> None:
        pass

    def execute(self) -> None:
        print(f"[{self._migrator_name}]: started")
        try:
            self._make_migration()
        except Exception as e:
            print(f"[{self._migrator_name}]: failed with exception - {e}")
            print(f"[{self._migrator_name}] traceback: {traceback.format_exc()}")
            return
        print(f"[{self._migrator_name}]: finished")
