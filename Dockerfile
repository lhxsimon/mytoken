FROM debian as python-base
COPY src/ /opt/src/

RUN apt-get update \
    && apt-get install -y python3 python3-venv python3-dev build-essential

RUN python3 -m venv /opt/env \
    && /opt/env/bin/pip3 install -U pip \
    && /opt/env/bin/pip3 install -r /opt/src/requirements.txt

FROM debian
COPY src/ /opt/src/
COPY --from=python-base /opt/env/ /opt/env/
RUN apt-get update \
    && apt-get install -y python3 ca-certificates curl

WORKDIR /opt/src/
EXPOSE 8000
CMD ["/opt/env/bin/python3", "run.py"]
