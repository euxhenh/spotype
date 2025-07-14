# Music Typing Correlation Pipeline

This repository demonstrates how to build a simple—but real‐time—personal
analytics pipeline with [ZenML](https://github.com/zenml-io/zenml). It
simultaneously tracks your typing speed and polls Spotify for the currently
playing track, segments your keystrokes by track, fetches each artist’s genres,
computes words-per-minute (WPM) per track, and visualizes the results.

## Concept & Architecture

ZenML is an MLOps framework that lets you define:

1. **Steps**: Modular, reusable functions that produce/consume artifacts.
2. **Pipelines**: Ordered sequences of steps wired together.
3. **Stacks**: Execution environments, artifact stores, orchestrators, etc.

Here, our pipeline has two steps:

- **`collect_and_track`**
  - Listens to your keyboard events for a user-configurable duration
  - Polls Spotify’s "currently playing" API at a user-configurable interval
  - Splits your keystrokes into time segments per track
  - Fetches each artist’s genres in batch
  - Computes WPM for each track segment
  - Returns a `pandas.DataFrame` with one row per track segment
    containing:
    ```text
    track_id, track_name, artist_name, genres, duration_seconds, keypresses, wpm
    ```

- **`visualize`**
  - Takes the DataFrame of per-track segments
  - Computes average WPM per track (or per genre)
  - Plots a bar chart (`data/wpm_by_genre.png`)

These steps are wired into a single ZenML pipeline:

```python
@pipeline
def correlation_pipeline(duration: int = 60, poll_interval: int = 1):
    df = collect_and_track(duration=duration, poll_interval=poll_interval)
    visualize(df)
```

## Repository Structure

```
.
├── data/                         ← token cache & output plots
├── pipelines/
│   └── correlation_pipeline.py   ← pipeline definition
├── run.py                        ← CLI entrypoint
├── steps/
│   ├── collect_and_track.py      ← combined data-collection step
│   └── visualize.py              ← plotting step
├── utils/
│   └── spotify_auth.py           ← OAuth helper
├── requirements.txt
└── README.md
```

## Getting Started

1. **Clone & Install**

```bash
git clone https://github.com/your-org/zenml-music-typing.git
cd zenml-music-typing
pip install -r requirements.txt
```

2. **Initialize ZenML**
```bash
zenml init
```
You’ll see a default stack with local orchestrator & artifact store.

3. **Configure Spotify OAuth**

Create a Spotify Developer app:
  - Redirect URI: http://127.0.0.1:8888/callback

Set your credentials (in your shell or a `.env` file):

```bash
export SPOTIPY_CLIENT_ID=your_client_id
export SPOTIPY_CLIENT_SECRET=your_client_secret
export SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
```

Run a quick auth check to populate the token cache:

```bash
python - <<EOF
from utils.spotify_auth import get_spotify_client
get_spotify_client()
EOF
```

This will open your browser, ask you to grant "Playback State" permission, and
save a token to `data/.spotify_token.json`.

4. **Run the Pipeline**

```bash
python run.py --duration 90
```

  - `--duration` (seconds): total time to track typing & poll Spotify. For a
    better solution, this should be turned into a cron job, but for the purposes
    of this demo it should suffice.

ZenML will:
  1. Spin up a pipeline run
  2. Execute `collect_and_track` (real-time keystroke + track polling)
  3. Execute `visualize` (bar chart of WPM by genre)
  4. Save the plot to `data/wpm_by_track.png`

You can also view run metadata & logs in the local ZenML dashboard.

## What’s Happening Under the Hood?

  1. **Keyboard Listener**
     - Uses `pynput` to timestamp every key press.

  2. Spotify Polling
     - Uses `spotipy` + OAuth to fetch your currently playing track.
     - Detects when a track changes to split keystrokes into segments.

  3. **Genre Enrichment**
     - Batches artist IDs through `sp.artists(...)` to fetch each artist’s genre list.

  4. WPM Calculation
     - Counts key presses in each segment, converts to "words" (assuming 5
       chars/word), normalizes by segment duration to compute WPM.

  5. Visualization
     - Groups segments by track (or genre) and plots average WPM.

## Next Steps
  - **Focus vs. Energy buckets**: map genres to “focus”/“energetic” categories.
  - **ZenML Secrets**: store your Spotify credentials securely in a managed
    secrets store.
  - **Cloud Orchestration**: switch your stack from local to
    Airflow/Prefect/Kubernetes for scheduled, containerized runs.
  - **Dashboards**: integrate with Streamlit or Plotly Dash for live
    exploration.
