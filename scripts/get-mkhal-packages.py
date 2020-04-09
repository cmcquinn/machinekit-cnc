#!/usr/bin/env python3

import json
import subprocess
import argparse
import zipfile
import io
import sys


def printErr(msg):
    print("\033[91m {}\033[00m" .format(msg))


def getMkHalPackages(githubID, tag, outputPath):
    # get artifacts_url from latest run
    result = json.loads(subprocess.check_output(
        'hub api -X GET /repos/{}/machinekit-hal/actions/workflows/build-preview.yaml/runs'.format(githubID).split()))
    artifacts_url = result.get('workflow_runs')[0].get('artifacts_url')

    # get artifacts list
    artifacts = json.loads(subprocess.check_output(
        'hub api -X GET {}'.format(artifacts_url).split())).get('artifacts')
    artifact_list = []

    # get rid of unneeded info
    keylist = ['archive_download_url', 'name']
    for artifact in artifacts:
        info = dict()
        for key in artifact.keys():
            if key in keylist:
                info[key] = artifact.get(key)
        artifact_list.append(info)

    artifacts = artifact_list

    # match tag and print out artifact list
    url = None
    print('Artifacts list retreived from API:')
    for artifact in artifacts:
        print(artifact)
        if artifact['name'].find(tag) is not -1:
            name = artifact['name']
            url = artifact.get('archive_download_url')

    if url is None:
        printErr('Unable to find an artifact with the tag ' + tag)
        sys.exit(1)

    # get zip archive and extract files
    print('Downloading {} from {}'.format(name, url))
    try:
        archive = io.BytesIO(subprocess.check_output(
            'hub api -X GET {}'.format(url).split()))
        with zipfile.ZipFile(archive) as ziparchive:
            print('Extracting Debian packages to ' + outputPath)
            ziparchive.extractall(path=outputPath)
    except subprocess.CalledProcessError as error:
        printErr(error.output)
        sys.exit(1)


if __name__ == "__main__":
    # build up command-line arguments
    parser = argparse.ArgumentParser(
        description='Process command line arguments')
    parser.add_argument('-i', metavar='githubID', type=str,
                        help='GitHub user ID for the owner of the machinekit-hal repository to get packages from', dest='githubID', required=True, nargs='?')
    parser.add_argument('-t', metavar='tag', type=str,
                        help='Tag containing Debian version and arch to get packages for', dest='tag', required=True, nargs='?')
    parser.add_argument('-o', metavar='outputPath', type=str,
                        help='Directory to put the zipfile containing packages into', dest='outputPath', required=True, nargs='?')
    parser.add_argument('-w', metavar='workflow', type=str,
                        help='Name of the workflow to get packages from', default='build-preview.yaml', dest='workflow')

    args = parser.parse_args()
    getMkHalPackages(args.githubID, args.tag, args.outputPath)
