FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install --no-cache-dir \
    dash \
    plotly \
    scikit-image \
    pandas \
    gunicorn 

ENTRYPOINT ["gunicorn", "-w", "1", "-b", "0.0.0.0:8050", "app:server"]