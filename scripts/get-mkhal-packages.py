#!/usr/bin/env python3

import json
import subprocess
import argparse
import zipfile
import io

# build up command-line arguments
parser = argparse.ArgumentParser(description='Process command line arguments')
parser.add_argument('-i', metavar='githubID', type=str, help='GitHub user ID for the owner of the machinekit-hal repository to get packages from', dest='githubID', required=True, nargs='?')
parser.add_argument('-t', metavar='tag', type=str, help='Tag containing Debian version and arch to get packages for', dest='tag', required=True, nargs='?')
parser.add_argument('-o', metavar='outputDir', type=str, help='Directory to put the zipfile containing packages into', dest='outputDir', required=True, nargs='?')
parser.add_argument('-w', metavar='workflow', type=str, help='Name of the workflow to get packages from', default='build-preview.yaml', dest='workflow')

args = parser.parse_args()

# get artifacts_url from latest run
result = json.loads(subprocess.check_output('hub api -X GET /repos/{}/machinekit-hal/actions/workflows/build-preview.yaml/runs'.format(args.githubID).split()))
artifacts_url = result.get('workflow_runs')[0].get('artifacts_url')

# get artifacts list
artifacts = json.loads(subprocess.check_output('hub api -X GET {}'.format(artifacts_url).split())).get('artifacts')

# match tag
for artifact in artifacts:
    if artifact['name'].find(args.tag) is not -1:
        url = artifact.get('archive_download_url')

# get zip archive and extract files
archive = io.BytesIO(subprocess.check_output('hub api -X GET {}'.format(url).split()))
with zipfile.ZipFile(archive) as ziparchive:
    ziparchive.extractall(path=args.outputDir)