# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR . /app

# Copy the requirements file into the container at /app
COPY . /requirements.txt 

# Install dependencies
RUN pip install --no-cache-dir -r  . /requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Expose port 8000 to allow communication to/from server
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
