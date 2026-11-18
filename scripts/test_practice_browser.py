from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
chrome = next(
    Path("/Users/mohammed/.cache/hyperframes/chrome/chrome-headless-shell").glob(
        "*/chrome-headless-shell-mac-arm64/chrome-headless-shell"
    )
)
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=str(chrome), headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto("http://127.0.0.1:8765/")
    page.wait_for_selector(".option")
    assert page.locator(".nav-item").count() == 29
    page.screenshot(path=str(ROOT / "research/practice-preview.png"), full_page=True)
    page.set_viewport_size({"width": 1280, "height": 720})
    assert (
        page.locator("#next").bounding_box()["y"]
        + page.locator("#next").bounding_box()["height"]
        <= 720
    )
    page.screenshot(path=str(ROOT / "research/practice-laptop.png"), full_page=True)
    page.set_viewport_size({"width": 1440, "height": 1000})
    page.locator("#question-card").screenshot(
        path=str(ROOT / "research/practice-question.png")
    )
    page.locator('input[value="0"]').check()
    assert page.locator("#answer-status").inner_text() == "Réponse enregistrée"
    page.locator("#next").click()
    page.locator('input[value="1"]').check()
    page.locator("#flag").click()
    page.reload()
    page.wait_for_selector(".option")
    assert page.locator('input[value="1"]').is_checked()
    assert page.locator("#flag").get_attribute("aria-pressed") == "true"
    page.locator("#previous").click()
    assert page.locator('input[value="0"]').is_checked()
    page.locator("#clear").click()
    assert page.locator("input:checked").count() == 0
    page.locator(".nav-item").nth(2).click()
    page.locator('input[value="2"]').check()
    page.once("dialog", lambda d: d.accept())
    page.locator("#finish").click()
    assert page.locator("#results").is_visible()
    assert page.locator(".review-item").count() == 29
    assert page.locator("#score").inner_text().startswith("1 / 29")
    page.reload()
    page.wait_for_selector(".review-item")
    assert page.locator("#results").is_visible()
    page.locator("#again").click()
    assert page.locator("input:checked").count() == 0
    page.locator("#duration").select_option("0")
    assert page.locator("#timer").inner_text() == "Sans limite"
    page.locator("#help-toggle").click()
    assert page.locator("#help").is_visible()
    page.evaluate(
        "let s=JSON.parse(localStorage.getItem('beru-practice-v1'));s.deadline=Date.now()-5000;s.finished=false;localStorage.setItem('beru-practice-v1',JSON.stringify(s))"
    )
    page.reload()
    page.wait_for_selector(".review-item")
    assert page.locator("#results").is_visible()
    page.locator("#again").click()
    page.set_viewport_size({"width": 390, "height": 844})
    page.screenshot(path=str(ROOT / "research/practice-mobile.png"), full_page=True)
    assert page.evaluate("document.documentElement.scrollWidth<=window.innerWidth")
    assert page.request.get("http://127.0.0.1:8765/API.env").status == 404
    assert (
        page.request.get("http://127.0.0.1:8765/healthz").json()["app"]
        == "beru-practice"
    )
    assert not errors, errors
    browser.close()
    print(
        "Browser checks passed: answer/clear/navigation/flags/persistence/scoring/restart/timer/mobile/server isolation"
    )
