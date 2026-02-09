import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from utils.config import HOST, PORT, HEADLESS, THREAD, PAGE_COUNT, PROXY_SUPPORT, STATIC_DIR
from utils.logger import logger
from utils.browser import initialize_browser, cleanup_results_loop, periodic_cleanup_loop, create_context_with_proxy
from utils.routes import register_routes

class CaptchaSolverServer:
    def __init__(self, headless, thread, page_count, proxy_support):
        self.app = FastAPI()
        self.headless = headless
        self.thread_count = thread
        self.page_count = page_count
        self.proxy_support = proxy_support
        self.page_pool = asyncio.Queue()
        self.camoufox = None
        self.browser = None
        self.results = {}
        self.proxies = []
        self.max_task_num = self.thread_count * self.page_count
        self.current_task_num = 0

        STATIC_DIR.mkdir(parents=True, exist_ok=True)
        self.app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

        self.app.add_event_handler("startup", self._startup)
        self.app.add_event_handler("shutdown", self._shutdown)

        register_routes(self.app, self)

    def decrement_task(self):
        self.current_task_num -= 1

    async def _startup(self):
        logger.info("Start initializing the browser")
        try:
            self.camoufox, self.browser = await initialize_browser(
                self.headless, self.thread_count, self.page_count, self.page_pool
            )
            asyncio.create_task(cleanup_results_loop(self.results))
            asyncio.create_task(periodic_cleanup_loop(
                self.page_pool,
                self.max_task_num,
                lambda: create_context_with_proxy(self.browser)
            ))
        except Exception as e:
            logger.error(f"Browser initialization failed: {str(e)}")
            raise

    async def _shutdown(self):
        logger.info("Start cleaning browser resources")
        try:
            if self.browser:
                await self.browser.close()
        except Exception as e:
            logger.warning(f"Exception when closing the browser: {e}")
        logger.success("All browser resources have been cleaned")

def create_app():
    server = CaptchaSolverServer(
        headless=HEADLESS,
        thread=THREAD,
        page_count=PAGE_COUNT,
        proxy_support=PROXY_SUPPORT
    )
    return server.app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)