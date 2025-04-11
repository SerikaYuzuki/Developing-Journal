FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
ENV LANG=en_US.UTF-8

# 必要な依存をインストール（Rは省略）
RUN apt-get update && apt-get install -y \
    curl \
    git \
    wget \
    python3 \
    python3-pip \
    pandoc \
    texlive-full \
    fonts-noto-cjk \
    && apt-get clean

# Quarto CLIのインストール（Debianパッケージ）
RUN curl -LO https://quarto.org/download/latest/quarto-linux-amd64.deb && \
    dpkg -i quarto-linux-amd64.deb && \
    rm quarto-linux-amd64.deb

# JupyterとQuarto連携用パッケージ
RUN pip install --break-system-packages jupyter \
    numpy matplotlib pandas scipy plotly \
    rdkit

WORKDIR /workspace

CMD ["/bin/bash"]
