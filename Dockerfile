FROM python:3.9

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x src/main.py

RUN prisma generate
 
CMD [ "python", "src/main.py" ]