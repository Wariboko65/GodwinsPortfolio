#!/bin/bash
# Installs the motion/video agent skills into ~/.claude/skills (and ~/.agents/skills) for every session:
# iart-ai motion-skills (19 packs) and Remotion's official skills. Safe to re-run; it refreshes them.
# lemo-opuscar, OneTake and HyperFrames are installed separately and are left alone here.
set -u
D=${HOME}/.claude/skills; A=${HOME}/.agents/skills
mkdir -p "$D" "$A"
T=$(mktemp -d)
PACKS="tiktok-video-skills text-message-video-skills youtube-video-skills ecommerce-video-skills ad-video-skills
data-animation-skills explainer-video-skills map-animation-skills web-animation-skills motion-design-skills
kinetic-typography-skills freelance-motion-skills webgl-animation-skills manim-skills generative-illustration-skills
javascript-animation-skills b-roll-skills talking-head-skills lower-thirds-skills"   # lower-thirds last: its version wins
n=0
install_from() {  # every folder holding a SKILL.md under $1/skills becomes ~/.claude/skills/<name>
  for s in "$1"/skills/*/; do
    [ -f "$s/SKILL.md" ] || continue
    name=$(basename "$s"); rm -rf "$D/$name"; cp -r "$s" "$D/$name"; ln -sfn "$D/$name" "$A/$name"; n=$((n + 1))
  done
}
for p in $PACKS; do
  git clone -q --depth 1 "https://github.com/iart-ai/$p.git" "$T/$p" 2>/dev/null && install_from "$T/$p" || echo "! could not fetch $p"
done
git clone -q --depth 1 https://github.com/remotion-dev/skills.git "$T/remotion" 2>/dev/null && install_from "$T/remotion" || echo "! could not fetch remotion skills"
rm -rf "$T"
echo "installed $n skills into $D"
