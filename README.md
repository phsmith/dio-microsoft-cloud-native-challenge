## DIO Microsoft Azure Cloud Native Boot Camp Challenge

### Products Register - Cloud E-Commerce

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
  pip install -r requirements.txt
  ```

#### :running: Running the project

This project uses the [Streamlit](https://streamlit.io) Python framework to easily build and deploy a graphical web interface for the application.

Run the project with the command:
```sh
streamlit run main.py
```
By default, Streamlit opens port 8501 on localhost: http://localhost:8501

#### :rocket: Deploy to Azure Container Apps

1. Create an Azure Resource Group:
    ```sh
    export RG_NAME=MyResourceGroup01
    az group create --location eastus --name $RG_NAME
    ```
2. Create an Azure Container Registry:
    ```sh
    export ACR_NAME=myregistry01
    az acr create --name ${ACR_NAME} --resource-group ${RG_NAME} --sku Basic --admin-enabled true
    ```
3. Build the application Docker image:
    ```sh
    export IMAGE_NAME=my-streamlit-app:0.1
    docker build -t ${IMAGE_NAME} .
    ```
4. Login into ACR and push the Docker image:
    ```sh
    az acr login -n ${ACR_NAME}
    docker push ${IMAGE_NAME}
    ```
5. Create a Azure Container App and deploy the application container image:
    ```sh
    export REGISTRY_SERVER=${ACR_NAME}.azurecr.io
    export REGISTRY_USERNAME=<ACR_ADMIN_USERNAME>
    export REGISTRY_PASSWORD=<ACR_ADMIN_PASSWORD>

    az containerapp up \
      --resource-group ${RG_NAME} \
      --name my-containerapp-01 \
      --environment my-containerapp-env-01
      --registry-server ${REGISTRY_SERVER}
      --registry-username ${REGISTRY_USERNAME}
      --registry-password ${REGISTRY_PASSWORD}
      --image ${REGISTRY_SERVER}/${IMAGE_NAME} \
      --ingress external \
      --target-port 8501 \
      --env-vars \
          BLOB_STORAGE_CONNECTION_STRING=<BLOB_STORAGE_CONNECTION_STRING> \
          BLOB_STORAGE_CONTAINER_NAME=<BLOB_STORAGE_CONTAINER_NAME> \
          BLOB_STORAGE_ENDPOINT=<BLOB_STORAGE_ENDPOINT> \
          SQL_SERVER=<SQL_SERVER> \
          SQL_DATABASE=<SQL_DATABASE> \
          SQL_USERNAME=<SQL_USERNAME> \
          SQL_PASSWORD=<SQL_PASSWORD> \
      --browse
    ```
