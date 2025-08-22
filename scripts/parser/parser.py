"""YAML parser for Einstein Toolkit Apptainer image"""

import os
import shutil
import sys
from cluster import Cluster
from yaml import load, BaseLoader

class Parser:
    """
    A simple class to parse the cluster configuration YAML file.
    """

    def __init__(self, filename: str, outdir: str) -> None:
        self.infile = filename
        self.outdir = outdir

    def parse(self) -> None:
        clusters = load(open(self.infile), Loader=BaseLoader)

        for name, user_cfg in clusters.items():
            outfile = os.path.join(self.outdir, name.lower() + ".lua")
            with open(outfile, "w") as f:
                f.write(f"{Cluster(name, user_cfg)}")

            print(f"Successfully wrote configuration '{outfile}'")


if __name__ == "__main__":
    outdir = os.path.join(sys.argv[2], "cluster")
    shutil.rmtree(outdir, ignore_errors=True)
    os.mkdir(outdir)

    print(f"Outputting cluster configurations to {outdir}/")
    parser = Parser(sys.argv[1], outdir)
    parser.parse()
