# image: tapis/img-classify:0.2
FROM tensorflow/tensorflow:1.5.0-py3

# Install necessary requirements
RUN pip install requests

# Copy the app into the container
# Need to run in /tmp to avoid permissions problem when not running as root
ADD classify_image.py /tmp/classify_image.py
WORKDIR /tmp

# Note: Using ENTRYPOINT makes this run immediately in non-interactive mode.
ENTRYPOINT ["python", "/tmp/classify_image.py"]
