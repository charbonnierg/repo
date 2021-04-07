module.exports = {
  branches: [
    { name: "stable" },
    { name: "next", prerelease: "rc", channel: false },
  ],
  // Define plugins used
  plugins: [
    // # Use default options for commit-analyzer
    "@semantic-release/commit-analyzer",
    // We need to tell semantic release how it can generate URL for commits and issues
    // See: https://github.com/semantic-release/release-notes-generator/issues/119#issuecomment-614189962
    [
      "@semantic-release/release-notes-generator",
      {
        preset: "conventionalcommits",
        writerOpts: {
          commitsSort: ["subject", "scope"],
        },
      },
    ],
    // Write changelog into CHANGELOG.md
    ["@semantic-release/changelog", { changelogFile: "CHANGELOG.md" }],
    // # Use custom script to perform release
    [
      "@semantic-release/exec",
      {
        prepareCmd:
          "python ./.github/scripts/release.py prepare ${nextRelease.version} ${branch.name}",
        publishCmd:
          "python ./.github/scripts/release.py publish  ${nextRelease.version} ${branch.name}",
        successCmd:
          "python ./.github/scripts/release.py success  ${nextRelease.version} ${branch.name}",
      },
    ],
  ],
};
