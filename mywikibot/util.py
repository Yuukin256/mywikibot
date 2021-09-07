import pywikibot


def make_botreq_summary(site: pywikibot.APISite, section_name: str, content: str):
    if not site:
        site = pywikibot.Site("ja", "wikipedia")
    if not section_name:
        section_name = pywikibot.input("Bot作業依頼のセクション名を入力してください")
    if not content:
        content = pywikibot.input("要約欄に表示する作業内容を入力してください")

    page = pywikibot.Page(site, "Wikipedia:Bot作業依頼")
    oldid = page.latest_revision_id
    return f"Botによる: [[Special:Permalink/{oldid}#{section_name}|Bot作業依頼]] {content}"
