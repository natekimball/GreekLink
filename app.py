import uvicorn
from fastapi import FastAPI, File, UploadFile
import LinearMatching
from mangum import Mangum

app = FastAPI()

@app.get("/")
async def welcome():
    return {"message": "Welcome to the Matchr"}

@app.post("/big_little_match")
async def big_little(littlefile: UploadFile = File(...), bigfile: UploadFile = File(...)):
    lf,bf = await handlefiles(littlefile, bigfile)
    [headers, result] = LinearMatching.big_little_match(lf,bf)
    return {
        "headers": headers,
        "result": result
    }

@app.get("/big_little_match")
async def get_big_little():
    return {"message": "Please use POST request to submit big and little files"}

@app.post("/match")
async def match(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    f1,f2 = await handlefiles(file1,file2)
    # print(f1.readlines())
    # print(f2.readlines())
    return LinearMatching.match(f1,f2)

@app.get("/match")
async def get_match():
    return {"message": "Please use POST request to submit files"}

@app.post("/custom_match/{table}/{cols}/{rows}")
async def custom_match(table, cols, rows, file1: UploadFile = File(...), file2: UploadFile = File(...)):
    rows, cols = int(rows), int(cols)
    tablelist = [int(x) for x in table.split(",")]
    table = [[0 for _ in range(cols)] for _ in range(rows)]
    x = 0
    for i in range(cols):
        for j in range(rows):
            table[i][j] = tablelist[x]
            x+=1
    f1,f2 = await handlefiles(file1,file2)
    return LinearMatching.custom_match(f1,f2, table)

@app.get("/custom_match")
async def get_custom_match():
    return {"message": "Please use POST request to submit files and custom table"}

async def handlefiles(file1, file2):
    a, b = [x.decode("utf-8") for x in [await file1.read(), await file2.read()]]
    f1, f2 = open("resources/input/littlefile.txt", "w"), open("resources/input/bigfile.txt", "w")
    f1.writelines(a)
    f2.writelines(b)
    f1.close()
    f2.close()
    return open("resources/input/littlefile.txt", "r"), open("resources/input/bigfile.txt", "r")

handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)