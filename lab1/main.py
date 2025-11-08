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


def plot_probabilities_or_entropy(
    data: dict,
    xlabel: str = "n-byte block (hex)",
    ylabel: str = "Data",
    title: str = "Probabilities of n-byte windows/blocks",
    file="figure.png",
):
    import matplotlib.pyplot as plt

    # Sort and convert binary keys for plotting
    sorted_keys = sorted(data.keys())
    sorted_values = [data[key] for key in sorted_keys]
    labels = [hex(key[0]) for key in sorted_keys]

    font_size = 24
    # 36 prevelik

    plt.rcParams.update(
        {
            "font.size": font_size,  # osnovna velikost pisave
            "axes.labelsize": font_size,  # velikost oznak osi
            "xtick.labelsize": font_size * 0,  # velikost oznak na osi x
            "ytick.labelsize": font_size,  # velikost oznak na osi y
            "axes.titlesize": font_size,  # naslov grafa
            "font.family": "Times New Roman",
        }
    )
    plt.figure(figsize=(9, 5))
    plt.bar(range(len(labels)), sorted_values)  # Use numeric positions
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    # Show only every 8th label
    ax = plt.gca()
    ax.set_xticks(range(0, len(labels), 8))
    ax.set_xticklabels([labels[i] for i in range(0, len(labels), 8)], rotation=90)

    # Remove margins - bars go to edges
    plt.xlim(-0.5, len(labels) - 0.5)

    plt.tight_layout()

    plt.savefig(file, dpi=600, bbox_inches="tight")


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
        entropies[key] = -prob * log2(prob)  # Compute the entropy of the n-byte window/block

    h = sum(entropies.values()) / n  # Calculate the entropy in bits per n-byte block [bit/byte] or [bit/character]
    return h, entropies, probs, counts


if __name__ == "__main__":
    # filepath = "datoteke/besedilo.txt"
    # print("filepath:", filepath)
    # for n in range(1, 6):
    #     print(f"\tH_{n}: {my_analyze_file(filepath,  n=n)[0]}")
    #
    # files = ["iss_0480.jpg", "iss_0960.jpg", "iss_1920.jpg", "iss_2560.jpg", "iss_3840.jpg", "iss_7680.jpg"]
    # for file in files:
    #     filepath = f"datoteke/{file}"
    #     print("filepath:", filepath)
    #     for n in range(1, 6):
    #         print(f"\tH_{n}: {my_analyze_file(filepath,  n=n)[0]}")
    #
    # files = ["posnetek.aiff", "posnetek.flac", "posnetek.m4a", "posnetek.mp3", "posnetek.ogg", "posnetek.raw", "posnetek.wav"]
    # for file in files:
    #     filepath = f"datoteke/{file}"
    #     print("filepath:", filepath)
    #     for n in range(1, 6):
    #         print(f"\tH_{n}: {my_analyze_file(filepath,  n=n)[0]}")

    xlabel = "n-bajtni nizi (od x00 do xFF)"
    ylabel = "Verjetnost niza"
    title = "Verjetnost n-bajtnih nizov"
    plot_probabilities_or_entropy(my_analyze_file("datoteke/posnetek.aiff", n=1)[2], xlabel=xlabel, ylabel=ylabel, title=title, file="datoteke/verjetnostNizovAiff.png")
    plot_probabilities_or_entropy(my_analyze_file("datoteke/posnetek.mp3", n=1)[2], xlabel=xlabel, ylabel=ylabel, title=title, file="datoteke/verjetnostNizovMp3.png")
