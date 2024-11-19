# Use an official Python runtime as a parent image
FROM python:3.12-slim

RUN apt-get update && \
    apt-get -y install curl && \
    apt-get -y install gnupg

RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
    curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    ACCEPT_EULA=Y apt-get install -y mssql-tools18 && \
    echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc && \
    apt-get install -y unixodbc-dev

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN python3 -m pip install --upgrade pip
RUN pip3 install poetry
RUN poetry config virtualenvs.create false

# Copy the poetry files into the container and install
COPY poetry.lock pyproject.toml ./
RUN poetry install

# Copy the rest of the application code into the container
COPY app app

# Expose port 80 to the outside world
EXPOSE 80

# Run the FastAPI app using uvicorn
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
