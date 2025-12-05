FROM ubuntu:noble-20251013

WORKDIR /app

RUN apt-get update && apt-get install -y python3 python3-pip python3.12-venv 

RUN python3 -m venv .venv \
 && .venv/bin/pip install --no-cache-dir \
    bottle python-dotenv

COPY datoteke/ datoteke/
COPY static/ static/
COPY views/ views/
COPY model.py model.py
COPY spletni_umesnik.py spletni_umesnik.py
COPY .env .env

EXPOSE 8000

ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "spletni_umesnik.py"]