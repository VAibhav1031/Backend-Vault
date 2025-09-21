FROM python:3.13-slim 

WORKDIR /task_app

COPY . .

RUN pip3 install uv && uv sync


ENTRYPOINT ["uv","run"]

CMD ["python","run.py"]



