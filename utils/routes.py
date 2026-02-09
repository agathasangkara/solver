import time
import uuid
import asyncio
from fastapi import Query, HTTPException
from fastapi.responses import JSONResponse
from utils.logger import logger
from utils.solvers import solve_turnstile, solve_recaptcha_v3, solve_recaptcha_v2

def register_routes(app, server):

    @app.get("/turnstile")
    async def process_turnstile(url: str = Query(...), sitekey: str = Query(...), action: str = Query(None), cdata: str = Query(None)):
        if not url or not sitekey:
            raise HTTPException(status_code=400, detail={"status": "error", "error": "Required: url, sitekey"})
        if server.current_task_num >= server.max_task_num:
            return JSONResponse(content={"status": "error", "error": "Server at max capacity"}, status_code=429)
        task_id = str(uuid.uuid4())
        logger.info(f"New Turnstile task: {task_id}")
        server.results[task_id] = {"status": "process", "message": "solving turnstile", "start_time": time.time()}
        try:
            asyncio.create_task(solve_turnstile(task_id, url, sitekey, action, cdata, server.results, server.page_pool, server.decrement_task))
            server.current_task_num += 1
            return JSONResponse(content={"task_id": task_id, "status": "accepted"}, status_code=202)
        except Exception as e:
            server.results.pop(task_id, None)
            return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

    @app.get("/recaptchav3")
    async def process_recaptcha_v3(url: str = Query(None), sitekey: str = Query(None), action: str = Query(None), min_score: float = Query(None)):
        if not url or not sitekey:
            raise HTTPException(status_code=400, detail={"status": "error", "error": "Required: url, sitekey"})
        if not action or not min_score:
            raise HTTPException(status_code=400, detail={"status": "error", "error": "Required: action, min_score"})
        if server.current_task_num >= server.max_task_num:
            return JSONResponse(content={"status": "error", "error": "Server at max capacity"}, status_code=429)
        task_id = str(uuid.uuid4())
        logger.info(f"New reCAPTCHA v3 task: {task_id}")
        server.results[task_id] = {"status": "process", "message": "solving recaptcha_v3", "start_time": time.time()}
        try:
            asyncio.create_task(solve_recaptcha_v3(task_id, url, sitekey, action, min_score, server.results, server.page_pool, server.decrement_task))
            server.current_task_num += 1
            return JSONResponse(content={"task_id": task_id, "status": "accepted"}, status_code=202)
        except Exception as e:
            server.results.pop(task_id, None)
            return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

    @app.get("/recaptchav3enterprise")
    async def process_recaptcha_v3_enterprise(url: str = Query(None), sitekey: str = Query(None), action: str = Query(None), min_score: float = Query(None)):
        if not url or not sitekey:
            raise HTTPException(status_code=400, detail={"status": "error", "error": "Required: url, sitekey"})
        if not action or not min_score:
            raise HTTPException(status_code=400, detail={"status": "error", "error": "Required: action, min_score"})
        if server.current_task_num >= server.max_task_num:
            return JSONResponse(content={"status": "error", "error": "Server at max capacity"}, status_code=429)
        task_id = str(uuid.uuid4())
        logger.info(f"New reCAPTCHA v3 Enterprise task: {task_id}")
        server.results[task_id] = {"status": "process", "message": "solving recaptcha_v3_enterprise", "start_time": time.time()}
        try:
            asyncio.create_task(solve_recaptcha_v3(task_id, url, sitekey, action, min_score, server.results, server.page_pool, server.decrement_task))
            server.current_task_num += 1
            return JSONResponse(content={"task_id": task_id, "status": "accepted"}, status_code=202)
        except Exception as e:
            server.results.pop(task_id, None)
            return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

    @app.get("/recaptchav2")
    async def process_recaptcha_v2(url: str = Query(None), sitekey: str = Query(None)):
        if not url or not sitekey:
            raise HTTPException(status_code=400, detail={"status": "error", "error": "Required: url, sitekey"})
        if server.current_task_num >= server.max_task_num:
            return JSONResponse(content={"status": "error", "error": "Server at max capacity"}, status_code=429)
        task_id = str(uuid.uuid4())
        logger.info(f"New reCAPTCHA v2 task: {task_id}")
        server.results[task_id] = {"status": "process", "message": "solving recaptcha_v2", "start_time": time.time()}
        try:
            asyncio.create_task(solve_recaptcha_v2(task_id, url, sitekey, False, server.results, server.page_pool, server.decrement_task))
            server.current_task_num += 1
            return JSONResponse(content={"task_id": task_id, "status": "accepted"}, status_code=202)
        except Exception as e:
            server.results.pop(task_id, None)
            return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

    @app.get("/recaptchav2invisible")
    async def process_recaptcha_v2_invisible(url: str = Query(None), sitekey: str = Query(None)):
        if not url or not sitekey:
            raise HTTPException(status_code=400, detail={"status": "error", "error": "Required: url, sitekey"})
        if server.current_task_num >= server.max_task_num:
            return JSONResponse(content={"status": "error", "error": "Server at max capacity"}, status_code=429)
        task_id = str(uuid.uuid4())
        logger.info(f"New reCAPTCHA v2 Invisible task: {task_id}")
        server.results[task_id] = {"status": "process", "message": "solving recaptcha_v2_invisible", "start_time": time.time()}
        try:
            asyncio.create_task(solve_recaptcha_v2(task_id, url, sitekey, True, server.results, server.page_pool, server.decrement_task))
            server.current_task_num += 1
            return JSONResponse(content={"task_id": task_id, "status": "accepted"}, status_code=202)
        except Exception as e:
            server.results.pop(task_id, None)
            return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

    @app.get("/recaptchav2enterprise")
    async def process_recaptcha_v2_enterprise(url: str = Query(None), sitekey: str = Query(None)):
        if not url or not sitekey:
            raise HTTPException(status_code=400, detail={"status": "error", "error": "Required: url, sitekey"})
        if server.current_task_num >= server.max_task_num:
            return JSONResponse(content={"status": "error", "error": "Server at max capacity"}, status_code=429)
        task_id = str(uuid.uuid4())
        logger.info(f"New reCAPTCHA v2 Enterprise task: {task_id}")
        server.results[task_id] = {"status": "process", "message": "solving recaptcha_v2_enterprise", "start_time": time.time()}
        try:
            asyncio.create_task(solve_recaptcha_v2(task_id, url, sitekey, False, server.results, server.page_pool, server.decrement_task))
            server.current_task_num += 1
            return JSONResponse(content={"task_id": task_id, "status": "accepted"}, status_code=202)
        except Exception as e:
            server.results.pop(task_id, None)
            return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

    @app.get("/result")
    async def get_result(task_id: str = Query(..., alias="id")):
        if not task_id:
            return JSONResponse(content={"status": "error", "message": "Missing task_id"}, status_code=400)
        if task_id not in server.results:
            return JSONResponse(content={"status": "error", "message": "Invalid task_id or expired"}, status_code=404)
        result = server.results[task_id]
        if result.get("status") == "process":
            start_time = result.get("start_time", time.time())
            if time.time() - start_time > 300:
                server.results[task_id] = {
                    "status": "error",
                    "elapsed_time": round(time.time() - start_time, 3),
                    "value": "timeout",
                    "message": "Task timeout"
                }
                result = server.results[task_id]
            else:
                return JSONResponse(content=result, status_code=202)
        result = server.results.pop(task_id)
        if result.get("status") == "success":
            status_code = 200
        elif result.get("value") == "timeout":
            status_code = 408
        elif "fail" in result.get("value", ""):
            status_code = 422
        else:
            status_code = 500
        return JSONResponse(content=result, status_code=status_code)