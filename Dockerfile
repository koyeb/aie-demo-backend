FROM python:3.13

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install uv && \
    uv pip install --system alembic && \
    uv pip install --system -e .  # Installs dependencies using uv

ARG DEV=false
RUN if [ "$DEV" = "true" ] ; then uv pip install --system -e .[dev] ; fi

COPY ./app/ ./
COPY ./alembic/ ./alembic
COPY alembic.ini .
COPY docker/entrypoint.sh ./entrypoint.sh

ENV PYTHONPATH "${PYTHONPATH}:/app"

EXPOSE 8080
CMD ["/app/entrypoint.sh"]
