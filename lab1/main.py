from math import log2, log
from pathlib import Path


def sensible_Hn_values(path: str, max_n: int = 5):
    """
    Compute the values of n for which H_n is sensible.
    Input:
        path: path to the file that will be read in binary mode.
        max_n: the maximum value of n that will be considered.
    Output:
        n: the values of n for which H_n is sensible.
    """
    N = Path(path).stat().st_size  # File size in bytes
    n = round(log(N, 2**8))  # Could be floor
    return range(1, min(n + 1, max_n))


def my_analyze_file(path: str, n: int = 5):
    """
    Compute H_n for a given file.
    Input:
        path: path to the file that will be read in binary mode,
        n: the n in H_n, with of moving window with lenght n-bytes.
    Output:
        H_n: entropy in bits per n-byte block.
    """
    data = Path(path).read_bytes()  # Reads the file in binary mode
    counts = {}  # Initialize the dictionary of counts
    for i in range(len(data) - n + 1):
        key = data[i : i + n]  # Extract the n-byte window/block
        counts[key] = counts[key] + 1 if key in counts else 1  # Increment the count or set it to 1 if it's the first time

    probs = {}  # Initialize the dictionary of probabilities
    for key, count in counts.items():
        probs[key] = count / (len(data) - n + 1)  # Compute the probability of the n-byte window/block

    entropies = {}
    for key, prob in probs.items():
        entropies[key] = -prob * log2(prob) / n  # Compute the entropy of the n-byte window/block

    h = sum(entropies.values())  # Calculate the entropy in bits per n-byte block [bit/byte] or [bit/character]
    return h, entropies, probs, counts


if __name__ == "__main__":
    filepath = "datoteke/besedilo.txt"
    print("filepath:", filepath)
    for n in range(1, 6):
        print(f"\tH_{n}: {my_analyze_file(filepath,  n=n)[0]}")

    files = ["iss_0480.jpg", "iss_0960.jpg", "iss_1920.jpg", "iss_2560.jpg", "iss_3840.jpg", "iss_7680.jpg"]
    for file in files:
        filepath = f"datoteke/{file}"
        print("filepath:", filepath)
        for n in range(1, 6):
            print(f"\tH_{n}: {my_analyze_file(filepath,  n=n)[0]}")

    files = ["posnetek.aiff", "posnetek.flac", "posnetek.m4a", "posnetek.mp3", "posnetek.ogg", "posnetek.raw", "posnetek.wav"]
    for file in files:
        filepath = f"datoteke/{file}"
        print("filepath:", filepath)
        for n in range(1, 6):
            print(f"\tH_{n}: {my_analyze_file(filepath,  n=n)[0]}")
