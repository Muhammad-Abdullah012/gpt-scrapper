FROM python:3

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt /app
COPY main.py /app
COPY scrap.py /app/

RUN pip install --upgrade pip
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install playwright
RUN playwright install
RUN playwright install-deps
# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
# ENV NAME World

# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
