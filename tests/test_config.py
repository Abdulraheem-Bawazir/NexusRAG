from app.core.config import PROJECT_ROOT, Settings


def test_default_settings() -> None:
    settings = Settings.from_env()

    assert settings.app_name == "NexusRAG"
    assert settings.environment == "development"
    assert settings.log_level == "INFO"


def test_data_directories() -> None:
    settings = Settings.from_env()

    assert settings.raw_data_dir == PROJECT_ROOT / "data" / "raw"
    assert settings.processed_data_dir == PROJECT_ROOT / "data" / "processed"