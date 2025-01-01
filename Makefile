# Makefile to automate Docker and Azure Container Registry tasks

.PHONY: login build tag push

# Azure Container Registry name
ACR_NAME=benchmarkregistry
# Docker image name
IMAGE_NAME=benchmark
# Full image name including registry
FULL_IMAGE_NAME=$(ACR_NAME).azurecr.io/$(IMAGE_NAME)

# Login to Azure Container Registry
login:
	az acr login --name $(ACR_NAME)

# Build the Docker image
build:
	docker build -t $(IMAGE_NAME) .

# Tag the Docker image
tag:
	docker tag $(IMAGE_NAME) $(FULL_IMAGE_NAME)

# Push the Docker image to ACR
push:
	docker push $(FULL_IMAGE_NAME)

# Run the app
run:
	poetry run python -m uvicorn app.main:app --reload

# Full pipeline: login, build, tag, and push
deploy: login build tag push
