import argparse

from pipelines.correlation_pipeline import correlation_pipeline


def main():
    """
    Entrypoint for the program. Specify duration in seconds and Spotify poll
    interval through argparse.
    """
    parser = argparse.ArgumentParser(
        description="Run the music-typing correlation pipeline with custom durations."
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Total duration of the typing & music tracking (in seconds)."
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=1,
        help="Interval between Spotify polling (in seconds)."
    )
    args = parser.parse_args()

    # Run the ZenML pipeline
    correlation_pipeline(duration=args.duration, poll_interval=args.poll_interval)


if __name__ == "__main__":
    main()
