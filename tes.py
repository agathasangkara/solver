import sys
import time
import webbrowser
import threading
import subprocess
import requests
from utils.config import HOST, PORT
from utils.logger import logger

BASE_URL = f"http://{HOST}:{PORT}"
DOC_URL = f"{BASE_URL}/static/doc.html"
HEALTH_TIMEOUT = 30
POLL_INTERVAL = 0.5

def wait_for_server():
    logger.info(f"Waiting for server at {BASE_URL} ...")
    start = time.time()
    while time.time() - start < HEALTH_TIMEOUT:
        try:
            r = requests.get(f"{BASE_URL}/result?id=test", timeout=2)
            if r.status_code in (400, 404, 422):
                return True
        except requests.ConnectionError:
            pass
        except Exception:
            pass
        time.sleep(POLL_INTERVAL)
    return False

def test_turnstile():
    logger.info("=== Test: Turnstile ===")
    r = requests.get(f"{BASE_URL}/turnstile", params={
        "url": "https://turnstiledemo.lusostreams.com",
        "sitekey": "0x4AAAAAAA48lYLAs6wu2g30"
    })
    logger.info(f"[Turnstile] Status: {r.status_code} | Body: {r.json()}")
    assert r.status_code == 202
    task_id = r.json().get("task_id")
    assert task_id
    logger.info(f"[Turnstile] task_id: {task_id}")
    return task_id

def test_recaptcha_v3():
    logger.info("=== Test: reCAPTCHA v3 ===")
    r = requests.get(f"{BASE_URL}/recaptchav3", params={
        "url": "https://example.com",
        "sitekey": "6LeXXXXXXX-YYYYYYYa",
        "action": "login",
        "min_score": 0.7
    })
    logger.info(f"[reCAPTCHA v3] Status: {r.status_code} | Body: {r.json()}")
    assert r.status_code == 202
    return r.json().get("task_id")

def test_recaptcha_v3_enterprise():
    logger.info("=== Test: reCAPTCHA v3 Enterprise ===")
    r = requests.get(f"{BASE_URL}/recaptchav3enterprise", params={
        "url": "https://example.com",
        "sitekey": "6LeENT_XXXXX_YYY",
        "action": "signup",
        "min_score": 0.5
    })
    logger.info(f"[reCAPTCHA v3 Enterprise] Status: {r.status_code} | Body: {r.json()}")
    assert r.status_code == 202
    return r.json().get("task_id")

def test_recaptcha_v2():
    logger.info("=== Test: reCAPTCHA v2 ===")
    r = requests.get(f"{BASE_URL}/recaptchav2", params={
        "url": "https://example.com",
        "sitekey": "6LeXXXXXXX-YYYYYYYa"
    })
    logger.info(f"[reCAPTCHA v2] Status: {r.status_code} | Body: {r.json()}")
    assert r.status_code == 202
    return r.json().get("task_id")

def test_recaptcha_v2_invisible():
    logger.info("=== Test: reCAPTCHA v2 Invisible ===")
    r = requests.get(f"{BASE_URL}/recaptchav2invisible", params={
        "url": "https://example.com",
        "sitekey": "6LeINV_XXXXX_YYY"
    })
    logger.info(f"[reCAPTCHA v2 Invisible] Status: {r.status_code} | Body: {r.json()}")
    assert r.status_code == 202
    return r.json().get("task_id")

def test_recaptcha_v2_enterprise():
    logger.info("=== Test: reCAPTCHA v2 Enterprise ===")
    r = requests.get(f"{BASE_URL}/recaptchav2enterprise", params={
        "url": "https://example.com",
        "sitekey": "6LeENT2_XXXXX_YYY"
    })
    logger.info(f"[reCAPTCHA v2 Enterprise] Status: {r.status_code} | Body: {r.json()}")
    assert r.status_code == 202
    return r.json().get("task_id")

def test_get_result(task_id):
    logger.info(f"=== Test: Get Result for {task_id} ===")
    r = requests.get(f"{BASE_URL}/result", params={"id": task_id})
    logger.info(f"[Result] Status: {r.status_code} | Body: {r.json()}")
    return r

def test_missing_params():
    logger.info("=== Test: Missing Params ===")
    r = requests.get(f"{BASE_URL}/recaptchav3", params={"url": "https://example.com"})
    logger.info(f"[Missing Params] Status: {r.status_code}")
    assert r.status_code in (400, 422)

    r2 = requests.get(f"{BASE_URL}/turnstile")
    logger.info(f"[Missing Params Turnstile] Status: {r2.status_code}")
    assert r2.status_code in (400, 422)

def test_invalid_task_id():
    logger.info("=== Test: Invalid Task ID ===")
    r = requests.get(f"{BASE_URL}/result", params={"id": "nonexistent-id-12345"})
    logger.info(f"[Invalid ID] Status: {r.status_code} | Body: {r.json()}")
    assert r.status_code == 404

def poll_result(task_id, timeout=15):
    logger.info(f"Polling result for {task_id} ...")
    start = time.time()
    while time.time() - start < timeout:
        r = requests.get(f"{BASE_URL}/result", params={"id": task_id})
        data = r.json()
        if data.get("status") != "process":
            logger.info(f"[Poll Result] Final: {r.status_code} | {data}")
            return data
        time.sleep(1)
    logger.warning(f"[Poll Result] Timeout polling {task_id}")
    return None

def run_all_tests():
    logger.info("=" * 60)
    logger.info("CAPTCHA Solver API - Test Suite")
    logger.info("=" * 60)

    test_missing_params()
    test_invalid_task_id()

    tid_turnstile = test_turnstile()
    test_get_result(tid_turnstile)
    time.sleep(2)
    poll_result(tid_turnstile, timeout=10)

    logger.success("=" * 60)
    logger.success("tests completed!")
    logger.success("=" * 60)

def start_server_process():
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", HOST, "--port", str(PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

def main():
    logger.info("Starting server process...")
    proc = start_server_process()

    try:
        if not wait_for_server():
            logger.error("Server failed to start within timeout!")
            proc.terminate()
            sys.exit(1)

        logger.success(f"Server is running at {BASE_URL}")

        logger.info(f"Opening API documentation: {DOC_URL}")
        webbrowser.open(DOC_URL)

        time.sleep(1)

        run_all_tests()

        logger.info("Press Ctrl+C to stop the server...")
        proc.wait()

    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        proc.terminate()
        proc.wait()
        logger.success("Server stopped.")
    except Exception as e:
        logger.error(f"Test error: {e}")
        proc.terminate()
        proc.wait()
        sys.exit(1)

if __name__ == "__main__":
    main()