import os
import pytest
from src.limiter import limiter
from src.config import settings

@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """
    Fixture autouse que reinicia los contadores del Limiter de SlowAPI antes de cada prueba,
    evitando que las pruebas de ráfaga (burst rate limit) contaminen otros tests.
    """
    try:
        limiter.reset()
    except Exception:
        if hasattr(limiter, "_storage") and hasattr(limiter._storage, "reset"):
            limiter._storage.reset()
    yield

@pytest.fixture(autouse=True)
def isolate_tracker_csv(tmp_path, monkeypatch):
    """
    Fixture autouse que aisla las pruebas utilizando un archivo tracker CSV temporal en tmp_path.
    Previene totalmente la contaminación del archivo data/tracker_diagnosticos.csv del repositorio.
    """
    temp_tracker = tmp_path / "tracker_diagnosticos.csv"
    original_tracker = settings.paths.tracker_csv
    if os.path.exists(original_tracker):
        with open(original_tracker, "r", encoding="utf-8") as f:
            header = f.readline()
        with open(temp_tracker, "w", encoding="utf-8") as f:
            f.write(header)
    else:
        with open(temp_tracker, "w", encoding="utf-8") as f:
            f.write("id,momento,fecha,placa,vehiculo,sintoma,diagnostico_ml,falla_real,campos_completos,ml_coincide,conforme_con_diagnostico\n")
            
    monkeypatch.setattr(settings.paths, "tracker_csv", temp_tracker)
    yield
