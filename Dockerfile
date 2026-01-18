FROM apify/actor-python:3.11
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py document_processor.py study_generator.py export_utils.py ./
CMD ["python3", "-u", "main.py"]