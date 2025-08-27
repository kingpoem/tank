# scripts/autoflake_wrapper.py
import subprocess


def main():
    subprocess.run([
        "autoflake",
        "--in-place",
        "--remove-unused-variables",
        "--remove-all-unused-imports",
        "--recursive",
        "."
    ])

