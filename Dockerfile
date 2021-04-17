FROM ubuntu:hirsute
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    LANG=zh_CN.UTF-8 \
    SHELL=/bin/bash \
    PS1="\u@\h:\w \$ " \
    PAGERMAID_DIR=/pagermaid \
    DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]
RUN source ~/.bashrc \
    && apt update \
    && apt upgrade -y \
    && apt install --no-install-recommends -y \
        software-properties-common \
        build-essential \
        sudo \
        python3 \
        python3-dev \
        python3-pip \
        python3-magic \
        python3-dateparser \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-chi-sim \
        git \
        openssl \
        redis-server \
        curl \
        wget \
        neofetch \
        imagemagick \
        ffmpeg \
        fortune-mod \
        figlet \
        libzbar-dev \
        libxslt1-dev \
        libxml2-dev \
    && apt clean -y \
    && apt autoclean -y
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone
RUN ln -sf /usr/bin/python3 /usr/bin/python \
    && python -m pip install --upgrade pip \
    && pip install wheel \
    && pip install eyed3 pycryptodome
RUN sed -e 's;^# \(%wheel.*NOPASSWD.*\);\1;g' -i /etc/sudoers
RUN useradd pagermaid -r -m -d /pagermaid
RUN usermod -aG sudo,users pagermaid
USER pagermaid
RUN mkdir /pagermaid/workdir
RUN git clone -b master https://github.com/Xtao-Labs/PagerMaid-Modify.git /pagermaid/workdir
WORKDIR /pagermaid/workdir
RUN pip -m pip install -r requirements.txt
RUN sudo rm -rf /root/.cache
CMD ["sh","utils/docker-run.sh"]
