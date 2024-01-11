FROM continuumio/miniconda3
WORKDIR /app
COPY environment.yml .
RUN conda env create -f environment.yml

COPY . .
CMD ["conda", "run", "--no-capture-output", "-n", "plot-bot", "python", "app.py"]
