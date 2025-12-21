
import caches
import pytest

def test_caches ():

  #calc_key_func が未指定の場合の動作確認

  recache_count = 0

  def calc_value_func (args:tuple[int, int], kwargs:dict[str, int]) -> int:
    nonlocal recache_count
    recache_count += 1
    a, b = args
    c = kwargs["c"]
    return a + b + c

  c = caches.Caches(3, calc_value_func=calc_value_func)

  #新規引数で呼び出します

  assert c.get((1, 2), {"c": 3}) == 6
  assert recache_count == 1
  assert c.get((2, 3), {"c": 4}) == 9
  assert recache_count == 2
  assert c.get((3, 4), {"c": 5}) == 12
  assert recache_count == 3

  #キャッシュ済み引数で呼び出します

  assert c.get((1, 2), {"c": 3}) == 6
  assert recache_count == 3
  assert c.get((2, 3), {"c": 4}) == 9
  assert recache_count == 3
  assert c.get((3, 4), {"c": 5}) == 12
  assert recache_count == 3

  #新規引数の後でキャッシュ済み引数で呼び出します

  assert c.get((5, 6), {"c": 7}) == 18
  assert recache_count == 4
  assert c.get((2, 3), {"c": 4}) == 9
  assert recache_count == 4
  assert c.get((3, 4), {"c": 5}) == 12
  assert recache_count == 4

  c.clear()

  assert c.get((5, 6), {"c": 7}) == 18
  assert recache_count == 5
  assert c.get((2, 3), {"c": 4}) == 9
  assert recache_count == 6
  assert c.get((3, 4), {"c": 5}) == 12
  assert recache_count == 7

def test_caches2 ():

  #calc_key_func を指定した場合の動作確認

  recache_count = 0

  def calc_key_func (args:tuple[int, int], kwargs:dict[str, int]) -> int:
    return 0

  def calc_value_func (args:tuple[int, int], kwargs:dict[str, int]) -> int:
    nonlocal recache_count
    recache_count += 1
    a, b = args
    c = kwargs["c"]
    return a + b + c

  c = caches.Caches(3, calc_key_func=calc_key_func, calc_value_func=calc_value_func)

  #calc_key_func が常に同じ値を返すため、最初の引数だけがキャッシュされます

  assert c.get((1, 2), {"c": 3}) == 6
  assert recache_count == 1
  assert c.get((2, 3), {"c": 4}) == 6 #キャッシュ済み6が返されます
  assert recache_count == 1
  assert c.get((3, 4), {"c": 5}) == 6 #キャッシュ済み6が返されます
  assert recache_count == 1

def test_caches_zero_max_cache_count ():

  #max_cache_count に0を指定した場合の動作確認

  recache_count = 0

  def calc_value_func (args:tuple[int, int], kwargs:dict[str, int]) -> int:
    nonlocal recache_count
    recache_count += 1
    a, b = args
    c = kwargs["c"]
    return a + b + c

  c = caches.Caches(0, calc_value_func=calc_value_func)

  assert c.get((1, 2), {"c": 3}) == 6
  assert recache_count == 1
  assert c.get((1, 2), {"c": 3}) == 6
  assert recache_count == 2
  assert c.get((1, 2), {"c": 3}) == 6
  assert recache_count == 3

def test_caches_change_max_cache_count ():

  #max_cache_count を途中で変更した場合の動作確認

  recache_count = 0

  def calc_value_func (args:tuple[int, int], kwargs:dict[str, int]) -> int:
    nonlocal recache_count
    recache_count += 1
    a, b = args
    c = kwargs["c"]
    return a + b + c

  c = caches.Caches(3, calc_value_func=calc_value_func)

  assert c.get((1, 2), {"c": 3}) == 6
  assert recache_count == 1
  assert c.get((2, 3), {"c": 4}) == 9
  assert recache_count == 2
  assert c.get((3, 4), {"c": 5}) == 12
  assert recache_count == 3

  c.max_cache_count = 0

  #max_cache_count が変更された場合、次の .get 実行後にキャッシュが整理されます。

  assert c.get((1, 2), {"c": 3}) == 6
  assert recache_count == 3
  assert c.get((1, 2), {"c": 3}) == 6
  assert recache_count == 4
  assert c.get((1, 2), {"c": 3}) == 6
  assert recache_count == 5
