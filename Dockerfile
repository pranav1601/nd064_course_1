FROM python:2.7

COPY porject/techtrends/. /app
#  defines the working directory within the container
WORKDIR /app

RUN pip install -r requirements.txt && python init_db.py

EXPOSE 3111

CMD [ "python", "app.py" ]