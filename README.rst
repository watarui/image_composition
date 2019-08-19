初期設定
========

.. code-block:: sh

    git clone URL@image_composition.git
    cd image_composition

エディタ設定
============

.. code-block:: sh

    # For VSCode
    cp .vscode/launch_example.json .vscode/launch.json
    cp .vscode/settings_example.json .vscode/setting.json
    code --install-extension EditorConfig.EditorConfig
    code --install-extension ms-python.python

pyenv
=====

.. code-block:: sh

    pyenv install --list | grep "  3"
    pyenv install 3.7.3
    pyenv local 3.7.3

poetry
======

.. code-block:: sh

    poetry install

仮想環境のアクティベート
========================

.. code-block:: sh

    source ./.venv/bin/activate

Flask
=====

.. code-block:: sh

    export FLASK_APP="./src/image_composition/app.py"
    flask run --reload

    # app.run(debug=True) が効かない場合
    export FLASK_DEBUG=1
