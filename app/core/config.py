import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class Settings:
    """Application configuration for NexusRAG."""

    app_name: str
    environment: str
    log_level: str
    raw_data_dir: Path
    processed_data_dir: Path

    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings from environment variables with safe defaults."""
        return cls(
            app_name=os.getenv("NEXUSRAG_APP_NAME", "NexusRAG"),
            environment=os.getenv("NEXUSRAG_ENV", "development"),
            log_level=os.getenv("NEXUSRAG_LOG_LEVEL", "INFO").upper(),
            raw_data_dir=PROJECT_ROOT / "data" / "raw",
            processed_data_dir=PROJECT_ROOT / "data" / "processed",
        )


settings = Settings.from_env()