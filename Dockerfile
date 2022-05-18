FROM python:3.9
LABEL Maintainer="Pranav C"
COPY ./requirements.txt /usr/app/src/requirements.txt
WORKDIR /usr/app/src
RUN pip install -r requirements.txt
COPY . /usr/app/src
CMD [ "python", "./tracing.py"]