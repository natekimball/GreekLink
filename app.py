# import json
import uvicorn
from fastapi import FastAPI, File, UploadFile
import sys
sys.path.append("${LAMBDA_TASK_ROOT}")
import LinearMatching
from mangum import Mangum
# from pydantic import BaseModel
from tabulate import tabulate
# from typing import List, Union
from fastapi import Form
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# class Item(BaseModel):
#     littles: str
#     bigs: str
#     table: Union[List[List[int]], None] = None

@app.get("/")
async def welcome():
    return {"message": "Welcome to the Matchr"}

@app.post("/big_little_file_match/{bias}")
async def big_little(littlefile: UploadFile = File(), bigfile: UploadFile = File(), bias: bool = True):
    lf,bf = await handlefiles(littlefile, bigfile)
    try:
        [headers, result] = LinearMatching.big_little_match(lf,bf, bias)
    except Exception as e:
        return { 'error':  str(e) }
    return {
        "headers": headers,
        "result": result
    }

# @app.post("/big_little_match")
# async def big_little(item: Item):
#     littles, bigs = item.littles.splitlines(), item.bigs.splitlines()
#     print(littles, bigs)
#     [headers, result] = LinearMatching.big_little_match(littles,bigs)
#     return {
#         "result": tabulate(result, headers=headers, tablefmt="fancy_grid")
#     }
    
@app.post("/big_little_match")
async def big_little(littles: str = Form(), bigs: str = Form(), bias: bool = Form()):
    # print(item)
    # item = json.loads(item, strict=False)
    # print(item)
    # littles, bigs = item['littles'].splitlines(), item['bigs'].splitlines()
    littles, bigs = littles.splitlines(), bigs.splitlines()
    try:
        [headers, result] = LinearMatching.big_little_match(littles,bigs, bias)
        for x in result:
            for y in x:
                y += '\t\t\t'
    except Exception as e:
        return { "error": str(e) }
    return { "result": tabulate(result, headers=headers, tablefmt="html") }

@app.get("/big_little_match")
async def get_big_little():
    return {"message": "Please use POST request to submit big and little files"}

@app.post("/file_match")
async def match(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    f1,f2 = await handlefiles(file1,file2)
    try:
        return LinearMatching.match(f1,f2)
    except Exception as e:
        return { 'error':  str(e) }

@app.post("/match")
async def match(littles: str = Form(), bigs: str = Form()):
    littles, bigs = littles.splitlines(), bigs.splitlines()
    try:
        return LinearMatching.match(littles,bigs)
    except Exception as e:
        return { 'error':  str(e) }

@app.get("/match")
async def get_match():
    return {"message": "Please use POST request to submit files"}

@app.post("/custom_file_match/{table}/{cols}/{rows}")
async def custom_match(table, cols, rows, file1: UploadFile = File(...), file2: UploadFile = File(...)):
    table = create_table(table, cols, rows)
    f1,f2 = await handlefiles(file1,file2)
    try:
        return LinearMatching.custom_match(f1,f2, table)
    except Exception as e:
        return { 'error':  str(e) }

@app.post("/custom_match")
async def custom_match(littles: str = Form(), bigs: str = Form(), table: str = Form(), cols: int = Form(), rows: int = Form()):
    table = create_table(table, cols, rows)
    littles, bigs = littles.splitlines(), bigs.splitlines()
    try:
        return LinearMatching.custom_match(littles, bigs, table)
    except Exception as e:
        return { 'error':  str(e) }

@app.get("/custom_match")
async def get_custom_match():
    return {"message": "Please use POST request to submit files and custom table"}

async def handlefiles(file1, file2):
    return [x.decode("utf-8").splitlines() for x in [await file1.read(), await file2.read()]]

def create_table(table, cols, rows):
    rows, cols = int(rows), int(cols)
    tablelist = [int(x) for x in table.split(",")]
    table = [[0 for _ in range(cols)] for _ in range(rows)]
    x = 0
    for i in range(cols):
        for j in range(rows):
            table[i][j] = tablelist[x]
            x+=1
    return table

handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)