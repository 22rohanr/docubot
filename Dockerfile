FROM public.ecr.aws/lambda/python:3.9

WORKDIR /var/task

COPY requirements.txt ./
COPY app.py controller.py llm.py ./
COPY templates ./templates

RUN pip install --no-cache-dir -r requirements.txt

CMD ["app.lambda_handler"]
