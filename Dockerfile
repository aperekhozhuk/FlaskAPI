
FROM python:alpine3.7
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install --upgrade pip
RUN flask db upgrade
EXPOSE 5000

CMD ["flask", "run", "--host", "0.0.0.0"]
