# Vehicle Price Estimator

A web-based vehicle pricing application that estimates a vehicle's market value from attributes such as year, make, model, and mileage. It combines a user-facing search workflow with a backend data layer and regression-based price estimation.

## Features

- Search by vehicle year, make, model, and optional mileage.
- Estimate average market value from comparable listings.
- Display matching vehicle listings.
- Persist vehicle, dealer, attribute, listing, and status information in MySQL.
- Use regression analysis to account for mileage when estimating price.

## Architecture

```
User input
   ↓
Web interface
   ↓
Backend/API
   ↓
Vehicle + listing data
   ↓
Regression-based estimation
   ↓
Estimated price + comparable listings
```

## Technology

- Python / web backend components
- MySQL
- Regression-based price estimation
- HTML/CSS frontend components

Check the source tree for the exact framework and runtime configuration.

## Engineering focus

This project demonstrates how a conventional web application can combine relational data modeling with a lightweight machine-learning component to produce an explainable estimate rather than simply returning a stored price.

## Future improvements

- Add reproducible training/evaluation scripts.
- Report model metrics such as MAE and RMSE.
- Version the training dataset and model.
- Add automated API and database tests.
- Add input validation and clearer uncertainty/range reporting.
- Containerize the application for repeatable local deployment.
