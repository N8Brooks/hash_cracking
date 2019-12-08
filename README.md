# Hash Cracking

A python script for finding crc32 collisions with a word.

### Prerequisites

* Python3
* TQDM package

```
pip install tqdm
```

## Usage

### What it does

* Goes through all permutations of words printing those with the same crc32 hash as specified word
* Updates progress bar until it hits the time limit where the script will stop

### Help

```
python crack.py -h
```

### Example 

This will compute collisions with 'word' for 5 minutes*

```
python crack.py word -t 300
```


## Other

### Status

* **Future** - *Plans to add c++ version*

### Authors

* **Nathan Brooks** - *Initial work*

### License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
