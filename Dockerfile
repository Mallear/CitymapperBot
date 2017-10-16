FROM python:3.6

COPY . /slack/bot/

RUN pip install slackclient
RUN pip install googlemaps
RUN pip install pyyaml

EXPOSE 80

CMD ["python", "/slack/bot/bot.py"]
