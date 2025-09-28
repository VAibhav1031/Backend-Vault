FROM python:3.13-slim 

WORKDIR /task_app

COPY . .

RUN apt-get update && apt-get install -y postgresql-client && \
    pip3 install uv && \
    uv sync \
    && rm -rf /var/lib/apt/lists/*


RUN chmod +x docker-entrypoint.sh 

EXPOSE 5555

ENTRYPOINT ["./docker-entrypoint.sh"]

# ENTRYPOINT ["uv","run"]
#
# CMD ["python","run.py"]
#


