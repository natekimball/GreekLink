from fastapi import FastAPI, File, UploadFile
import Matching

app = FastAPI()

@app.post("/matchbiglittles")
async def uploadfiles(littlefile: UploadFile = File(...), bigfile: UploadFile = File(...)):
    a, b = [x.decode("utf-8") for x in [await littlefile.read(), await bigfile.read()]]
    f1, f2 = open("input/littlefile.txt", "w"), open("input/bigfile.txt", "w")
    f1.writelines(a)
    f2.writelines(b)
    f1.close()
    f2.close()
    f1,f2 = open("input/littlefile.txt", "r"), open("input/bigfile.txt", "r")
    result = Matching.big_little_match(f1,f2)
    return { "result": result }

@app.post("/match")
async def uploadfiles(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    a, b = [x.decode("utf-8") for x in [await file1.read(), await file2.read()]]
    f1, f2 = open("input/file1.txt", "w"), open("input/file2.txt", "w")
    f1.writelines(a)
    f2.writelines(b)
    f1.close()
    f2.close()
    f1,f2 = open("input/file1.txt", "r"), open("input/file2.txt", "r")
    [result, _] = Matching.match(f1,f2)
    return result
