# ---------- 1. aşama: build -------------------------------------------------
# Bölüm 2'deki adımların aynısı: bağımlılık, lint, test, paket.
# Bu aşamada pytest, flake8 ve testler vardır; son image'a girmezler.
FROM python:3.12-slim AS build
ENV PIP_ROOT_USER_ACTION=ignore PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

# Önce yalnızca requirements dosyaları: bağımlılık layer'ı cache'te kalır
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .
RUN flake8 .
RUN pytest -q
RUN pip wheel . --no-deps --no-cache-dir -w dist

# ---------- 2. aşama: çalışma -----------------------------------------------
# Yalnızca artifact (.whl) alınır; pip onu çalışma bağımlılığıyla (babel) kurar.
FROM python:3.12-slim
ENV PIP_ROOT_USER_ACTION=ignore PIP_DISABLE_PIP_VERSION_CHECK=1
COPY --from=build /app/dist/sepet_hesaplama-1.0.0-py3-none-any.whl /tmp/
RUN pip install --no-cache-dir /tmp/sepet_hesaplama-1.0.0-py3-none-any.whl \
    && rm /tmp/sepet_hesaplama-1.0.0-py3-none-any.whl

USER nobody
CMD ["python", "-m", "cart"]
