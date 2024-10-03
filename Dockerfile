FROM python:3.11-slim
RUN apt-get update && apt-get install -y \
    texlive \
    texlive-latex-base \
    texlive-lang-cyrillic \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-science \
    imagemagick
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
ENV PASSW_ADMIN=r04S9[*.Wb6
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]