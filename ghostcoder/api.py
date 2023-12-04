import os
from pathlib import Path
from starlette.requests import Request
from starlette.responses import Response

from fastapi import FastAPI, Body, Request, Response
import logging

from ghostcoder import FileRepository
from ghostcoder.schema import (
    ListFilesRequest,
    ListFilesResponse,
    WriteCodeRequest,
    WriteCodeResponse,
    ReadFileRequest,
    ReadFileResponse,
    FindFilesRequest,
    FindFilesResponse, BaseResponse, CreateBranchRequest
)
from ghostcoder.main import Ghostcoder

app = FastAPI()

logging_format = '%(asctime)s - %(name)s  - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=logging_format)
logging.getLogger('ghostcoder').setLevel(logging.DEBUG)
logging.getLogger('httpx').setLevel(logging.INFO)
logging.getLogger('openai').setLevel(logging.INFO)
logging.getLogger('httpcore').setLevel(logging.INFO)


# Middleware to log request headers
@app.middleware("http")
async def log_request_headers(request: Request, call_next):
    logging.info(f"Request headers: {request.headers}")
    response = await call_next(request)
    return response

repo_dir = os.environ.get('REPO_DIR', '/home/albert/repos/albert/ghostcoder')
model_name = os.environ.get('MODEL_NAME', 'gpt-4-1106-preview')
debug_mode = os.environ.get('DEBUG_MODE', 'True') == 'True'

repository = FileRepository(repo_path=Path(repo_dir),
                            exclude_dirs=["benchmark", "playground", "tests"])
gc = Ghostcoder(repository=repository, debug_mode=debug_mode)

@app.post("/api/files", response_model=ListFilesResponse)
async def list_files(request: ListFilesRequest = Body(...)):
    response = gc.list_files(request)
    return response

@app.post("/api/code/write", response_model=WriteCodeResponse)
async def write_code(request: WriteCodeRequest = Body(...)):
    response = gc.write_code(request)
    return response

@app.post("/api/files/read", response_model=ReadFileResponse)
async def read_file(request: ReadFileRequest):
    response = gc.read_file(request.file_path)
    return response

@app.post("/api/files/find", response_model=FindFilesResponse)
async def find_files(request: FindFilesRequest = Body(...)):
    response = gc.find_files(request.description)
    return response

@app.post("/api/branch/create", response_model=BaseResponse)
async def create_branch(request: CreateBranchRequest = Body(...)):
    response = gc.create_branch(request)
    return response
