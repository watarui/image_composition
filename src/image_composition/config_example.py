class Development:
    """
    開発環境の設定
    """

    # Flask
    DEBUG = True

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{user}:{password}@{host}/{database}?charset=utf8".format(
        **{
            "user": "root",
            "password": "",
            "host": "localhost",
            "database": "image_composition",
        }
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # token
    SECRET_KEY = "secret"
    # sec
    EXPIRES_IN = 60 * 1


Config = Development
