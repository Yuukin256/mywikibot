import sys
from typing import Any, Optional, Union

import pywikibot
from pywikibot.bot import ExistingPageBot, SingleSiteBot, open_webbrowser
from pywikibot.editor import TextEditor


class ReplaceBot(ExistingPageBot, SingleSiteBot):

    """`treat_page()` の実装方法: `current_page` からページを取得し、変更内容は `put_current()` に投げる"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # skip_page() 以外でのスキップ数のカウンター
        self._notchange_counter = 0

    # ページの変更が保存された時に呼ばれるコールバック
    def _async_callback(self, page: pywikibot.Page, err: Union[Exception, None]) -> None:
        pass

    # 確認は userPut() で行われるためスルー
    def user_confirm(self, question):
        return True

    def userPut(self, page: pywikibot.Page, oldtext: str, newtext: str, **kwargs: Any) -> bool:
        summary = kwargs.pop("summary") if "summary" in kwargs else self.opt.summary
        context = 0

        while True:
            if oldtext == newtext:
                pywikibot.output(f"{page.title(as_link=True)} 変更なしのためスキップ")
                self._notchange_counter += 1
                return False

            pywikibot.showDiff(oldtext, newtext, context)
            pywikibot.output("要約: " + summary)

            if self.opt.always:
                page.text = newtext
                return self._save_page(
                    page, page.save, summary=summary, asynchronous=True, callback=self._async_callback, **kwargs
                )

            choice = pywikibot.input_choice(
                "この変更を投稿しますか",
                [
                    ("はい", "y"),
                    ("いいえ", "n"),
                    ("エディタで編集する", "e"),
                    ("前後を表示する", "m"),
                    ("ブラウザで表示", "b"),
                    ("自動保存する", "a"),
                    ("終了する", "q"),
                ],
            )

            if choice == "q":
                self.quit()

            if choice == "m":
                context = context * 3 if context else 1

            if choice == "b":
                open_webbrowser(page)

            if choice == "e":
                editor = TextEditor()
                as_edited = editor.edit(newtext)
                if as_edited and as_edited != oldtext:
                    newtext = as_edited

            if choice == "a":
                self.opt.always = True

            if choice == "y":
                page.text = newtext
                return self._save_page(
                    page, page.save, summary=summary, asynchronous=True, callback=self._async_callback, **kwargs
                )

            if choice == "n":
                self._notchange_counter += 1
                return False

    # 表示内容を変更したいためオーバーライド
    def exit(self) -> None:
        self.teardown()

        pywikibot.stopme()

        pywikibot.output(
            f"\n処理したページ数: {self._treat_counter}"
            f"\n変更したページ数: {self._save_counter}"
            f"\n変更しなかったページ数: {self._notchange_counter}"
            f"\nスキップしたページ数: {self._skip_counter}"
        )

        exc_info = sys.exc_info()
        if exc_info[0] is None or exc_info[0] is KeyboardInterrupt:
            pywikibot.output("スクリプトは正常に終了しました")
        else:
            pywikibot.output("スクリプトは例外により終了しました\n")
            pywikibot.exception()
