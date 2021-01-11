#!/bin/bash

set +x # Do not leak information

if [ ! -z "$APPVEYOR" ]; then
    TRAVIS_REPO_SLUG="$APPVEYOR_REPO_NAME"
    TRAVIS_TAG="$APPVEYOR_REPO_TAG_NAME"
    TRAVIS_BUILD_NUMBER="$APPVEYOR_BUILD_NUMBER"
    TRAVIS_BUILD_ID="$APPVEYOR_BUILD_ID"
    TRAVIS_BRANCH="$APPVEYOR_REPO_BRANCH"
    TRAVIS_COMMIT="$APPVEYOR_REPO_COMMIT"
    TRAVIS_JOB_ID="$APPVEYOR_JOB_ID"
    TRAVIS_BUILD_WEB_URL="${APPVEYOR_URL}/project/${APPVEYOR_ACCOUNT_NAME}/${APPVEYOR_PROJECT_SLUG}/build/job/${APPVEYOR_JOB_ID}"
    echo "inhibit_deploy"
    echo "$inhibit_deploy"
    if [[ $APPVEYOR_REPO_COMMIT_MESSAGE =~ nodeploy ]] || [[ $APPVEYOR_REPO_COMMIT_MESSAGE_EXTENDED =~ nodeploy ] ; then
      echo "Release uploading disabled, commit message contains 'nodeploy'"
      exit 0
    fi
    if [ ! -z "$APPVEYOR_PULL_REQUEST_NUMBER" ] ; then
      echo "Release uploading disabled for pull requests"
      exit 0
    fi
fi

echo "Web url"
echo "$TRAVIS_BUILD_WEB_URL"
