## About this project

This is project consists in two parts: the first one is an API to implement an SQL interpreter that can do CRUD on CSV files based on SQL queries, and the second one is a client developed on Next with Typescript to interact with the previous backend.

## How to run

### Backend

Go to `api` folder and install the required modules to run the project with this command (additional mpdules may be needed, so check for your terminal messages):

```bash
pip install -r requirements.txt 
```

Next to it you need to do is to create an `.env` file in the root of the repo with the variable `DATABASE_URI` which require to contain the connection string to a `postgre`. Example:

```bash
postgresql://user:password@address/database
```

Then, go to the route `./api/src` and launch `app.py with this command (it is recommended to keep the port since the code contains some references to it in the client, you can change the port but you must also do it in code):

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8085
```

### Client

Get in `client` folder to install the npm modules to mount the app, then run this command:

```bash
npm install
```
Finally, expose the client with:

```bash
npm run dev
```

If you want to run the client for production you can also build the project (`npm run build`) and run it on your server (`npm run start`).