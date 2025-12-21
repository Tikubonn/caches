
import time
import caches
import pytest
import shutil
from pathlib import Path

TEST_DIR:Path = Path("./.test")
TEST_FILES:list[Path] = [
  (TEST_DIR.joinpath("sample.txt"), "abc"),
  (TEST_DIR.joinpath("sample2.txt"), "def"),
  (TEST_DIR.joinpath("sample3.txt"), "ghi"),
  (TEST_DIR.joinpath("sample4.txt"), "jkl"),
]

def setup_function (func):
  TEST_DIR.mkdir(parents=True)
  for path, data in TEST_FILES:
    with open(path, "w") as file:
      file.write(data)

def teardown_function (func):
  shutil.rmtree(TEST_DIR)

SLEEP_AMOUNT:int = 1
SLEEP_AMOUNT_FOR_ATIME:int = 2

def test_file_caches ():

  #基本的な動作確認を行います
  
  c = caches.file_caches(3)

  assert c.get((TEST_FILES[0][0], "r")) == TEST_FILES[0][1]
  assert c.get((TEST_FILES[1][0], "r")) == TEST_FILES[1][1]
  assert c.get((TEST_FILES[2][0], "r")) == TEST_FILES[2][1]

  time.sleep(SLEEP_AMOUNT_FOR_ATIME) #atime が更新されるまで待機する
  last_file_stats = [path.stat() for path, _ in TEST_FILES]
  time.sleep(SLEEP_AMOUNT) #atime の変化幅を確保するために待機する

  #これらはキャッシュ済みなので atime は変化しない

  assert c.get((TEST_FILES[0][0], "r")) == TEST_FILES[0][1]
  assert c.get((TEST_FILES[1][0], "r")) == TEST_FILES[1][1]
  assert c.get((TEST_FILES[2][0], "r")) == TEST_FILES[2][1]

  assert TEST_FILES[0][0].stat().st_atime == last_file_stats[0].st_atime
  assert TEST_FILES[1][0].stat().st_atime == last_file_stats[1].st_atime
  assert TEST_FILES[2][0].stat().st_atime == last_file_stats[2].st_atime

  #未キャッシュのファイルを1つ読み込んだ場合の動作確認

  assert c.get((TEST_FILES[3][0], "r")) == TEST_FILES[3][1]
  assert c.get((TEST_FILES[1][0], "r")) == TEST_FILES[1][1]
  assert c.get((TEST_FILES[2][0], "r")) == TEST_FILES[2][1]

  time.sleep(SLEEP_AMOUNT_FOR_ATIME) #atime が更新されるまで待機する

  assert TEST_FILES[3][0].stat().st_atime != last_file_stats[3].st_atime
  assert TEST_FILES[1][0].stat().st_atime == last_file_stats[1].st_atime #キャッシュ済みなので atime は変化しない
  assert TEST_FILES[2][0].stat().st_atime == last_file_stats[2].st_atime #キャッシュ済みなので atime は変化しない

def test_file_caches2 ():

  #基本的な動作確認を行います

  c = caches.file_caches(3)

  assert c.get((TEST_FILES[0][0], "r")) == TEST_FILES[0][1]
  assert c.get((TEST_FILES[1][0], "r")) == TEST_FILES[1][1]
  assert c.get((TEST_FILES[2][0], "r")) == TEST_FILES[2][1]

  time.sleep(SLEEP_AMOUNT_FOR_ATIME) #atime が更新されるまで待機する
  last_file_stats = [path.stat() for path, _ in TEST_FILES]
  time.sleep(SLEEP_AMOUNT) #atime の変化幅を確保するために待機する

  #kwargs を指定した場合と未指定の場合はそれぞれ別にキャッシュされます

  assert c.get((TEST_FILES[0][0], "r"), {"encoding": "ascii"}) == TEST_FILES[0][1]
  assert c.get((TEST_FILES[1][0], "r"), {"encoding": "ascii"}) == TEST_FILES[1][1]
  assert c.get((TEST_FILES[2][0], "r"), {"encoding": "ascii"}) == TEST_FILES[2][1]

  assert TEST_FILES[0][0].stat().st_atime != last_file_stats[0].st_atime
  assert TEST_FILES[1][0].stat().st_atime != last_file_stats[1].st_atime 
  assert TEST_FILES[2][0].stat().st_atime != last_file_stats[2].st_atime 

def test_file_caches3 ():

  #更新されたファイルが再キャッシュされるかを検証します

  c = caches.file_caches(3)

  assert c.get((TEST_FILES[0][0], "r")) == TEST_FILES[0][1]
  assert c.get((TEST_FILES[1][0], "r")) == TEST_FILES[1][1]
  assert c.get((TEST_FILES[2][0], "r")) == TEST_FILES[2][1]

  time.sleep(SLEEP_AMOUNT_FOR_ATIME) #atime が更新されるまで待機する
  last_file_stats = [path.stat() for path, _ in TEST_FILES]
  time.sleep(SLEEP_AMOUNT) #atime の変化幅を確保するために待機する

  #ファイルの更新を行います

  with open(TEST_FILES[0][0], "w") as file:
    file.write("ABC")

  #更新を行ったファイルを読み込みます

  assert c.get((TEST_FILES[0][0], "r")) == "ABC"
  assert c.get((TEST_FILES[1][0], "r")) == TEST_FILES[1][1]
  assert c.get((TEST_FILES[2][0], "r")) == TEST_FILES[2][1]

  time.sleep(SLEEP_AMOUNT_FOR_ATIME) #atime が更新されるまで待機する

  assert TEST_FILES[0][0].stat().st_atime != last_file_stats[0].st_atime
  assert TEST_FILES[1][0].stat().st_atime == last_file_stats[1].st_atime #キャッシュ済みなので atime は変化しない
  assert TEST_FILES[2][0].stat().st_atime == last_file_stats[2].st_atime #キャッシュ済みなので atime は変化しない

def test_file_caches_zero_max_cache_count ():

  #max_cache_count に0を指定した場合の動作確認

  c = caches.file_caches(0)

  assert c.get((TEST_FILES[0][0], "r")) == TEST_FILES[0][1]

  time.sleep(SLEEP_AMOUNT_FOR_ATIME) #atime が更新されるまで待機する
  last_file_stats = [path.stat() for path, _ in TEST_FILES]
  time.sleep(SLEEP_AMOUNT) #atime の変化幅を確保するために待機する

  assert c.get((TEST_FILES[0][0], "r")) == TEST_FILES[0][1]
  assert c.get((TEST_FILES[0][0], "r")) == TEST_FILES[0][1]
  assert c.get((TEST_FILES[0][0], "r")) == TEST_FILES[0][1]

  time.sleep(SLEEP_AMOUNT_FOR_ATIME) #atime が更新されるまで待機する
  
  assert TEST_FILES[0][0].stat().st_atime != last_file_stats[0].st_atime
