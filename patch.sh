#!/bin/bash
patch_dir=_patch/
# Loop through all .patch files and apply each one
for patch in ${patch_dir}*.patch; do
    git apply "$patch" --allow-empty
done