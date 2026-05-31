FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir globus-compute-endpoint "numpy==2.4.6"

RUN useradd -m compute
USER compute
WORKDIR /home/compute

COPY --chown=compute:compute user_config_template.yaml.j2 entrypoint.sh ./

ENTRYPOINT ["bash", "entrypoint.sh"]
