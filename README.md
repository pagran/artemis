# Artemis Flight History
![GitHub last commit (branch)](https://img.shields.io/github/last-commit/pagran/artemis/data)
![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/pagran/artemis/Deploy%20to%20Pages/data)

> Project is unofficial and not affiliated with NASA

## [Online viewer link](https://pagran.github.io/artemis/)

A project created for recording historical data about [Artemis I](https://www.nasa.gov/specials/artemis-i)

# How it works

1. Special server automatically collects raw data ([link](https://s3.us-east-1.amazonaws.com/nasa-jsc-public/Orion/mission/Orion_flight104_mission.txt)) every few seconds 
2. Once an hour it uploads collected data to repository in [data](https://github.com/pagran/artemis/tree/data) branch.
3. Push automatically launches a [Github Action](https://github.com/pagran/artemis/actions) that processes data and deploys the [Github Page](https://pagran.github.io/artemis/)


# Links
 - [Online Viewer](https://pagran.github.io/artemis/)
 - [NASA](https://www.nasa.gov)
 - [Official tracker](https://www.nasa.gov/specials/trackartemis/)
 - [About mission](https://www.nasa.gov/specials/artemis-i/)
 - [Parameter description](https://s3.us-east-1.amazonaws.com/nasa-jsc-public/Orion/mission/parameter_key.txt)
 - [Historical data (.csv)](https://pagran.github.io/artemis/data.csv.gz)