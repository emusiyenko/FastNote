# syntax=docker/dockerfile:1
# escape=\

FROM python
WORKDIR /FastNote
COPY requirements.txt requirements.txt
COPY app app

# install dependencies
RUN pip3 install -r requirements.txt
RUN pip install uvicorn==0.22.0

# expose port
EXPOSE 8000

# entry point
CMD ["python3", "-m", "uvicorn", "app.main:app", "--workers", "4", "--host", "0.0.0.0"]

