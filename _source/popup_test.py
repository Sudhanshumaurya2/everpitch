import asyncio
from playwright.async_api import async_playwright
B="http://127.0.0.1:8765"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for vp,tag in [((1366,860),"desktop"),((390,700),"mobile")]:
            ctx = await b.new_context(viewport={"width":vp[0],"height":vp[1]})
            pg = await ctx.new_page()
            await pg.goto(B+"/benefits.html", wait_until="load")
            await pg.wait_for_timeout(4000)
            print(tag, "modal visible @4s:", await pg.is_visible("#ep-modal"))
            await pg.wait_for_timeout(3000)
            vis = await pg.is_visible("#ep-modal.show")
            print(tag, "modal visible @7s:", vis, "| body locked:", await pg.evaluate("document.body.classList.contains('modal-open')"),
                  "| overlay bg:", await pg.evaluate("getComputedStyle(document.getElementById('ep-modal')).backgroundColor"))
            box = await pg.locator("#ep-modal .box").bounding_box()
            print(tag, "box fits viewport:", box["y"] >= 0 and box["y"]+box["height"] <= vp[1], "| focused:", await pg.evaluate("document.activeElement.className"))
            print(tag, "cta href:", await pg.get_attribute("#ep-modal a.btn", "href"), "| price text:", (await pg.inner_text("#ep-modal .mprice")).replace("\n"," "))
            await pg.screenshot(path=f"/tmp/modal-{tag}.png")
            await pg.keyboard.press("Escape"); await pg.wait_for_timeout(500)
            print(tag, "after Esc visible:", await pg.is_visible("#ep-modal.show"), "| scroll unlocked:", not await pg.evaluate("document.body.classList.contains('modal-open')"))
            await pg.reload(wait_until="load"); await pg.wait_for_timeout(8000)
            print(tag, "after reload (cooldown) modal shown:", await pg.is_visible("#ep-modal.show"))
            # toast: shows ~5s after load when modal is in cooldown
            await pg.reload(wait_until="load"); await pg.wait_for_timeout(5600)
            print(tag, "toast shown @5.6s:", await pg.is_visible("#ep-toast.show"), "|", (await pg.inner_text("#ep-toast b")))
            await pg.screenshot(path=f"/tmp/toast-{tag}.png")
            await pg.wait_for_timeout(6500)
            print(tag, "toast hidden after ~6s:", not await pg.is_visible("#ep-toast.show"))
            await ctx.close()
        # outside click + close button
        ctx = await b.new_context(viewport={"width":1366,"height":860}); pg = await ctx.new_page()
        await pg.goto(B+"/faq.html"); await pg.wait_for_timeout(7000)
        await pg.mouse.click(30, 400); await pg.wait_for_timeout(500)
        print("outside click closes:", not await pg.is_visible("#ep-modal.show"))
        await pg.evaluate("localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(7000)
        await pg.click("#ep-modal .x"); await pg.wait_for_timeout(500)
        print("X button closes:", not await pg.is_visible("#ep-modal.show"))
        # order page has no promo
        await pg.evaluate("localStorage.clear()"); await pg.goto(B+"/order?package=bundle"); await pg.wait_for_timeout(7000)
        print("order page modal:", await pg.is_visible("#ep-modal.show"))
        # reduced motion
        rc = await b.new_context(reduced_motion="reduce"); rp = await rc.new_page(); await rp.goto(B+"/"); await rp.wait_for_timeout(300)
        print("reduced motion: product animation =", await rp.evaluate("getComputedStyle(document.querySelector('.product img')).animationName"))
        await b.close()
asyncio.run(main())
