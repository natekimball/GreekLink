import uvicorn
from fastapi import FastAPI, File, UploadFile
import Matching
from mangum import Mangum

app = FastAPI()

@app.post("/big_little_match")
async def match(littlefile: UploadFile = File(...), bigfile: UploadFile = File(...)):
    f1, f2 = await handlefiles(littlefile, bigfile)
    [headers, result] = Matching.big_little_match(f1,f2)
    return {
        "headers": headers,
        "result": result
    }

@app.post("/match")
async def match(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    f1,f2 = await handlefiles(file1,file2)
    result = Matching.match(f1,f2)
    return result

@app.post("/custom_match/{table}/{cols}/{rows}")
async def match(table, cols, rows, file1: UploadFile = File(...), file2: UploadFile = File(...)):
    rows, cols = int(rows), int(cols)
    tablelist = [int(x) for x in table.split(",")]
    table = [[0 for _ in range(cols)] for _ in range(rows)]
    x = 0
    for i in range(cols):
        for j in range(rows):
            table[i][j] = tablelist[x]
            x+=1
    f1,f2 = await handlefiles(file1,file2)
    result = Matching.custom_match(f1,f2, table)
    return result

async def handlefiles(file1, file2):
    a, b = [x.decode("utf-8") for x in [await file1.read(), await file2.read()]]
    f1, f2 = open("resources/input/littlefile.txt", "w"), open("resources/input/bigfile.txt", "w")
    f1.writelines(a)
    f2.writelines(b)
    f1.close()
    f2.close()
    f1,f2 = open("resources/input/littlefile.txt", "r"), open("resources/input/bigfile.txt", "r")
    return f1,f2

handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=7000)