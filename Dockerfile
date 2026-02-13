# Python 3.10 පාවිච්චි කරන්න
FROM python:3.10

# වැඩ කරන තැන හදාගන්න
WORKDIR /app

# Requirements දාලා Install කරගන්න
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ඔයාගේ Project ෆයිල් ඔක්කොම මෙතනට දාන්න
COPY . .

# Database එකට ලියන්න අවසර දෙන්න (වැදගත්ම කෑල්ල)
RUN chmod 777 .

# App එක Run කරන්න (Port 7860 තමයි HF ඉල්ලන්නේ)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]