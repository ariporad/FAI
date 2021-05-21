# Fundamentals of Artificial Intelligence (FAI)

#### Brandeis University's COSI 101A

This repository contains my code from Brandeis University's Brandeis University: COSI 101A _Fundamentals of Artificial Intelligence_, which I took in Spring 2021 (referred to by me and me alone as the Olin-eqsue _FAI_, pronounced _/faye/_).

_**NOTE:** Academic dishonesty includes--among other things--submitting someone else's code as your own. Academic honesty is extremely important to me, and I expressly prohibit the use of any code in this repository in an academically dishonest way, for COSI 101A or any other course._

## [Homework 1: _Drive Ya' Nuts_](hw1/)

Homework 1 involved building an algorithm to solve puzzles in the following form (from [the assignment](hw1/assignment.pdf)):

> There are n+1 regular polygons with n sides, each a permutation of the n numbers (or colors or shapes) on each side. The problem is to arrange the polygons in a ring with one in the center, such that the numbers on each adjacent edge will match. In the commercial version, there are 7 pieces, each with 6 possible rotations, and hexagons tile the plane. But we can generalize. 4 triangles would fold up to a pyramid, 5 squares give you 5/6ths of a cube, 6 pentagons give you a bowl, and so on, even though 11 decagons or 13 dodecagons will not tile or fold up.

![Example solved 6th-order puzzle (ie. 7 hexagons)](hw1/example.png)

Documentation of my approach, along with the report ([Jupyter Notebook](hw1/report.ipynb), [PDF](hw1/report.pdf)) I thatturned in, can be found in the [`hw1/` folder](hw1/), as can [thoroughly-documented source code](hw1/main.py).

## [Homework 2: _Nannon_](hw2/)

Homework 2 involved building several algorithms to play [Nannon](https://nannon.com), a simplified version of backgammon:

![Nannon Rules](hw2/nannon-rules.jpg)

Documentation of my approach, along with the report ([Jupyter Notebook](hw2/src/report.ipynb), [PDF](hw2/report.pdf)) that I turned in, can be found in the [`hw2/` folder](hw2/), as can [thoroughly-documented source code](hw2/src).

## [Homework 3: Deep Flappy Bird](hw3/)

Homework 3 involved building a simulation of the game Flappy Bird and training a deep neural network to play it.

![Flappy Bird](hw3/flappy-bird.jpg)

Documentation of my approach, along with the report ([Jupyter Notebook](hw3/report.ipynb), [PDF](hw3/report.pdf)) that I turned in, can be found in the [`hw3/` folder](hw3/), as can [thoroughly-documented source code](hw3/env.py).
