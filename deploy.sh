#!/bin/bash
# modified, originally from: https://gist.github.com/domenic/ec8b0fc8ab45f39403dd
set -e # Exit with nonzero exit code if anything fails

SOURCE_BRANCH="master"
TARGET_BRANCH="gh-pages"
BUILD_DIR=".build"
WEBGENERATOR_REPO="https://github.com/graphicore/Atem-Webgenerator.git"
WEBGENERATOR_DIR=".webgenerator"

pip install git+$WEBGENERATOR_REPO

function doCompile {
    webgenerator . $BUILD_DIR
}

# Pull requests and commits to other branches shouldn't try to deploy, just build to verify
if [ "$TRAVIS_PULL_REQUEST" != "false" -o "$TRAVIS_BRANCH" != "$SOURCE_BRANCH" ]; then
    echo "Skipping deploy; just doing a build."
    doCompile
    exit 0
fi

# Save some useful information
REPO=`git config remote.origin.url`
SSH_REPO=${REPO/https:\/\/github.com\//git@github.com:}
SHA=`git rev-parse --verify HEAD`


# Clone the existing gh-pages for this repo into $BUILD_DIR/
# Create a new empty branch if gh-pages doesn't exist yet (should only happen on first deploy)
git clone $REPO $BUILD_DIR
pushd .
cd $BUILD_DIR
git checkout $TARGET_BRANCH || git checkout --orphan $TARGET_BRANCH
popd

# Clean out existing contents
# NOT advisable for our case! Atem-Webgenerator is doing "garceful" updates
# rm -rf out/**/* || exit 0

# Run our compile script
doCompile
