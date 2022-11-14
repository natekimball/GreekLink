from fastapi import FastAPI, File, UploadFile
import Matching
# from mangum import Mangum

app = FastAPI()

@app.post("/matchbiglittles")
async def uploadfiles(littlefile: UploadFile = File(...), bigfile: UploadFile = File(...)):
    f1, f2 = await handlefiles(littlefile, bigfile)
    [headers, result] = Matching.big_little_match(f1,f2)
    return {
        "headers": headers,
        "result": result
    }

@app.post("/match")
async def uploadfiles(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    f1,f2 = await handlefiles(file1,file2)
    result = Matching.match(f1,f2)
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

# Mangum(app)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)