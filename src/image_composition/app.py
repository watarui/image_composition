import os
from functools import reduce
from pathlib import Path
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import Flask, render_template, request, redirect, url_for
from .controller import ImageEditor
from .database import init_db
from .models.models import Alphabet, Scene

app = Flask(__name__)
app.config.from_object("src.image_composition.config.Config")


init_db(app)


def generate(firstname, lastname, scene, output_filename="out"):
    """
    画像を合成し、出力先のファイルパスを返す。
    """

    def make_path(lst, acc=os.sep):
        return reduce(lambda x, y: x + os.sep + y, lst, acc)

    parent_path = str(Path(__file__).resolve().parents[0])

    def get_font_img(font):
        return make_path(
            [
                "resources",
                ("lower" if font.islower() else "upper") + "case_letters",
                font + ".png",
            ],
            parent_path,
        )

    firstnames = [get_font_img(f) for f in list(firstname)]
    lastnames = [get_font_img(f) for f in list(lastname)]
    bg = make_path(["resources", "scenes", scene + ".jpg"], parent_path)
    dst = make_path(["static", "img", "tmp", output_filename + ".png"], parent_path)

    im = ImageEditor()
    fg = im.concat_fonts(firstnames + lastnames)
    im.composite(fg, bg, dst)

    return dst


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/result", methods=["GET", "POST"])
@app.route("/result/<token>", methods=["GET", "POST"])
def result(token=None):
    # /result への初回POST時
    if not token and request.method == "POST":
        # token 生成
        s = Serializer(app.config["SECRET_KEY"], app.config["EXPIRES_IN"])
        token = s.dumps({}).decode("utf-8")
        # フォーム入力値の取得
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        scene = request.form["scene"]
        # TODO: Add validations
        generate(firstname, lastname, scene, token)

        return redirect(url_for("result", token=token))

    if not token and request.method == "GET":
        return redirect(url_for("index"))

    # token がある場合
    s = Serializer(app.config["SECRET_KEY"])
    try:
        s.loads(token.encode("utf-8"))
    except Exception:
        # URL が期限切れの場合
        return redirect(url_for("index"))
    return render_template("result.html", filename=token)


if __name__ == "__main__":
    app.run(debug=True)
