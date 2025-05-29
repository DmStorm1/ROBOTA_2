import importlib.util
from tools import gen_config

def test_config_generated(tmp_path, monkeypatch):
    # Переміщаємося до тимчасової папки
    monkeypatch.chdir(tmp_path)
    # Пишемо файл student_id.txt з тестовим імʼям
    (tmp_path / "student_id.txt").write_text("TestStudent", encoding="utf-8")
    # Генеруємо config.py
    gen_config.generate_config()
    # Динамічно завантажуємо згенерований файл config.py
    spec = importlib.util.spec_from_file_location("config", str(tmp_path / "config.py"))
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)
    # Перевіряємо, що STUDENT_ID починається з "TestStudent_"
    assert cfg.STUDENT_ID.startswith("TestStudent_")
    # Перевіряємо, що SOURCES – це порожній список
    assert isinstance(cfg.SOURCES, list) and cfg.SOURCES == []
