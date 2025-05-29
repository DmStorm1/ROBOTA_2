import sys, os
# Вставляємо корінь проекту (де лежать config.py, backend/ і т.п.) в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
