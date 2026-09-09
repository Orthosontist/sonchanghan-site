#!/usr/bin/env bash
# Extract the supplied clinical panels at native resolution; no retouching.
set -euo pipefail
cd "$(dirname "$0")/../images/cases/224298737298"
mkdir -p cropped
convert 02-pre-treatment.png -crop 1037x692+11+156 +repage cropped/pre-treatment.png
convert 03-diagnosis-plan.png -crop 600x308+295+6 +repage cropped/ct.png
convert 04-treatment-course.png -crop 1035x653+31+257 +repage cropped/treatment-course.png
convert 09-post-treatment.png -crop 1037x692+28+78 +repage cropped/post-treatment.png
