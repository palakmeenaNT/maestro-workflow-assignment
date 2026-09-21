FROM apache/airflow:2.10.5-python3.11

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt \
    && python -m ipykernel install --user --name python3 --display-name "Python 3"
