ratesocccer
===========

Rate soccer teams using the Glicko rating system.

The first number is the mean rating, and the second is the standard deviation.
The numbers here are ordered by `mean - 3*stdev`, giving a conservative 95% certain estimate that a team is
*at least* that good. That's why you might see a team (like Roma) behind a team with a lower mean score
(Napoli), because the rating system is more sure of Napoli.

The link to the data is from my [soccerdata](https://github.com/llimllib/soccerdata) project

You should be able to see the current rankings [here](http://billmill.org/ratesoccer).
