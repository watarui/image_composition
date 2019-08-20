import os
import re
from functools import reduce
from pathlib import Path
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, ValidationError
from .controller import ImageEditor

app = Flask(__name__)
csrf = CSRFProtect(app)
app.config.from_object("src.image_composition.config.Config")


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


class Form(FlaskForm):
    firstname = StringField("firstname")
    lastname = StringField("lastname")

    def validate_firstname(self, firstname):
        if firstname.data == "":
            raise ValidationError("名前を入力してください")
        if len(firstname.data) > 10:
            raise ValidationError("10文字以内で入力してください")
        if not re.match("^[A-Z]+$", firstname.data):
            raise ValidationError("半角アルファベット（大文字）で入力してください")

    def validate_lastname(self, lastname):
        if lastname.data == "":
            raise ValidationError("名前を入力してください")
        if len(lastname.data) > 10:
            raise ValidationError("10文字以内で入力してください")
        if not re.match("^[A-Z]+$", lastname.data):
            raise ValidationError("半角アルファベット（大文字）で入力してください")


@app.route("/")
def index():
    form = Form(request.form)
    return render_template("index.html", form=form)


@app.route("/result", methods=["GET", "POST"])
@app.route("/result/<token>", methods=["GET", "POST"])
def result(token=None):
    # /result への初回POST時
    if not token and request.method == "POST":
        form = Form(request.form)
        if form.validate_on_submit():
            # token 生成
            s = Serializer(app.config["SECRET_KEY"], app.config["EXPIRES_IN"])
            token = s.dumps({}).decode("utf-8")
            # フォーム入力値の取得
            firstname = form.firstname.data
            lastname = form.lastname.data
            scene = request.form["scene"]

            generate(firstname, lastname, scene, token)

            return redirect(url_for("result", token=token))
        return render_template("index.html", form=form)

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
