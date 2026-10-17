"""Gabarito do exercício 6."""


def load_all(page, item_selector, more_selector, timeout_ms=3000):
    page.locator(item_selector).first.wait_for(timeout=timeout_ms)
    while page.locator(more_selector).count() > 0:
        before = page.locator(item_selector).count()
        page.locator(more_selector).click()
        page.wait_for_function("([sel, n]) => document.querySelectorAll(sel).length > n", arg=[item_selector, before], timeout=timeout_ms)
    return page.locator(item_selector).all_inner_texts()


def read_table(page, table_selector):
    rows = page.locator(f"{table_selector} tbody tr")
    try:
        rows.first.wait_for(timeout=3000)
    except Exception as error:
        raise ValueError("tabela vazia") from error
    headers = [h.strip() for h in page.locator(f"{table_selector} thead th").all_inner_texts()]
    return [dict(zip(headers, [c.strip() for c in row.locator("td").all_inner_texts()])) for row in rows.all()]


def fill_and_submit(page, values):
    for name, value in values.items():
        field = page.locator(f"[name={name}]")
        tag = field.evaluate("el => el.tagName.toLowerCase()")
        if tag == "select":
            field.select_option(value)
        else:
            field.fill(value)
    page.click("button[type=submit]")
    page.wait_for_load_state("load")
