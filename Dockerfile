FROM python:3.13.1-slim-bookworm

WORKDIR /app

COPY dist/*.whl .

RUN pip install --upgrade pip
RUN pip install *.whl

EXPOSE 5000

CMD ["flask", "--app=api", "run", "--host=0.0.0.0"]