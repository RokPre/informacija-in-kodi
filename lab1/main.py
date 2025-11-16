from math import log2, log
from pathlib import Path
import matplotlib.pyplot as plt


def sensible_Hn_values(path: str, max_n: int = 5) -> range:
    """
    Compute the range of n values for which H_n (entropy per n-byte block) is sensible.

    Args:
        path: Path to the binary file.
        max_n: Maximum n to consider.

    Returns:
        range of integers from 1 to sensible upper limit for n.
    """
    N = Path(path).stat().st_size  # File size in bytes
    # n = round(log(N, 2**8))  # Rough upper limit of meaningful n
    # return range(1, min(n + 1, max_n))
    n = int(N / 10)
    return range(1, min(n, max_n) + 1)


def configure_matplotlib(font_size: int = 22):
    """Globally configure matplotlib style (Times New Roman, proper sizing)."""
    plt.rcParams.update(
        {
            "font.family": "Times New Roman",
            "font.size": font_size,
            "axes.labelsize": font_size,
            "axes.titlesize": font_size,
            "xtick.labelsize": font_size * 0.7,
            "ytick.labelsize": font_size * 0.9,
            "legend.fontsize": font_size * 0.8,
            "figure.dpi": 600,
        }
    )


def plot_probabilities_or_entropy(
    data: dict,
    xlabel: str = "n-byte block (hex)",
    ylabel: str = "Probability",
    title: str = "Byte Distribution",
    file: str = "figure.png",
):
    """
    Plot probability or entropy data for n-byte blocks.

    Args:
        data: Dict mapping bytes sequences → probabilities.
        xlabel, ylabel, title: Plot labels.
        file: Output file path.
    """
    configure_matplotlib(22)

    sorted_keys = sorted(data.keys())
    sorted_values = [data[k] for k in sorted_keys]

    # Use printable ASCII if possible, else hex representation
    def key_to_label(k: bytes) -> str:
        b = k[0]
        return chr(b) if 32 <= b < 127 else hex(b)

    labels = [key_to_label(k) for k in sorted_keys]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(len(labels)), sorted_values, color="steelblue", edgecolor="black", linewidth=0.3)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    # Show every 8th label for readability
    ax.set_xticks(range(0, len(labels), 8))
    ax.set_xticklabels([labels[i] for i in range(0, len(labels), 8)], rotation=90)

    ax.set_xlim(-0.5, len(labels) - 0.5)
    plt.tight_layout()

    Path(file).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(file, bbox_inches="tight")
    plt.close(fig)


def plot_levels_of_entropy(
    datasets: list[list[float]],
    labels: list[str] | None = None,
    xlabel: str = "n",
    ylabel: str = "Hₙ [bit/znak]",
    title: str = "Entropija za različne vrste podatkov",
    file: str = "entropy_levels.png",
):
    """
    Plot Hₙ vs n for multiple files or datasets.

    Args:
        datasets: List of Hₙ sequences (one per file).
        labels: Corresponding labels for legend.
        file: Output file path.
    """
    configure_matplotlib(22)
    fig, ax = plt.subplots(figsize=(9, 5))

    colors = ["tab:blue", "tab:green", "tab:red", "tab:purple", "tab:orange"]

    for i, d in enumerate(datasets):
        label = labels[i] if labels and i < len(labels) else f"Dataset {i+1}"
        ax.plot(range(1, len(d) + 1), d, marker="o", linewidth=1.5, color=colors[i % len(colors)], label=label)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    plt.tight_layout()

    Path(file).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(file, bbox_inches="tight")
    plt.close(fig)


def my_analyze_file(path: str, n: int = 5):
    """
    Compute Hₙ (entropy per n-byte block) for a file.

    Args:
        path: Path to binary file.
        n: Block length in bytes.

    Returns:
        Tuple: (Hₙ value, entropies dict, probabilities dict, counts dict)
    """
    data = Path(path).read_bytes()
    counts: dict[bytes, int] = {}

    # Count n-byte sequences
    for i in range(len(data) - n + 1):
        key = data[i : i + n]
        counts[key] = counts.get(key, 0) + 1

    total_blocks = len(data) - n + 1
    probs = {k: v / total_blocks for k, v in counts.items()}
    entropies = {k: -p * log2(p) for k, p in probs.items()}

    Hn = sum(entropies.values()) / n
    return Hn, entropies, probs, counts


if __name__ == "__main__":
    # Example file paths
    base = "datoteke"
    text_file = f"{base}/besedilo.txt"
    image_files = [f"{base}/iss_{r}.jpg" for r in ["0480", "0960", "1920", "2560", "3840", "7680"]]
    audio_files = [f"{base}/posnetek.{ext}" for ext in ["aiff", "flac", "m4a", "mp3", "ogg", "raw", "wav"]]

    # Compute and print entropies
    for group in [text_file, *image_files, *audio_files]:
        print(f"\nFile: {group}")
        for n in range(1, 6):
            Hn = my_analyze_file(group, n)[0]
            print(f"  H_{n}: {Hn:.3f}")

    # Plot example probability distributions
    plot_probabilities_or_entropy(
        my_analyze_file(f"{base}/posnetek.aiff", n=1)[2],
        xlabel="Bajt (hex/ascii)",
        ylabel="Verjetnost",
        title="Porazdelitev bajtov – AIFF",
        file=f"{base}/verjetnostNizovAiff.png",
    )

    plot_probabilities_or_entropy(
        my_analyze_file(f"{base}/posnetek.mp3", n=1)[2],
        xlabel="Bajt (hex/ascii)",
        ylabel="Verjetnost",
        title="Porazdelitev bajtov – MP3",
        file=f"{base}/verjetnostNizovMp3.png",
    )

    # Entropy levels for multiple data types
    print(f"\tFile: {text_file}")
    result_text = [my_analyze_file(text_file, n=n)[0] for n in range(1, 26)]
    print(f"\tFile: {image_files[-1]}")
    result_image = [my_analyze_file(image_files[-1], n=n)[0] for n in range(1, 26)]
    print(f"\tFile: {audio_files[0]}")
    result_audio = [my_analyze_file(audio_files[0], n=n)[0] for n in range(1, 26)]
    print(f"\tFile: {audio_files[3]}")
    result_audio_mp3 = [my_analyze_file(audio_files[3], n=n)[0] for n in range(1, 26)]

    plot_levels_of_entropy(
        [result_text, result_image, result_audio, result_audio_mp3],
        labels=["Besedilo", "Slika", "Zvok (AIFF)", "Zvok (MP3)"],
        xlabel="Dolžina niza n [bajtov]",
        ylabel="Entropija Hₙ [bit/znak]",
        title="Entropija pri različnih tipih datotek",
        file=f"{base}/entropija_tipov.png",
    )
