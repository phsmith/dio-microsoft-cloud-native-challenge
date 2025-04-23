## DIO Microsoft Azure Cloud Native Boot Camp Challenge

### Cloud E-Commerce - Products Register

#### :hammer_and_wrench: Environment Setup

- Install [Dev Containers](https://marketplace.visualstudio.com/items/?itemName=ms-vscode-remote.remote-containers) VS Code extension.
  - With Dev Containers, you get the benefits of a complete development environment with all the services needed running locally.
- From the `View -> Command Pallet` menu, you can perform one of the following options:
  - Dev Containers: Open Folder in Container
  - Dev Containers: Reopen in container
  - Dev Containers: Rebuild and Reopen in container
- The following services are automatically set up in Dev Containers:
  - Azurite (Azure Storage simulator)
  - Azure SQL Server
- Create a Python virtual environment:
  ```sh
  python -m venv .venv
  ```
- Install the project dependencies:
  ```sh
  source .venv/bin/activate
  pip install -r src/backend/requirements.txt -r src/frontend/requirements.txt
  ```

#### :running: Running the project

This project uses the [Streamlit](https://streamlit.io) Python framework to easily build and deploy a graphical web interface for the application, which is integrated with an API built on top of the [FastAPI](https://fastapi.tiangolo.com) framework.

> By default, FastAPI apps are available at http://localhost:8000, you can access the API docs at http://localhost:8000/docs, and Streamlit apps are available at http://localhost:8501.

> Note that each module has an `.env` file for local development.

Open a terminal and run the backend:
```sh
fastapi dev src/backend/main.py
```

Then open another terminal to run the frontend:
```sh
streamlit run src/frontend/main.py
```

Or just use `docker compose`:
```sh
docker compose up
```

#### :rocket: Deploy to Azure Container Apps

1. Create an Azure Resource Group:
    ```sh
    export RG_NAME=MyResourceGroup01
    az group create --location eastus --name $RG_NAME
    ```
2. Create an Azure Container Registry:
    ```sh
    export ACR_NAME=myregistry01
    export REGISTRY_SERVER=${ACR_NAME}.azurecr.io
    az acr create --name ${ACR_NAME} --resource-group ${RG_NAME} --sku Basic --admin-enabled true
    ```
3. Build the backend Docker image:
    ```sh
    export BACKEND_IMAGE_TAG=${REGISTRY_SERVER}/my-fastapi-app:0.1
    docker build -t ${BACKEND_IMAGE_TAG} .
    ```

4. Build the frontend Docker image:
    ```sh
    export FRONTEND_IMAGE_TAG=${REGISTRY_SERVER}/my-streamlit-app:0.1
    docker build -t ${FRONTEND_IMAGE_TAG} .
    ```
5. Login into ACR and push the Docker image:
    ```sh
    az acr login -n ${ACR_NAME}
    docker push ${BACKEND_IMAGE_TAG}
    docker push ${FRONTEND_IMAGE_TAG}
    ```
6. Deploy the `backend` Azure Container App:
    ```sh
    export CONTAINER_APP_ENV_NAME=my-containerapp-env-01
    export REGISTRY_USERNAME=<ACR_ADMIN_USERNAME>
    export REGISTRY_PASSWORD=<ACR_ADMIN_PASSWORD>

    az containerapp up \
      --resource-group ${RG_NAME} \
      --name my-backend-app \
      --environment ${CONTAINER_APP_ENV_NAME}
      --registry-server ${REGISTRY_SERVER}
      --registry-username ${REGISTRY_USERNAME}
      --registry-password ${REGISTRY_PASSWORD}
      --image ${BACKEND_IMAGE_TAG} \
      --ingress external \
      --target-port 8000 \
      --env-vars \
          BLOB_STORAGE_CONNECTION_STRING=<BLOB_STORAGE_CONNECTION_STRING> \
          BLOB_STORAGE_ACCOUNT_NAME=<BLOB_STORAGE_ACCOUNT_NAME> \
          BLOB_STORAGE_CONTAINER_NAME=<BLOB_STORAGE_CONTAINER_NAME> \
          BLOB_STORAGE_ENDPOINT=<BLOB_STORAGE_ENDPOINT> \
          SQL_SERVER=<SQL_SERVER> \
          SQL_DATABASE=<SQL_DATABASE> \
          SQL_USERNAME=<SQL_USERNAME> \
          SQL_PASSWORD=<SQL_PASSWORD>
    ```

7. Deploy the `frontend` Azure Container App:
    ```sh
    export API_FQDN=$(az containerapp show --only-show-errors -g ${RG_NAME} -n my-backend-app --query 'properties.configuration.ingress.fqdn' -o tsv)

    az containerapp up \
      --resource-group ${RG_NAME} \
      --name my-frontend-app \
      --environment ${CONTAINER_APP_ENV_NAME}
      --registry-server ${REGISTRY_SERVER}
      --registry-username ${REGISTRY_USERNAME}
      --registry-password ${REGISTRY_PASSWORD}
      --image ${FRONTEND_IMAGE_TAG} \
      --ingress external \
      --target-port 8501 \
      --env-vars \
          STREAMLIT_SERVER_PORT=8501 \
          STREAMLIT_API_URL=https://${API_FQDN}/api
    ```
