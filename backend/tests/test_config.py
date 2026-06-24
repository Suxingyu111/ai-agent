from app.core.config import Settings


def test_settings_can_be_built_from_environment_values() -> None:
    settings = Settings(
        APP_ENV="test",
        SERVER_HOST="127.0.0.1",
        SERVER_PORT=9000,
        CORS_ALLOWED_ORIGINS="http://localhost:5173,http://127.0.0.1:5173",
    )

    assert settings.app_env == "test"
    assert settings.server_port == 9000
    assert settings.cors_allowed_origins == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


def test_settings_reads_comma_separated_cors_origins_from_env_file(tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "APP_ENV=development",
                "CORS_ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173",
            ]
        ),
        encoding="utf-8",
    )

    settings = Settings(_env_file=env_file)

    assert settings.app_env == "development"
    assert settings.cors_allowed_origins == [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ]
