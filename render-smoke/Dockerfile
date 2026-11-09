FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 gcc-mips-linux-gnu binutils-mips-linux-gnu libc6-dev-mips-cross \
    libcapstone-dev pkgconf bsdextrautils build-essential \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENV PATH="/app/tools:${PATH}"
COPY . /app
RUN mips-linux-gnu-gcc -fsyntax-only -std=gnu99 \
    -I. -Iinclude -Iinclude/n64 -Isrc \
    -DVERSION_US=1 -DNO_ERRNO_H=1 \
    -DF3DZEX_NON_GBI_2=1 -DF3DEX_GBI_2=1 -DF3DEX_GBI_SHARED=1 \
    src/game/mario.c
CMD ["python3", "render-smoke/server.py"]
