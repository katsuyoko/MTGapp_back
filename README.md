# MTGapp_back

## Setup

```
$ pip install -r requirements.txt
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py runserver
```

## Goolge APIs Console にて client_secret を発行

- [Goolge Developers Console](https://console.developers.google.com/apis/dashboard) にアクセス。
- 左上の▼で「**MTGapp**」プロジェクトを選択。
- 認証情報を作成。
    - **バックエンド → タイプ：その他**
    - フロントエンド → タイプ：ウェブアプリケーション

## credentials をセッション管理で保存している DB から削除

```
$ python manage.py shell
```

とすると、 ipython console みたいなのが起動するので、以下のコマンドを実行していく。

```py
from api import models

# 削除
models.Credentials.objects.all().delete()

# 確認
models.Credentials.objects.all().values()
```

もしくは、

```py
run clear_creds_in_db.py
```