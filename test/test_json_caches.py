
import json
import time
import caches
import pytest
import shutil
from typing import ClassVar
from pathlib import Path

TEST_DIR = Path("./.test")
TEST_FILES = [
  (TEST_DIR.joinpath("sample.json"), ["abc"]),
  (TEST_DIR.joinpath("sample2.json"), ["def"]),
  (TEST_DIR.joinpath("sample3.json"), ["ghi"]),
  (TEST_DIR.joinpath("sample4.json"), ["jkl"]),
]

def setup_function (func):
  TEST_DIR.mkdir(parents=True)
  for path, data in TEST_FILES:
    with open(path, "w") as file:
      json.dump(data, file)

def teardown_function (func):
  shutil.rmtree(TEST_DIR)

SLEEP_AMOUNT:ClassVar[int] = 1
SLEEP_AMOUNT_FOR_ATIME:ClassVar[int] = 2

def test_json_caches ():

  #基本的な動作確認を行います
  
  c = caches.json_caches(3)

  assert c.get((TEST_FILES[0][0],)) == TEST_FILES[0][1]
  assert c.get((TEST_FILES[1][0],)) == TEST_FILES[1][1]
  assert c.get((TEST_FILES[2][0],)) == TEST_FILES[2][1]

  time.sleep(SLEEP_AMOUNT_FOR_ATIME) #atime が更新されるまで待機する
  last_file_stats = [path.stat() for path, _ in TEST_FILES]
  time.sleep(SLEEP_AMOUNT) #atime の変化幅を確保するために待機する

  #これらはキャッシュ済みなので atime は変化しない

  assert c.get((TEST_FILES[0][0],)) == TEST_FILES[0][1]
  assert c.get((TEST_FILES[1][0],)) == TEST_FILES[1][1]
  assert c.get((TEST_FILES[2][0],)) == TEST_FILES[2][1]

  assert TEST_FILES[0][0].stat().st_atime == last_file_stats[0].st_atime
  assert TEST_FILES[1][0].stat().st_atime == last_file_stats[1].st_atime
  assert TEST_FILES[2][0].stat().st_atime == last_file_stats[2].st_atime

  #未キャッシュのファイルを1つ読み込んだ場合の動作確認

  assert c.get((TEST_FILES[3][0],)) == TEST_FILES[3][1]
  assert c.get((TEST_FILES[1][0],)) == TEST_FILES[1][1]
  assert c.get((TEST_FILES[2][0],)) == TEST_FILES[2][1]

  time.sleep(SLEEP_AMOUNT_FOR_ATIME) #atime が更新されるまで待機する

  assert TEST_FILES[3][0].stat().st_atime != last_file_stats[3].st_atime
  assert TEST_FILES[1][0].stat().st_atime == last_file_stats[1].st_atime #キャッシュ済みなので atime は変化しない
  assert TEST_FILES[2][0].stat().st_atime == last_file_stats[2].st_atime #キャッシュ済みなので atime は変化しない

def test_json_caches2 ():

  #基本的な動作確認を行います

  c = caches.json_caches(3)

  assert c.get((TEST_FILES[0][0],)) == TEST_FILES[0][1]
  assert c.get((TEST_FILES[1][0],)) == TEST_FILES[1][1]
  assert c.get((TEST_FILES[2][0],)) == TEST_FILES[2][1]

  time.sleep(SLEEP_AMOUNT_FOR_ATIME) #atime が更新されるまで待機する
  last_file_stats = [path.stat() for path, _ in TEST_FILES]
  time.sleep(SLEEP_AMOUNT) #atime の変化幅を確保するために待機する

  #kwargs を指定した場合と未指定の場合はそれぞれ別にキャッシュされます

  assert c.get((TEST_FILES[0][0],), {"encoding": "ascii"}) == TEST_FILES[0][1]
  assert c.get((TEST_FILES[1][0],), {"encoding": "ascii"}) == TEST_FILES[1][1]
  assert c.get((TEST_FILES[2][0],), {"encoding": "ascii"}) == TEST_FILES[2][1]

  assert TEST_FILES[0][0].stat().st_atime != last_file_stats[0].st_atime
  assert TEST_FILES[1][0].stat().st_atime != last_file_stats[1].st_atime 
  assert TEST_FILES[2][0].stat().st_atime != last_file_stats[2].st_atime 

def test_json_caches3 ():

  #更新されたファイルが再キャッシュされるかを検証します

  c = caches.json_caches(3)

  assert c.get((TEST_FILES[0][0],)) == TEST_FILES[0][1]
  assert c.get((TEST_FILES[1][0],)) == TEST_FILES[1][1]
  assert c.get((TEST_FILES[2][0],)) == TEST_FILES[2][1]

  time.sleep(SLEEP_AMOUNT_FOR_ATIME) #atime が更新されるまで待機する
  last_file_stats = [path.stat() for path, _ in TEST_FILES]
  time.sleep(SLEEP_AMOUNT) #atime の変化幅を確保するために待機する

  #ファイルの更新を行います

  with open(TEST_FILES[0][0], "w") as file:
    json.dump(["ABC"], file)

  #更新を行ったファイルを読み込みます

  assert c.get((TEST_FILES[0][0],)) == ["ABC"]
  assert c.get((TEST_FILES[1][0],)) == TEST_FILES[1][1]
  assert c.get((TEST_FILES[2][0],)) == TEST_FILES[2][1]

  time.sleep(SLEEP_AMOUNT_FOR_ATIME) #atime が更新されるまで待機する

  assert TEST_FILES[0][0].stat().st_atime != last_file_stats[0].st_atime
  assert TEST_FILES[1][0].stat().st_atime == last_file_stats[1].st_atime #キャッシュ済みなので atime は変化しない
  assert TEST_FILES[2][0].stat().st_atime == last_file_stats[2].st_atime #キャッシュ済みなので atime は変化しない

def test_json_caches_zero_max_cache_count ():

  #max_cache_count に0を指定した場合の動作確認

  c = caches.json_caches(0)

  assert c.get((TEST_FILES[0][0],)) == TEST_FILES[0][1]

  time.sleep(SLEEP_AMOUNT_FOR_ATIME) #atime が更新されるまで待機する
  last_file_stats = [path.stat() for path, _ in TEST_FILES]
  time.sleep(SLEEP_AMOUNT) #atime の変化幅を確保するために待機する

  assert c.get((TEST_FILES[0][0],)) == TEST_FILES[0][1]
  assert c.get((TEST_FILES[0][0],)) == TEST_FILES[0][1]
  assert c.get((TEST_FILES[0][0],)) == TEST_FILES[0][1]

  time.sleep(SLEEP_AMOUNT_FOR_ATIME) #atime が更新されるまで待機する
  
  assert TEST_FILES[0][0].stat().st_atime != last_file_stats[0].st_atime
