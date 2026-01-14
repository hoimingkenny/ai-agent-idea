# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# We also install a basic C compiler/libs because some python packages might need them,
# although for the listed deps slim might be enough.
# Let's keep it simple first.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Run main.py when the container launches
# We use ENTRYPOINT so arguments can be passed easily
ENTRYPOINT ["python", "main.py"]
