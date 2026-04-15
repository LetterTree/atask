#!/usr/bin/env node
"use strict";

const { spawnSync } = require("child_process");
const path = require("path");
const os = require("os");

function getBinaryPath() {
  const platform = os.platform();
  const arch = os.arch();

  if (arch !== "x64") {
    throw new Error(`atask: unsupported architecture '${arch}'. Only x64 is supported.`);
  }

  let pkgName, binName;
  if (platform === "linux") {
    pkgName = "@lettertree/atask-linux-x64";
    binName = "atask";
  } else if (platform === "darwin") {
    pkgName = "@lettertree/atask-darwin-x64";
    binName = "atask";
  } else if (platform === "win32") {
    pkgName = "@lettertree/atask-win32-x64";
    binName = "atask.exe";
  } else {
    throw new Error(`atask: unsupported platform '${platform}'. Supported: linux, darwin, win32.`);
  }

  try {
    const pkgDir = path.dirname(require.resolve(`${pkgName}/package.json`));
    return path.join(pkgDir, "bin", binName);
  } catch {
    throw new Error(
      `atask: could not find binary for platform '${platform}'.\n` +
      `Try reinstalling: npm install -g atask\n` +
      `Or run from source: pip install -e . && atask`
    );
  }
}

let binaryPath;
try {
  binaryPath = getBinaryPath();
} catch (err) {
  process.stderr.write(err.message + "\n");
  process.exit(1);
}

const result = spawnSync(binaryPath, process.argv.slice(2), {
  stdio: "inherit",
  windowsHide: true,
});

if (result.error) {
  process.stderr.write(`atask: failed to run binary: ${result.error.message}\n`);
  process.exit(1);
}

process.exit(result.status ?? 1);
