import subprocess
import sys
import os
from datetime import datetime

STEPS = [
    ("Extraction", "bs_extract_text.py"),
    ("Chunking", "bs_chunk_all.py"),
    ("Embedding", "bs_embed_all.py"),
]

os.makedirs("logs", exist_ok=True)
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_PATH = f"logs/pipeline_run_{TIMESTAMP}.log"


def run_step(name, script, log_file):
    header = f"\n{'=' * 80}\nSTEP: {name} ({script})\n{'=' * 80}\n"
    print(header)
    log_file.write(header)
    log_file.flush()

    process = subprocess.Popen(
        [sys.executable, script],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    for line in process.stdout:
        print(line, end="")
        log_file.write(line)
    process.wait()

    if process.returncode != 0:
        msg = f"\nFAILED: {script} exited with code {process.returncode}. Stopping pipeline.\n"
        print(msg)
        log_file.write(msg)
        return False
    return True


def main():
    with open(LOG_PATH, "w", encoding="utf-8") as log_file:
        start_msg = f"Pipeline run started: {datetime.now().isoformat()}\n"
        print(start_msg)
        log_file.write(start_msg)

        for name, script in STEPS:
            if not run_step(name, script, log_file):
                sys.exit(1)

        end_msg = f"\nPipeline run finished: {datetime.now().isoformat()}\nLog saved to {LOG_PATH}\n"
        print(end_msg)
        log_file.write(end_msg)


if __name__ == "__main__":
    main()