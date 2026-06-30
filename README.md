# Alberta TRM Financing Dashboard

This project packages a polished Streamlit dashboard for Treasury & Risk Management / Capital Markets financing analysis, with a focus on Alberta's public financing profile and the Director of Financing team's context.

## Purpose

The dashboard is designed for interview preparation and analytical demonstration. It presents:

- Executive KPI cards for borrowing requirements, maturities, and debt balances
- Borrowing trend and maturity-pressure visuals
- Term debt and money market views across currencies
- Recent issuance activity, public credit ratings, and potential recommendations

All figures are based on public Alberta Investor Relations / TRM materials and should be verified against source documents before official use.

## Project Structure

```text
.
|-- app.py
|-- requirements.txt
|-- README.md
`-- data
    |-- trm_financing_data.csv
    |-- borrowing_requirements.csv
    |-- debt_maturities.csv
    |-- term_debt_currency.csv
    |-- average_term_by_currency.csv
    |-- money_market_debt.csv
    |-- recent_issuance.csv
    |-- credit_ratings.csv
    `-- recommendations.csv
```

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub.
2. Sign in to Streamlit Community Cloud.
3. Create a new app and point it to this repository.
4. Set `app.py` as the entry point.
5. Deploy. Streamlit will install packages from `requirements.txt`.

## Future Expansion

This repository is structured for future enhancements such as:

- adding direct links to official Alberta source documents
- extracting tables directly from PDF source materials
- introducing automated refresh logic for public financing updates
- layering in risk, liquidity, and multi-currency analytics from official systems

## Disclaimer

For interview preparation and analytical demonstration only. Figures should be verified against source documents before official use.
