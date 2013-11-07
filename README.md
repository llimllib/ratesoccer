ratesocccer
===========

Rate soccer teams using the Glicko rating system.

The first number is the mean rating, and the second is the standard deviation.
The numbers here are ordered by `mean - 3*stdev`, giving a conservative 95% certain estimate that a team is
*at least* that good. That's why you might see a team (like Roma) behind a team with a lower mean score
(Napoli), because the rating system is more sure of Napoli.

The link to the data is from my [soccerdata](https://github.com/llimllib/soccerdata) project

Here's what it thinks the top 50 are:

* Bayern Munich 1902.37 137.68
* Napoli 1861.01 130.30
* AS Roma 1950.08 160.43
* Atletico Madrid 1920.24 151.83
* Arsenal 1856.53 133.55
* Real Madrid 1852.03 134.11
* Barcelona 1888.08 146.38
* Borussia Dortmund 1827.36 126.15
* Paris Saint-Germain 1773.00 131.77
* Lille 1726.69 119.75
* Juventus 1777.39 137.98
* Bayer Leverkusen 1703.32 127.19
* Internazionale 1724.13 136.81
* Chelsea 1708.38 131.58
* Everton 1706.83 131.97
* Fiorentina 1692.53 134.19
* AS Monaco 1699.65 136.94
* Tottenham Hotspur 1677.09 131.74
* Hellas Verona 1650.89 128.11
* Manchester United 1642.83 126.03
* Manchester City 1648.32 129.22
* Athletic Bilbao 1625.55 122.23
* Borussia Monchengladbach 1605.30 128.96
* Liverpool 1638.56 143.92
* Southampton 1626.03 140.77
* Nantes 1564.27 120.30
* Villarreal 1599.81 133.48
* Schalke 04 1576.21 125.63
* Stade de Reims 1573.81 125.03
* Getafe 1559.87 124.10
* VfL Wolfsburg 1569.75 128.22
* Real Sociedad 1500.27 110.59
* Bordeaux 1499.45 114.30
* Levante 1518.99 122.41
* Granada 1515.24 122.36
* Marseille 1467.68 110.28
* Guingamp 1493.89 120.76
* Bastia 1495.75 121.42
* Toulouse 1500.44 123.35
* Montpellier 1477.65 115.82
* Espanyol 1510.23 129.40
* Hull City 1514.50 131.55
* Stade Rennes 1475.88 119.68
* Nice 1476.51 120.07
* Hertha Berlin 1496.56 126.88
* Newcastle United 1534.25 139.60
* Evian Thonon Gaillard 1455.81 116.73
* AC Milan 1484.31 126.90
* Lyon 1434.47 111.43
* Aston Villa 1484.39 128.55
