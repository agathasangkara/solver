import time
import asyncio
from utils.logger import logger
from utils.templates import (
    HTML_TEMPLATE,
    RECAPTCHA_V3_TEMPLATE,
    RECAPTCHA_V2_TEMPLATE,
    RECAPTCHA_V2_INVISIBLE_TEMPLATE,
)

async def solve_turnstile(task_id, url, sitekey, action, cdata, results, page_pool, decrement_task):
    start_time = time.time()
    page, context = await page_pool.get()
    try:
        url_with_slash = url + "/" if not url.endswith("/") else url
        turnstile_div = (
            f'<div class="cf-turnstile" style="background: white;" data-sitekey="{sitekey}"'
            + (f' data-action="{action}"' if action else '')
            + (f' data-cdata="{cdata}"' if cdata else '')
            + '></div>'
        )
        page_data = HTML_TEMPLATE.replace("<!-- cf turnstile -->", turnstile_div)
        await page.route(url_with_slash, lambda route: route.fulfill(body=page_data, status=200))
        await page.goto(url_with_slash)
        await page.eval_on_selector("//div[@class='cf-turnstile']", "el => el.style.width = '70px'")

        for attempt in range(50):
            try:
                turnstile_check = await page.input_value("[name=cf-turnstile-response]", timeout=200)
                if turnstile_check == "":
                    await page.locator("//div[@class='cf-turnstile']").click(timeout=200)
                    await asyncio.sleep(0.1)
                else:
                    elapsed_time = round(time.time() - start_time, 3)
                    results[task_id] = {"status": "success", "elapsed_time": elapsed_time, "value": turnstile_check}
                    logger.info(f"Turnstile solved, task: {task_id}, time: {elapsed_time}s")
                    break
            except Exception as e:
                logger.debug(f"Turnstile attempt {attempt + 1} fail: {e}")
                await asyncio.sleep(0.05)

        if results.get(task_id, {}).get("status") != "success":
            elapsed_time = round(time.time() - start_time, 3)
            results[task_id] = {"status": "error", "elapsed_time": elapsed_time, "value": "turnstile_fail"}
            logger.warning(f"Turnstile failed, task: {task_id}, time: {elapsed_time}s")
    except Exception as e:
        elapsed_time = round(time.time() - start_time, 3)
        results[task_id] = {"status": "error", "elapsed_time": elapsed_time, "value": "turnstile_fail"}
        logger.error(f"Turnstile exception, task: {task_id}: {e}")
    finally:
        decrement_task()
        await page_pool.put((page, context))

async def solve_recaptcha_v3(task_id, url, sitekey, action, min_score, results, page_pool, decrement_task):
    start_time = time.time()
    page, context = await page_pool.get()
    try:
        url_with_slash = url + "/" if not url.endswith("/") else url
        page_data = RECAPTCHA_V3_TEMPLATE.format(sitekey=sitekey, action=action)
        await page.route(url_with_slash, lambda route: route.fulfill(body=page_data, status=200))
        await page.goto(url_with_slash)

        for attempt in range(50):
            try:
                token = await page.input_value("#recaptcha-token", timeout=200)
                if token:
                    elapsed_time = round(time.time() - start_time, 3)
                    results[task_id] = {
                        "status": "success",
                        "elapsed_time": elapsed_time,
                        "value": token,
                        "action": action,
                        "min_score": min_score
                    }
                    logger.info(f"reCAPTCHA v3 solved, task: {task_id}, time: {elapsed_time}s")
                    break
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.debug(f"reCAPTCHA v3 attempt {attempt + 1} fail: {e}")
                await asyncio.sleep(0.05)

        if results.get(task_id, {}).get("status") != "success":
            elapsed_time = round(time.time() - start_time, 3)
            results[task_id] = {"status": "error", "elapsed_time": elapsed_time, "value": "recaptcha_v3_fail"}
            logger.warning(f"reCAPTCHA v3 failed, task: {task_id}, time: {elapsed_time}s")
    except Exception as e:
        elapsed_time = round(time.time() - start_time, 3)
        results[task_id] = {"status": "error", "elapsed_time": elapsed_time, "value": "recaptcha_v3_fail"}
        logger.error(f"reCAPTCHA v3 exception, task: {task_id}: {e}")
    finally:
        decrement_task()
        await page_pool.put((page, context))

async def solve_recaptcha_v2(task_id, url, sitekey, invisible, results, page_pool, decrement_task):
    start_time = time.time()
    page, context = await page_pool.get()
    try:
        url_with_slash = url + "/" if not url.endswith("/") else url
        template = RECAPTCHA_V2_INVISIBLE_TEMPLATE if invisible else RECAPTCHA_V2_TEMPLATE
        page_data = template.format(sitekey=sitekey)
        await page.route(url_with_slash, lambda route: route.fulfill(body=page_data, status=200))
        await page.goto(url_with_slash)
        await asyncio.sleep(1)

        for attempt in range(80):
            try:
                token = await page.input_value("#recaptcha-response", timeout=300)
                if token:
                    elapsed_time = round(time.time() - start_time, 3)
                    results[task_id] = {"status": "success", "elapsed_time": elapsed_time, "value": token}
                    label = " Invisible" if invisible else ""
                    logger.info(f"reCAPTCHA v2{label} solved, task: {task_id}, time: {elapsed_time}s")
                    break

                if not invisible:
                    try:
                        checkbox = await page.query_selector("iframe[title*='reCAPTCHA']")
                        if checkbox:
                            frame = await checkbox.content_frame()
                            if frame:
                                await frame.click(".recaptcha-checkbox-border", timeout=300)
                                await asyncio.sleep(0.5)
                    except:
                        pass

                await asyncio.sleep(0.2)
            except Exception as e:
                logger.debug(f"reCAPTCHA v2 attempt {attempt + 1} fail: {e}")
                await asyncio.sleep(0.1)

        if results.get(task_id, {}).get("status") != "success":
            elapsed_time = round(time.time() - start_time, 3)
            results[task_id] = {"status": "error", "elapsed_time": elapsed_time, "value": "recaptcha_v2_fail"}
            logger.warning(f"reCAPTCHA v2 failed, task: {task_id}, time: {elapsed_time}s")
    except Exception as e:
        elapsed_time = round(time.time() - start_time, 3)
        results[task_id] = {"status": "error", "elapsed_time": elapsed_time, "value": "recaptcha_v2_fail"}
        logger.error(f"reCAPTCHA v2 exception, task: {task_id}: {e}")
    finally:
        decrement_task()
        await page_pool.put((page, context))