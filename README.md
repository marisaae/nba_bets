# NBA Player Performance Analytics & Prediction Platform
[Live App Link](https://nba-bets-mm7o.onrender.com) – View the interactive dashboard

## Overview
An end-to-end data analytics application that aggregates historical and live player performance data from multiple external APIs to analyze metrics, visualize trends, and generate predictive estimates for future performance compared to their prop lines.

## Key Features
- Automated ingestion of historical and real-time player data
- Relational data modeling and storage in PostgreSQL
- Interactive performance visualizations
- Live market-based player propostion lines for upcoming games
- Predictive modeling for player statistics, enabling comparison to the betting propositions

## Data Sources
- Sports data APIs providing historical game logs, schedules, live updates, and proposition lines (e.g. Odds-API, NBA-API)
- Data is normalized and stored in a relational PostgreSQL database for consistent querying

## Tech Stack
- **Languages:** Python, SQL  
- **Databases:** PostgreSQL (Supabase)
- **Libraries & Tools:** pandas, Plotly, scikit-learn, SQLAlchemy, psycopg, Streamlit, pgAdmin  
- **Automation and Deployment:** Render (application hosting), Windows Task Scheduler (scheduled data refreshes)

## Analysis & Modeling
Raw player, game, and schedule data from multiple sources is normalized and integrated through multi-table SQL joins to produce analysis-ready datasets. Complex relational data is transformed into interpretable features using a combination of SQL and pandas, including game context, opponent information, home/away indicators, and rolling performance metrics. These engineered features are then used in scikit-learn models to generate forward-looking estimates of player statistics.

## Visualizations & Insights
Plotly visualizations highlight performance trends over time, and variance across different conditions, and comparisons against projections, supporting data-driven evaluation of player outcomes.

## Deployment
The application is deployed as a live web app using Render, with a cloud-hosted PostgreSQL database managed via Supabase. Data refresh processes are automated to support ongoing analysis.

## Future Improvements
- Expanding user controls to allow selection and comparison of different players and teams
- Adding user-configurable analysis parameters such as time ranges, selected performance metrics, and visualization options
- Evaluating and refining predictive models using additional contextual features (injuries, opposing team rest days, traveling distances)

