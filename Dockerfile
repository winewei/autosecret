FROM python:3.7.5-slim-stretch

WORKDIR /srv

COPY . .

RUN pip install -r requirements.txt

CMD ["bash", "-c", "python main.py"]
