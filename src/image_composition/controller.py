import os
import shutil
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from functools import reduce
from PIL import Image


class ImageEditor:
    def is_Image(self, obj):
        return type(obj) == Image.Image

    def open(self, img):
        if self.is_Image(img):
            return img
        return Image.open(img).copy()

    def composite(self, fg, bg, dst):
        b = Image.open(bg).copy().convert("RGBA")
        f = self.open(fg)
        (x1, y1) = b.size
        (x2, y2) = f.size

        # 基点
        base = ((x1 - x2) // 2, (y1 - y2) // 2)

        # 前景が背景からはみ出ないように縮小
        # FIXME: はみ出しちゃうよ！
        f.thumbnail((x1, y1))

        b.paste(f, base, f)
        b.save(dst)

    def __concat_fonts(self, f1, f2):
        a = self.open(f1)
        b = self.open(f2)

        # 結合後の画像は余白が透明のものを用意
        img = Image.new(
            "RGBA", (a.width + b.width, max(a.height, b.height)), (255, 255, 255, 0)
        )

        # 下揃え
        # TODO: 小文字の場合は下揃えとは限らない
        if a.height >= b.height:
            img.paste(a, (0, 0))
            img.paste(b, (a.width, (a.height - b.height)))
        else:
            img.paste(a, (0, (b.height - a.height)))
            img.paste(b, (a.width, 0))

        return img

    def concat_fonts(self, fonts):
        return reduce(self.__concat_fonts, fonts)


class ImageRemover:
    """
    画像削除スケジューラ
    """

    def __init__(self, img, expires_in, date=datetime.now(), dst=os.sep + "tmp"):
        self.img = img
        self.expires_in = expires_in
        self.date = date
        self.dst = dst

    def __rm(self):
        shutil.move(self.img, self.dst)

    def start(self):
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            self.__rm, "date", run_date=self.date + timedelta(seconds=self.expires_in)
        )
        scheduler.start()
