FROM continuumio/miniconda3
WORKDIR /app
COPY environment.yml .
RUN conda env create -f environment.yml

COPY . .
EXPOSE 80
CMD ["conda", "run", "--no-capture-output", "-n", "plot-bot", "python", "app.py"]
