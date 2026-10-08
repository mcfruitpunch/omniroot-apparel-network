from pathlib import Path
import os
from playwright.sync_api import sync_playwright

root = Path(__file__).parent
errors = []
html = (root / "index.html").read_text(encoding="utf-8")

with sync_playwright() as p:
    chromium_path = os.getenv("CHROMIUM_PATH", "/usr/bin/chromium")
    launch = dict(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
    if Path(chromium_path).exists():
        launch["executable_path"] = chromium_path
    browser = p.chromium.launch(**launch)

    page = browser.new_page(viewport={"width": 1400, "height": 900}, accept_downloads=True)
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.set_content(html, wait_until="load")
    assert page.get_by_text("Your body.", exact=False).count() > 0
    page.get_by_role("button", name="Shop + customize").click()
    assert page.get_by_text("Everyday overshirt").count() > 0
    page.locator("#fabric").select_option("linen")
    assert page.get_by_text("Linen blend").count() > 0
    page.get_by_role("button", name="Submit demo order").click()
    assert page.get_by_text("Your Fit Passport belongs to you.").count() > 0

    page.get_by_role("button", name="Load fictional sample").click()
    assert page.get_by_text("Validated for demo").count() > 0
    page.get_by_role("button", name="Shop + customize").click()
    page.locator("#fabric").select_option("linen")
    page.get_by_role("button", name="Submit demo order").click()
    assert page.get_by_text("OA-1001").count() > 0
    page.get_by_role("button", name="Maker Hub").click()
    assert page.get_by_text("Scoped measurement packet:").count() > 0
    assert page.get_by_text("adaptive", exact=False).count() == 0
    page.get_by_role("button", name="Accept simulated job").click()
    assert page.get_by_text("Accepted by maker").count() > 0

    page.get_by_role("button", name="Designer Studio").click()
    page.locator("#design-name").fill("Trailside Vest")
    page.locator("#design-desc").fill("A simple demo outer layer.")
    page.locator('input[name="rights"]').check()
    page.get_by_role("button", name="Submit for technical review").click()
    assert page.get_by_text("Trailside Vest").count() > 0
    page.get_by_role("button", name="Shop + customize").click()
    assert page.get_by_text("Trailside Vest").count() == 0
    page.get_by_role("button", name="Maker Hub").click()
    page.get_by_role("button", name="Mark sample approved (demo)").click()
    page.get_by_role("button", name="Shop + customize").click()
    assert page.get_by_text("Trailside Vest").count() > 0
    page.close()

    fresh = browser.new_page(viewport={"width": 1400, "height": 900})
    fresh.set_content(html, wait_until="load")
    fresh.get_by_role("button", name="Orders").click()
    assert fresh.get_by_text("No demo orders created yet.").count() > 0

    mobile = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, device_scale_factor=1)
    mobile.on("pageerror", lambda error: errors.append(str(error)))
    mobile.set_content(html, wait_until="load")
    mobile.get_by_role("button", name="Shop + customize").click()
    width = mobile.evaluate("document.documentElement.scrollWidth")
    assert width <= 400, f"mobile overflow: {width}"
    browser.close()

print("PASS: Fit Passport, sample order, maker stage, designer review, reset and mobile width")
print("Browser JS errors:", errors)
assert not errors
