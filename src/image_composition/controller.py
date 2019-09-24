import os
import shutil
from datetime import datetime, timedelta
from functools import reduce
from typing import List, Tuple, Union
from PIL import Image
from apscheduler.schedulers.background import BackgroundScheduler


class ImageEditor:
    def is_Image(self, obj: object) -> bool:
        return type(obj) == Image.Image

    def open(self, img: str) -> Image.Image:
        if self.is_Image(img):
            return img
        return Image.open(img).copy()

    def composite(
        self,
        fg: Union[Image.Image, str],
        bg: Union[Image.Image, str],
        dst: str,
        n: Union[int, float] = 1,
        padding_y: int = 0,
        padding_x: int = 0,
        offset_y: int = 0,
    ) -> None:
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

        def fit(
            fw: Union[int, float],
            fh: Union[int, float],
            bw: Union[int, float],
            bh: Union[int, float],
        ) -> Tuple[int, int]:
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

    def __concat_fonts(self, f1: str, f2: str, ol: int) -> Image.Image:
        a = self.open(f1)
        b = self.open(f2)
        aw, ah = a.size
        bw, bh = b.size

        # 重ね合わせの分だけ、幅を小さくする
        # aw = aw - ol

        # 結合後の画像は余白が透明のものを用意
        img = Image.new("RGBA", (aw + bw, max(ah, bh)), (255, 255, 255, 0))

        # 下揃え
        if a.height >= b.height:
            img.paste(a, (0, 0), a)
            img.paste(b, (aw, ah - bh), b)
        else:
            img.paste(a, (0, bh - ah), a)
            img.paste(b, (aw, 0), b)

        return img

    def concat_fonts(self, fonts: List[str], overlap: int = 0) -> Image.Image:
        """
        引数で渡された画像を順に合成していき、最終的に合成された画像オブジェクトを返す。

        Parameters
        ----------
        fonts : list of str
            合成する画像ファイルのパスのリスト
        overlap : int
            隣り合う画像ファイルの重なり
        """
        return reduce(lambda a, b: self.__concat_fonts(a, b, overlap), fonts)


class ImageRemover:
    """
    画像削除スケジューラ
    """

    def __init__(
        self,
        img: str,
        expires_in: int = 60,
        date: datetime = datetime.now(),
        dst: str = os.sep + "tmp",
    ):
        self.img = img
        self.expires_in = expires_in
        self.date = date
        self.dst = dst

    def __rm(self) -> None:
        shutil.move(self.img, self.dst)

    def start(self) -> None:
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            self.__rm, "date", run_date=self.date + timedelta(seconds=self.expires_in)
        )
        scheduler.start()
