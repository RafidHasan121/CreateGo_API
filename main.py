from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import EmailStr, BaseModel
from supabase import create_client, Client
from openai import OpenAI

from services import *
import os

# global vars
description = """
## /

**POST** = creating a new thread with the assistant.\n
**GET** = running the assistant and getting the assistant response.\n
**PATCH** = After updating the creatego JSON file, uploads the updated JSON to the thread.

## /Projects/

**GET** = Get all the projects.

## /Chat/

**GET** = Get chat history of a project or a thread.

## /Upload/

**POST** = Upload chat history to the database.

## /Add/

**POST** = Add a member to a group chat.

"""

app = FastAPI(title="Creatego API", description=description)

client = OpenAI(api_key=os.environ.get("API_KEY"))


# API list
@app.get("/{thread_id}")
def get_assistant(thread_id: str):
    try:
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=os.environ.get("ASSISTANT_ID"),
            stream=True
        )
    except:
        raise HTTPException(status_code=400, detail="Wrong thread id provided")

    # sync response

    # return {"run_id" : run.id,
    #         "thread_id" : run.thread_id}

    # async response

    return StreamingResponse(streaming_generator(run), status_code=200, media_type="text/event-stream")

class post_assistant_model(BaseModel):
    message: str
    project: int
    t_id: str | None = None 

@app.post("/")
def post_assistant(data: post_assistant_model):
    # previous thread

    if data.t_id:
        message = continue_run_request(client, data.project, data.message, data.t_id)

    # new thread

    else:
        message = new_run_request(client, data.message, data.project)

    return {"thread_id": message.thread_id}


@app.patch("/", status_code=200)
def patch_assistant(project: int, t_id: str):
    json_data = get_routes(project)
    id_list = json_uploader(client, project)
    client.beta.threads.messages.create(
        thread_id=t_id, role="user",
        content="the updated json for the project has been attached to this message, future queries are based on this JSON",
        file_ids=id_list)

    run = client.beta.threads.runs.create(
        thread_id=t_id,
        assistant_id=os.environ.get("ASSISTANT_ID"),
    )

    return {"result": "JSON updated"}


@app.get('/projects/')
def project_list():
    return get_projects()


@app.get('/chat/')
def get_chat_history(thread_id: str | None = None, project_id: int | None = None, page: int = 0, limit: int = 5):
    if thread_id and project_id:
        raise HTTPException(
            status_code=400, detail="Provide only project_id or thread_id")
    if project_id:
        try:
            data, error = supabase.table('chat_history').select(
                '*').eq('project_id', project_id).order('created_at', desc=True).limit(limit).offset(page*limit).execute()
        except:
            raise HTTPException(status_code=400, detail=error[1])
    elif thread_id:
        try:
            data, error = supabase.table('chat_history').select(
                '*').eq('thread_id', thread_id).order('created_at', desc=True).limit(limit).offset(page*limit).execute()
        except:
            raise HTTPException(status_code=400, detail=error[1])
    else:
        raise HTTPException(
            status_code=400, detail="Provide either project_id or thread_id")

    return data[1]

class upload_chat_history_model(BaseModel):
    role: str
    project_id: int
    thread_id: str
    message: str

@app.post('/upload/', status_code=200)
def upload_chat_history(data: upload_chat_history_model):
    insert_chat_history(project_id=data.project_id,
                        thread_id=data.thread_id, message=data.message, role=data.role)
    return {"status": "success"}

class add_member_to_groupchat_model(BaseModel):
    project_id: int
    email: EmailStr

@app.post('/add/', status_code=200)
def add_member_to_groupchat(data: add_member_to_groupchat_model):
    insert_group_thread(project_id=data.project_id, email=data.email)
    return {"status": "completed"}
