FROM ubuntu:noble-20251013

WORKDIR /app

RUN apt-get update && apt-get install -y python3 python3-pip python3.12-venv 
ENV PATH="/app/.venv/bin:$PATH"

RUN python3 -m venv .venv \
 && .venv/bin/pip install --no-cache-dir --upgrade pip \
 && .venv/bin/pip install --no-cache-dir \
    bottle>=0.12.25 \
    python-dotenv>=1.0.0 \
    gunicorn>=21.2.0 \
    psycopg[binary]>=3.1 \
    psycopg_pool>=3.1


COPY conf/ conf/
COPY datoteke/ datoteke/
COPY model.py model.py
COPY spletni_umesnik.py spletni_umesnik.py

EXPOSE 8081

CMD ["gunicorn", "-c", "conf/gunicorn.conf.py", "spletni_umesnik:app"]