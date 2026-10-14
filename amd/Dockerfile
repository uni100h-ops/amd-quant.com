# Select an official image compatible with the allocated GPU and host ROCm driver.
ARG ROCM_IMAGE=rocm/pytorch:latest
FROM ${ROCM_IMAGE}
WORKDIR /app
COPY requirements.txt requirements-ml.txt requirements-ibm.txt ./
# The base image supplies ROCm PyTorch. Do not install a CUDA/CPU torch wheel.
RUN python -m pip install --no-cache-dir -r requirements-ml.txt -r requirements-ibm.txt
COPY . .
ENV QCHAT_ROLE=engine QCHAT_PROFILE=micro QCHAT_DEVICE=cuda REQUIRE_AMD=1 QUANTUM_BACKEND=ibm STATE_DIR=/state PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
