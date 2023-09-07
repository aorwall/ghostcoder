## Context
Imagine you are developing a system for a mountain rescue team. The team is equipped with jump boots that can leap great heights but have a limit on total jumps. Your system needs to track the jumps across the mountain ranges. The mountain ranges are represented by an array of heights, and the team can move forward only.

Your task is to break down the problem and develop the tracking system for it.

## Requirements
* A MountainRange class that takes an array of mountain heights and jump capacity of the team.
* A method can_complete_mission() in the MountainRange class that returns a Boolean indicating whether the team can complete the mission from start to the end of the array.

## Constraints
* All inputs are integers.
* The array will have at least two elements but no more than 100.
* The jump capacity is a positive integer and can be up to 1000.
* The mountain heights are non-negative integers and can go up to 1000.
