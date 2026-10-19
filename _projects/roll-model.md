---
title: Roll Model
theme: robot-learning
status: active
featured: true
order: 1
summary: "A robotic arm that picks up whichever die I point at. orange-bot runs the arm, and friday, a planner, decides what to pick, checks each attempt and tries again when it fails."
code: code goes public with the first post
cast:
  - {name: orange-bot, role: the policy}
  - {name: friday, role: the brain}
  - {name: SO-101, role: the arm}
media:
  video: /assets/media/roll-model/pick-place.mp4
  poster: /assets/media/roll-model/pick-place.jpg
  alt: "Overhead view: the arm picks the die marked with a magenta X and places it on a cyan ring."
  caption: "Self-play on 9 Oct 2026, sped up 2×. It picks the die with the X and sets it on the ring. This one worked; in that round, 6 of 10 made it onto the ring."
# The series, in order. A published post with `project: roll-model` and the same `series_order`
# replaces its planned entry.
planned:
  - {order: 0, title: Meet orange-bot, summary: "How I set up the arm so a policy could learn, and the three camera setups it took. I keep this one updated as the rig changes."}
  - {order: 1, title: "Point, pick, place (almost)", summary: "Teaching an SO-101 to pick up the die I mark and put it down where I mark."}
  - {order: 2, title: Practice without me, summary: "Rewards, self-play and reinforcement learning on the real arm."}
  - {order: 3, title: Think before you pick, summary: "Getting the robot to predict what will happen before it acts, on hardware this small."}
---
orange-bot is the policy that drives my SO-101 arm, a SmolVLA I fine-tuned on demonstrations I
recorded myself. Mark a die with an X and it picks that one up. Now it can put it down where it's
told, too.

friday is the part that thinks. It looks at the table, chooses which die to mark and where it should
go, watches each attempt and retries the ones that failed. It never moves a motor itself.

The posts build on each other. First, getting a policy to work at all and measuring it properly.
Then adding friday. Then letting the arm practise on its own, and finally world models.
