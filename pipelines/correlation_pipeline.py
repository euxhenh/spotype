from zenml import pipeline

from steps.collect_and_track import collect_and_track
from steps.visualize import visualize


@pipeline(enable_cache=False)
def correlation_pipeline(duration: int = 60, poll_interval: int = 1) -> None:
    """
    Args:
        duration (int): Total test duration (seconds).
        poll_interval (int): How often to poll Spotify (seconds).
    """
    df = collect_and_track(duration=duration, poll_interval=poll_interval)
    visualize(df)
