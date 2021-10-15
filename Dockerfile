# API is built with Python so start with that
FROM python
# Metadata
LABEL maintainer="georgecawsdev@gmail.com"
# Copy text file containing python packages to install
COPY requirements.txt .
# Install the python packages from the file
RUN pip3 install -r requirements.txt
# Move the API code into the api folder
WORKDIR /api
COPY src/ .
# Run
CMD ["python3", "./api.py"]