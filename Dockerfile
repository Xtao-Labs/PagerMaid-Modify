FROM mrwangzhe/pagermaid_os:latest
USER pagermaid
RUN mkdir /pagermaid/workdir
RUN git clone -b master https://github.com/Xtao-Labs/PagerMaid-Modify.git /pagermaid/workdir
WORKDIR /pagermaid/workdir
RUN python -m pip install -r requirements.txt \
    && rm -rf /pagermaid/.cache
CMD ["sh","utils/docker-run.sh"]
