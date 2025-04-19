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
  ```
  python -m venv .venv
  ```
- Install the project dependencies:
  ```
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
