FROM python:3.9

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x marketbot/main.py

RUN prisma generate
 
CMD [ "python", "marketbot/main.py" ]