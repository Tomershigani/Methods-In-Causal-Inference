# Methods In Causal Inference - Causal Impact of the Tel Aviv Light Rail on Property Prices

## Project Overview
This project investigates the causal impact of the Tel Aviv Light Rail’s Red Line on property prices in its vicinity. The Red Line, running through key municipalities in Gush Dan, offers an opportunity to analyze the effect of new transportation infrastructure on housing values. We collected property transaction data from public real estate databases and enriched it with address information using web scraping techniques.

## Data Collection
We obtained data on real estate transactions through public government sources. Given the structure of the data, we used a Selenium Python script to map each property by its "gush-helka" (plot ID) to its full address via the Israeli Centre for Mapping. To facilitate grouping by distance, we used Google API services to determine the proximity of each property to Red Line stations. This allowed us to categorize properties into three distance bands: 0-500m, 500-1000m, and 1000m+.

## Methodology
To estimate the causal effect, we relied on several analytical techniques:
- **ATE Calculation** using the Rubin-Neyman framework to measure average treatment effects across distance groups.
- **Propensity Score Matching (PSM)** and **Mahalanobis Distance Matching** for balancing treatment and control groups, enhancing comparability.
- **Regression Discontinuity Design (RDD)** to assess impact near predefined proximity thresholds.

These methods account for confounding variables like year of construction, property area, and number of bedrooms to control for baseline differences in property characteristics across distance bands.

## Key Findings
Preliminary findings suggest a positive impact of the Red Line on property values within 500m of stations, with diminishing effects as distance increases. However, variability in results and non-significant findings in some cases indicate that further analysis with larger datasets is needed for more definitive conclusions.

## Limitations
Data limitations, including address mapping challenges and pre-existing differences among properties, contribute to some residual confounding. Additionally, market-wide trends during the study period may influence our estimates.

## Conclusion
While proximity to the metro shows potential for enhancing property values, this effect is context-sensitive and varies across distance bands. Our study underscores the importance of comprehensive causal inference designs for urban infrastructure projects.

![image](https://github.com/user-attachments/assets/1dd49c8d-1676-47e5-bbac-a4a6ad1d3d26)
