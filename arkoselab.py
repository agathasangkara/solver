import asyncio
import random
import json
import time
import uuid
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from camoufox.async_api import AsyncCamoufox
from camoufox import DefaultAddons
from faker import Faker
import uvicorn


class ArkoseAPIServer:
    def __init__(self, headless: bool, thread: int, page_count: int, proxy: str = None):
        self.app = FastAPI()
        self.headless = headless
        self.thread_count = thread
        self.page_count = page_count
        self.proxy = proxy
        self.page_pool = asyncio.Queue()
        self.browser_args = ["--no-sandbox", "--disable-dev-shm-usage"]
        self.results = {}
        self.max_task_num = self.thread_count * self.page_count
        self.current_task_num = 0
        
        self.app.add_event_handler("startup", self._startup)
        self.app.add_event_handler("shutdown", self._shutdown)
        self.app.get("/arkoselab")(self.process_arkose)
        self.app.get("/result")(self.get_result)

    async def _cleanup_results(self):
        while True:
            await asyncio.sleep(3600)
            expired = [tid for tid, res in self.results.items()
                      if isinstance(res, dict) and res.get("status") == "error" 
                      and time.time() - res.get("start_time", 0) > 3600]
            for tid in expired:
                self.results.pop(tid, None)

    async def _startup(self):
        print("[+] Starting Camoufox...")
        print(f"[*] {self.thread_count} browsers x {self.page_count} tabs = {self.max_task_num} total")
        
        self.browsers = []
        
        for browser_num in range(self.thread_count):
            camoufox = AsyncCamoufox(
                headless=self.headless,
                exclude_addons=[DefaultAddons.UBO],
                args=self.browser_args
            )
            browser = await camoufox.start()
            self.browsers.append(browser)
            
            if self.proxy:
                parts = self.proxy.split(':')
                if len(parts) == 4:
                    context = await browser.new_context(
                        viewport={'width': 500, 'height': 700},
                        proxy={"server": f"http://{parts[0]}:{parts[1]}", 
                               "username": parts[2], "password": parts[3]}
                    )
                else:
                    context = await browser.new_context(viewport={'width': 500, 'height': 700})
            else:
                context = await browser.new_context(viewport={'width': 500, 'height': 700})
            
            for tab in range(self.page_count):
                page = await context.new_page()
                await self.page_pool.put((page, context, browser))

        print(f"[+] Ready: {self.page_pool.qsize()} tabs")
        asyncio.create_task(self._cleanup_results())

    async def _shutdown(self):
        for browser in self.browsers:
            try:
                await browser.close()
            except:
                pass

    async def _solve_arkose(self, task_id: str):
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        start_time = time.time()
        page, context, browser = await self.page_pool.get()
        
        try:
            fake = Faker()
            name = fake.name()
            email = f"{fake.word().lower()}{random.randint(1000000000000, 9999999999999)}@gmail.com"
            print(f"\n[*] {task_id} : SOLVING ...")
            captured = {"token": None, "stop": False}
            
            async def handle_response(response):
                if 'arkoselabs.com/fc/gt2/public_key' in response.url:
                    try:
                        status = response.status
                        
                        if status == 400:
                            print(f"[!] {task_id[:8]}: 400 DENIED")
                            self.results[task_id] = {"status": "error", "elapsed_time": round(time.time() - start_time, 3), "value": "access_denied"}
                            captured['stop'] = True
                        elif status == 200:
                            data = json.loads(await response.text())
                            if 'token' in data and data['token']:
                                captured['token'] = data['token']
                                elapsed = round(time.time() - start_time, 3)
                                self.results[task_id] = {"status": 'success', "elapsed_time": elapsed, "value": data['token']}
                                print(f"[+] {task_id[:8]}: {elapsed}s successfully solved")
                    except:
                        pass
            
            page.on("response", handle_response)
            
            await page.goto('https://x.com/i/flow/signup', wait_until='domcontentloaded')
            await asyncio.sleep(2)
            
            if await page.query_selector('text="Something went wrong"'):
                await asyncio.sleep(0.5)
                await page.goto('https://x.com/i/flow/signup', wait_until='domcontentloaded')
                await asyncio.sleep(2)
            
            clicked = False
            for attempt in range(30):
                for text in ['Create account', 'Buat akun']:
                    try:
                        if btn := await page.query_selector(f'text="{text}"'):
                            await btn.click()
                            clicked = True
                            await asyncio.sleep(2)
                            break
                    except:
                        continue
                if clicked:
                    break
                await asyncio.sleep(1)
            
            if not clicked:
                self.results[task_id] = {"status": "error", "elapsed_time": round(time.time() - start_time, 3), "value": "no_button"}
                return
            
            try:
                await (await page.wait_for_selector('input[name="name"]', timeout=5000)).fill(name)
            except:
                pass
            
            await asyncio.sleep(0.5)
            
            try:
                if btn := await page.query_selector('text="Use email instead"'):
                    await btn.click()
                    await asyncio.sleep(1)
            except:
                pass
            
            try:
                await (await page.wait_for_selector('input[name="email"]', timeout=3000)).fill(email)
            except:
                pass
            
            await asyncio.sleep(0.5)
            
            try:
                selects = await page.query_selector_all('select')
                if len(selects) >= 3:
                    await selects[0].select_option(str(random.randint(1, 12)))
                    await selects[1].select_option(str(random.randint(1, 28)))
                    await selects[2].select_option(str(random.randint(1985, 2000)))
            except:
                pass
            
            await asyncio.sleep(1)
            
            for text in ['Next', 'Berikutnya']:
                try:
                    if btn := await page.query_selector(f'text="{text}"'):
                        await btn.click()
                        break
                except:
                    continue
            
            await asyncio.sleep(3)
            
            if await page.query_selector('text="Customize your experience"'):
                try:
                    if boxes := await page.query_selector_all('input[type="checkbox"]'):
                        await boxes[0].click()
                        await asyncio.sleep(0.5)
                except:
                    pass
                
                for text in ['Next', 'Berikutnya']:
                    try:
                        if btn := await page.query_selector(f'text="{text}"'):
                            await btn.click()
                            break
                    except:
                        continue
                
                await asyncio.sleep(2)
            
            for _ in range(25):
                if captured['stop'] or captured['token']:
                    break
                await asyncio.sleep(1)
            
            if not captured['token'] and not captured['stop']:
                self.results[task_id] = {"status": "error", "elapsed_time": round(time.time() - start_time, 3), "value": "no_token"}
            
            await page.goto('about:blank')
        
        except Exception as e:
            self.results[task_id] = {"status": "error", "elapsed_time": round(time.time() - start_time, 3), "value": str(e)}
        
        finally:
            self.current_task_num -= 1
            await self.page_pool.put((page, context, browser))

    async def process_arkose(self):
        if self.current_task_num >= self.max_task_num:
            return JSONResponse(content={"status": "error"}, status_code=429)
        
        task_id = str(uuid.uuid4())
        self.results[task_id] = {"status": "process", "start_time": time.time()}
        
        asyncio.create_task(self._solve_arkose(task_id))
        self.current_task_num += 1
        return JSONResponse(content={"task_id": task_id, "status": "accepted"}, status_code=202)

    async def get_result(self, task_id: str = Query(..., alias="id")):
        if task_id not in self.results:
            return JSONResponse(content={"status": "error"}, status_code=404)
        
        result = self.results[task_id]
        
        if result.get("status") == "process":
            if time.time() - result.get("start_time", 0) > 180:
                result = {"status": "error", "value": "timeout"}
                self.results[task_id] = result
            else:
                return JSONResponse(content=result, status_code=202)
        
        result = self.results.pop(task_id)
        return JSONResponse(content=result, status_code=200 if result.get("status") == "success" else 500)

server = ArkoseAPIServer(
    headless=True,
    thread=1,
    page_count=1,
    proxy="5.78.64.26:823:8df0abssa5e2da33872d:5745b9cxs12bbdb5" #host:port:user:pass
)
uvicorn.run(server.app, host="127.0.0.1", port=5034)
