from app.core.db import normalize_database_url


def test_postgres_scheme_corto_usa_psycopg3():
    assert (
        normalize_database_url("postgres://user:pass@host/db")
        == "postgresql+psycopg://user:pass@host/db"
    )


def test_postgresql_sin_driver_usa_psycopg3():
    assert (
        normalize_database_url("postgresql://user:pass@host/db")
        == "postgresql+psycopg://user:pass@host/db"
    )


def test_sqlite_no_se_modifica():
    assert normalize_database_url("sqlite:///./dev.db") == "sqlite:///./dev.db"


def test_url_con_driver_explicito_no_se_modifica():
    assert (
        normalize_database_url("postgresql+psycopg://user:pass@host/db")
        == "postgresql+psycopg://user:pass@host/db"
    )
