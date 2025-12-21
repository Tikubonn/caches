
import json
from typing import Callable, Hashable, Any
from pathlib import Path
from collections import OrderedDict

def dict_to_hashable (d:dict) -> tuple[tuple[Hashable, Hashable], ...]:
  return tuple(((k, d[k]) for k in sorted(d.keys())))

class Caches:

  """キャッシュ機能を提供します。

  Examples
  --------
  >>> import random
  >>> c = Caches(3, calc_key_value=lambda args, kwargs: random.randint(args[0], args[1]))
  >>> c.get((1, 2))
  2
  >>> c.get((1, 2))
  2
  >>> c.get((1, 2))
  2
  """

  def __init__ (self, max_cache_count:int, *, calc_value_func:Callable[[tuple[Any, ...], dict], Any], calc_key_func:Callable[[tuple[Any, ...], dict], tuple[tuple[Any, ...], Hashable]]|None=None):

    """インスタンスの初期化を行います。

    Parameters
    ----------
    max_cache_count : int
      インスタンスが保持することができる最大キャッシュ数です。
    calc_value_func : Callable[[tuple[Any, ...], dict], Any]
      未キャッシュの値を要求された際に新しい値を計算するために用いられる関数です。
    calc_key_func : Callable[[tuple[Any, ...], dict], tuple[tuple[Any, ...], Hashable]]|None
      与えられた引数から、キャッシュ保存先を決定するために用いられる、ハッシュ可能な値を計算する関数です。
      未指定の場合には `None` が使用されます。
    """

    self.max_cache_count = max_cache_count
    self._calc_value_func = calc_value_func
    self._calc_key_func = calc_key_func
    self._cached_values = OrderedDict()

  def clear (self):

    """インスタンスに記録されたキャッシュを全て破棄します。"""

    self._cached_values.clear()

  def get (self, args:tuple[Any, ...]=(), kwargs:dict={}) -> Any:

    """引数に基づいてキャッシュを検索し、キャッシュ済みあるいは新たに計算された値を返します。

    Notes
    -----
    引数に該当するキャッシュが存在しなければ、コンストラクタで指定された関数を用いて新たな値を計算し、キャッシュに記録します。
    この時、保存されたキャッシュ数が最大値を超過していれば、その分だけ古いキャッシュを破棄します。

    Parameters
    ----------
    args : tuple[Any, ...]
      キャッシュの検索と再計算に用いられる引数の組です。
    kwargs : dict
      キャッシュの検索と再計算に用いられるキーワード引数の集合です。

    Returns
    -------
    Any
      キャッシュ済みあるいは新たに計算された値です。
    """

    if self._calc_key_func:
      key = self._calc_key_func(args, kwargs)
    else:
      key = args, dict_to_hashable(kwargs)
    if key in self._cached_values:
      value = self._cached_values[key]
      self._cached_values.move_to_end(key, last=False)
    else:
      value = self._calc_value_func(args, kwargs)
      self._cached_values[key] = value
      self._cached_values.move_to_end(key, last=False)
    while len(self._cached_values) > max(0, self.max_cache_count):
      self._cached_values.popitem()
    return value

def file_caches (max_cache_count:int) -> Caches:

  """ファイル読み込み向けに設定された `Caches` インスタンスを作成します。

  Notes
  -----
  読み込み先のファイルが更新されると、次回の `.get` メソッド実行時に再読み込みされます。
  ファイル更新の有無の判定には `os.stat` 関数が用いられています。

  Examples
  --------
  >>> import caches
  >>> fc = caches.file_caches(3)
  >>> fc.get(("anything.txt", "r"))
  >>> fc.get(("anything.txt", "r"), {"encoding": "utf-8"})

  Parameters
  ----------
  max_cache_count : int
    `Caches` インスタンスが保持することができる最大キャッシュ数です。
  
  Returns
  -------
  Caches
    ファイル読み込み向けに設定された `Caches` インスタンスです。
    返されたインスタンスの `.get` メソッドの `args` 引数にはファイルパスとモード文字列を指定します。
    返されたインスタンスの `.get` メソッドの `kwargs` 引数には `open` 関数に与える追加の引数を指定します。
  """

  def calc_key_func (args:tuple[Path|str, str], kwargs:dict) -> tuple[tuple[Hashable, ...], Hashable]:
    path, mode = args
    st = Path(path).stat()
    return (Path(path), mode, (st.st_ctime, st.st_mtime)), dict_to_hashable(kwargs)

  def calc_value_func (args:tuple[Path|str, str], kwargs:dict) -> str|bytes:
    path, mode = args
    if mode in {"r", "rb"}:
      with open(path, mode, **kwargs) as file:
        return file.read()
    else:
      raise ValueError()

  return Caches(
    max_cache_count,
    calc_key_func=calc_key_func,
    calc_value_func=calc_value_func
  )

def json_caches (max_cache_count:int) -> Caches:

  """JSON読み込み向けに設定された `Caches` インスタンスを作成します。

  Notes
  -----
  読み込み先のファイルが更新されると、次回の `.get` メソッド実行時に再読み込みされます。
  ファイル更新の有無の判定には `os.stat` 関数が用いられています。

  Examples
  --------
  >>> import caches
  >>> fc = caches.file_caches(3)
  >>> fc.get(("anything.txt",))
  >>> fc.get(("anything.txt",), {"encoding": "utf-8"})

  Parameters
  ----------
  max_cache_count : int
    `Caches` インスタンスが保持することができる最大キャッシュ数です。
  
  Returns
  -------
  Caches
    JSON読み込み向けに設定された `Caches` インスタンスです。
    返されたインスタンスの `.get` メソッドの `args` 引数にはファイルパスを指定します。
    返されたインスタンスの `.get` メソッドの `kwargs` 引数には `open` 関数に与える追加の引数を指定します。
  """

  def calc_key_func (args:tuple[Path|str], kwargs:dict) -> tuple[tuple[Hashable, ...], Hashable]:
    path, = args
    st = Path(path).stat()
    return (Path(path), (st.st_ctime, st.st_mtime)), dict_to_hashable(kwargs)

  def calc_value_func (args:tuple[Path|str], kwargs:dict) -> Any:
    path, = args
    with open(path, "r", **kwargs) as file:
      return json.load(file)

  return Caches(
    max_cache_count,
    calc_key_func=calc_key_func,
    calc_value_func=calc_value_func
  )
