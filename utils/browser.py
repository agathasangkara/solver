import asyncio
from camoufox import DefaultAddons
from camoufox.async_api import AsyncCamoufox
from utils.logger import logger

BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
]

async def create_context_with_proxy(browser, proxy=None):
    if not proxy:
        return await browser.new_context()
    parts = proxy.split(':')
    if len(parts) == 3:
        return await browser.new_context(proxy={"server": proxy})
    elif len(parts) == 5:
        proxy_scheme, proxy_ip, proxy_port, proxy_user, proxy_pass = parts
        return await browser.new_context(
            proxy={
                "server": f"{proxy_scheme}://{proxy_ip}:{proxy_port}",
                "username": proxy_user,
                "password": proxy_pass
            }
        )
    else:
        logger.warning(f"Invalid proxy format: {proxy}, using a proxyless context")
        return await browser.new_context()

async def initialize_browser(headless, thread_count, page_count, page_pool):
    camoufox = AsyncCamoufox(
        headless=headless,
        exclude_addons=[DefaultAddons.UBO],
        args=BROWSER_ARGS
    )
    browser = await camoufox.start()
    for _ in range(thread_count):
        context = await create_context_with_proxy(browser)
        for _ in range(page_count):
            page = await context.new_page()
            await page_pool.put((page, context))
    logger.success(f"Page pool initialization is complete, including {page_pool.qsize()} Pages")
    return camoufox, browser

async def cleanup_results_loop(results):
    import time
    while True:
        await asyncio.sleep(3600)
        expired = [
            tid for tid, res in results.items()
            if isinstance(res, dict) and res.get("status") == "error"
               and time.time() - res.get("start_time", 0) > 3600
        ]
        for tid in expired:
            results.pop(tid, None)
            logger.debug(f"Clean up expired tasks: {tid}")

async def periodic_cleanup_loop(page_pool, max_task_num, create_context_func):
    import asyncio
    while True:
        from utils.config import CLEANUP_INTERVAL_MINUTES
        await asyncio.sleep(CLEANUP_INTERVAL_MINUTES * 60)
        logger.info("Start cleaning the page cache and context one by one")
        total = max_task_num
        success = 0
        for _ in range(total):
            try:
                page, context = await page_pool.get()
                try:
                    await page.close()
                except:
                    pass
                try:
                    await context.close()
                except Exception as e:
                    logger.warning(f"Error cleaning page: {e}")
                context = await create_context_func()
                page = await context.new_page()
                await page_pool.put((page, context))
                success += 1
                await asyncio.sleep(1.5)
            except Exception as e:
                logger.warning(f"Failed to clean and rebuild the page: {e}")
                continue
        logger.success(f"Regular cleaning is completed, a total of {success}/{total} Pages")
