FROM python:3.6

COPY . /slack/bot/

RUN pip install -r /slack/bot/requirements.txt

EXPOSE 80

CMD ["python", "/slack/bot/bot.py"]
