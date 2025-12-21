
# caches

## Overview

![](https://img.shields.io/badge/Python-3.12-blue)
![](https://img.shields.io/badge/License-AGPLv3-blue)

キャッシュ機能を提供します。

キャッシュ機能を提供する専用のオブジェクトを作成し、そのオブジェクトから値を取り出す方式になっています(使用者は取り出された値がキャッシュ済みなのか、新たに計算された値なのかを知ることは出来ない)
専用のオブジェクトは作成時に「キャッシュ検索用のキーを計算する関数」と「キャッシュされる値を計算する関数」の2つの関数を受け取ります。

## Usage

ユーザ定義キャッシュを作成する実行例

```py
import random
from caches import Caches

c = Caches(3, calc_value_func=lambda args, kwargs: random.randint(args[0], args[1]))
c.get((1, 3)) #2
c.get((1, 3)) #2
c.get((1, 3)) #2
```

ファイル読み込み向けのキャッシュを作成する実行例

```py
import caches 

with open("sample.txt", "w") as file:
  file.write("abc")

c = caches.file_caches(3)
c.get(("sample.txt", "r")) #abc
c.get(("sample.txt", "r")) #abc
c.get(("sample.txt", "r")) #abc
```

JSON読み込み向けのキャッシュを作成する実行例

```py
import json
import caches 

with open("sample.json", "w") as file:
  json.dump(["a", "b", "c"], file)

c = caches.file_caches(3)
c.get(("sample.json",)) #["a", "b", "c"]
c.get(("sample.json",)) #["a", "b", "c"]
c.get(("sample.json",)) #["a", "b", "c"]
```

## Install

```shell
pip install .
```

### Test

```shell
pip install .[test]
pytest .
```

### Document

```py
import caches

help(caches)
```

## Donation

<a href="https://buymeacoffee.com/tikubonn" target="_blank"><img src="doc/img/qr-code.png" width="3000px" height="3000px" style="width:150px;height:auto;"></a>

もし本パッケージがお役立ちになりましたら、少額の寄付で支援することができます。<br>
寄付していただいたお金は書籍の購入費用や日々の支払いに使わせていただきます。
ただし、これは寄付の多寡によって継続的な開発やサポートを保証するものではありません。ご留意ください。

If you found this package useful, you can support it with a small donation.
Donations will be used to cover book purchases and daily expenses.
However, please note that this does not guarantee ongoing development or support based on the amount donated.

## License

© 2025 tikubonn

caches licensed under the [AGPLv3](./LICENSE).
