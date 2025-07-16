import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from zenml import step


@step
def visualize(df: pd.DataFrame) -> None:
    """Bar chart of typing speed (WPM) per track."""
    if df.empty:
        print("No data to visualize.")
        return

    # Clean genres column and handle missing values
    df['genres'] = df['genres'].fillna('').astype(str)
    df['genres'] = df['genres'].replace('', 'Unknown Genre')
    
    # Split and explode genres
    df['genres'] = df['genres'].str.split(',')
    df = df.explode('genres')
    df['genres'] = df['genres'].str.strip()

    ax = sns.boxplot(
        df,
        x="genres",
        y="wpm",
        hue='genres',
        palette='Set2',
    )

    sns.stripplot(
        df,
        x="genres",
        y="wpm",
        ax=ax,
        color=".3",
    )

    ax.set_xlabel('genre', fontsize=12)
    ax.set_ylabel('wpm', fontsize=12)
    ax.tick_params(axis='x', rotation=90)

    sns.despine(ax=ax)

    plt.tight_layout()

    plt.savefig("data/wpm_by_genre.png")
    print("Saved chart to 'data/wpm_by_genre.png'")

    plt.show()
