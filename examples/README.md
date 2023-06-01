## Setup Instructions

The app is built with Python 3.9. Clone this repository and follow the steps below
to get started.

### Create conda environment:

```bash
conda create -n demo-examples python=3.9 -y
conda activate demo-examples
```

You can choose any other environment manager of your choice.

### Install dependencies:

```bash
pip install -r requirements.txt
```

### Run the application

To run a demo example, select the command based on the langchain use case you want to try out.

```
uvicorn app.<app_name>:app --reload
```

Jump to [Demo Applications](#demo-applications) section to see the list of available applications.

### Websocket Testing

Open http://localhost:8000 in your browser to access the chatbot UI with websocket support.

## Demo Applications

### Conversation Chain

Start FastAPI server:

```bash
uvicorn app.conversation_chain:app --reload
```
