from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
chrome=next(Path('/Users/mohammed/.cache/hyperframes/chrome/chrome-headless-shell').glob('*/chrome-headless-shell-mac-arm64/chrome-headless-shell'))
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=str(chrome),headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    for name,count in [('fundamentals',24),('deep',28),('mic',20),('table41',45)]:
        page.goto('http://127.0.0.1:8765/?test='+name)
        page.wait_for_selector('.option')
        assert page.locator('.nav-item').count()==count
        assert page.locator('#test-set').input_value()==name
        assert not page.locator('#results').is_visible()
        rows=json.loads((ROOT/'practice'/f'questions-{name}.json').read_text())
        for i,row in enumerate(rows):
            page.locator('.nav-item').nth(i).click()
            assert page.locator('#stem').inner_text()==row['stem']
            assert page.locator('.option').count()==len(row['options'])
            page.locator(f'input[value="{row["gold"]}"]').check()
        page.once('dialog',lambda d:d.accept());page.locator('#finish').click()
        assert page.locator('#score').inner_text().startswith(f'{count} / {count}')
        assert page.locator('.review-item').count()==count
        assert 'Référence du corpus' in page.locator('#review').inner_text()
        page.locator('#again').click()
        page.locator('input[value="1"]').check()
        page.reload();page.wait_for_selector('.option');assert page.locator('input[value="1"]').is_checked()
        page.set_viewport_size({'width':390,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        page.set_viewport_size({'width':1440,'height':1000})
    page.locator('#test-set').select_option('fundamentals');page.wait_for_url('**test=fundamentals');page.wait_for_selector('.option')
    assert page.locator('.nav-item').count()==24
    assert page.locator('input[value="1"]').is_checked()
    assert not errors,errors
    page.screenshot(path=str(ROOT/'research/practice-added-tests.png'),full_page=True)
    browser.close()
print('All four added tests: all 117 questions navigable, scoring/corrections, persistence, switching and mobile layout passed.')
