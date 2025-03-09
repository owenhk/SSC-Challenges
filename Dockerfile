# Step 1: Use the official Python 3.12 image
FROM python:3.12-slim
LABEL author="Owen Hills-Klaus with help from ChatGPT ;)"

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the requirements file into the container
COPY requirements.txt .

# Step 4: Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the application code into the container
COPY . .

EXPOSE 8080

# Step 7: Define the command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]