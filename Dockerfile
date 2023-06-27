FROM python:3.9-slim-buster

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY ./app ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# run program on startup
CMD ["python", "./main.py"]