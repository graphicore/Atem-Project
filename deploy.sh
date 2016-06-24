#!/bin/bash
# modified, originally from: https://gist.github.com/domenic/ec8b0fc8ab45f39403dd
set -e # Exit with nonzero exit code if anything fails

SOURCE_BRANCH="master"
TARGET_BRANCH="gh-pages"
BUILD_DIR=".build"
WEBGENERATOR_REPO="https://github.com/graphicore/Atem-Webgenerator.git"
WEBGENERATOR_DIR=".webgenerator"

git clone $WEBGENERATOR_REPO $WEBGENERATOR_DIR
pushd .
cd $WEBGENERATOR_DIR
# assume python is in version >= 3.5
# and since we are on travis, there's no need for a virtual environment
pip install -r requirements.txt
popd

function doCompile {
    $WEBGENERATOR_DIR/webgenerator.py . $BUILD_DIR
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

# Now let's go have some fun with the cloned repo
cd $BUILD_DIR


git config user.name "Travis CI"
git config user.email "$COMMIT_AUTHOR_EMAIL"

git add .
# If there are no changes to the compiled $BUILD_DIR (e.g. this is a README update) then just bail.
if [ -z "`git diff --cached`" ]; then
    echo "No changes to $TARGET_BRANCH on this push; exiting."
    exit 0
fi

echo 'deploying now ...'

# Commit the "changes", i.e. the new version.
# The delta will show diffs between new and old versions.

git commit -m "Travis deploy to GitHub Pages: ${SHA}"

# Get the deploy key by using Travis's stored variables to decrypt id_rsa.enc
ENCRYPTED_KEY_VAR="encrypted_${ENCRYPTION_LABEL}_key"
ENCRYPTED_IV_VAR="encrypted_${ENCRYPTION_LABEL}_iv"
ENCRYPTED_KEY=${!ENCRYPTED_KEY_VAR}
ENCRYPTED_IV=${!ENCRYPTED_IV_VAR}
openssl aes-256-cbc -K $ENCRYPTED_KEY -iv $ENCRYPTED_IV -in id_rsa.enc -out id_rsa -d
chmod 600 id_rsa
eval `ssh-agent -s`
ssh-add id_rsa

# Now that we're all set up, we can push.
git push $SSH_REPO $TARGET_BRANCH
