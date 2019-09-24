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

    def composite(
        self,
        fg,
        bg,
        dst,
        n=1,
        padding_y: int = 0,
        padding_x: int = 0,
        offset_y: int = 0,
    ):
        """
        画像を合成出力する。
        """
        b = Image.open(bg).copy().convert("RGBA")
        f = self.open(fg)
        bw, bh = b.size
        fw, fh = f.size

        # 背景の高さをn倍と見積もることで、
        # 前景の高さをn倍に縮小する
        bh = bh * n

        def fit(fw, fh, bw, bh):
            """
            背景にフィットするような前景のサイズを整数のタプルで返す。
            """
            # 背景に対する前景の比率
            pw, ph = fw / bw, fh / bh
            # 比率の大きな方、
            # つまり前景と背景との間に余裕のない側を基準として補正
            # もとの前景が背景より小さい場合は背景サイズを維持
            if pw < 1 and (ph * n) < 1:
                w, h = bw, bh
            elif pw <= (ph * n):
                w, h = fw / ph, bh
            else:
                w, h = bw, fh / pw
            return int(w) - padding_x, int(h) - padding_y

        # 前景をリサイズ
        f = f.resize(fit(fw, fh, bw, bh))

        # 背景に対する前景の基点（原点座標は左上端）
        base = (
            # 横は中央に配置
            int((bw - f.width) / 2),
            # 縦は中央よりoffset_yだけ上に配置
            int((((bh / n) - f.height) / 2) - offset_y),
        )

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
