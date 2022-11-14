FROM python:3.8

WORKDIR /code

COPY . /code

ENV VIRTUAL_ENV=/match_env/
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]

# docker run  -p 7000:7000 rankedmatching:latest