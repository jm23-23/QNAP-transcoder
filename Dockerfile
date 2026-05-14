FROM ubuntu:24.04

# Ustawienie trybu nieinteraktywnego, aby instalator nie "wisiał"
ENV DEBIAN_FRONTEND=noninteractive

# Instalacja FFmpeg i sterowników z flagą --no-install-recommends
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    python3 \
    python3-pip \
    intel-media-va-driver-non-free \
    libva-drm2 \
    libva-x11-2 \
    vainfo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Reszta pliku pozostaje bez zmian...
COPY requirements.txt .
RUN pip3 install -r requirements.txt --break-system-packages

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]