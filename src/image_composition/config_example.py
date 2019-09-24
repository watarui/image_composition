class Development:
    """
    開発環境の設定
    """

    # Flask
    DEBUG = True

    # token
    SECRET_KEY = "secret"
    # sec
    EXPIRES_IN = 60 * 1

    # 前景拡大率
    FRONT_IMG_N = 1 / 3

    # 背景を外枠としたときの前景のパディング
    FRONT_IMG_PADDING_X = 300
    FRONT_IMG_PADDING_Y = 0

    # 前景の高さ方向の背景中心からのズレ（基準は前景下辺）
    FRONT_IMG_OFFSET_Y = 400

    # フォントの重なり具合
    FONTS_OVERLAP = 300


Config = Development
