FROM harbor.changdu.ltd:443/nlp/deeplotx:0.4.6

WORKDIR /serving
COPY . .
RUN rm -rf ./.venv
RUN timeout 20m pip install -r ./requirements.txt
RUN chmod +x /serving/null.sh
RUN chmod +x /serving/run.sh

CMD echo 'Service starts.' && if [ "$OS_ENV" = "prod" ]; then \
        /bin/bash /serving/run.sh; \
    else \
        /bin/bash /serving/run.sh; \
    fi