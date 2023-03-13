# Description

An investor can invest his money in different financial instruments. One of them are Loans, money borrowed to customers or businesses. To simplify the situation, we’ll say that each loan has one single expected repayment (this is sometimes called bullet repayment). This means that the investor invests some money in the loan (lends money to the customer/business) and then expects a repayment on the maturity date of that loan. 

## Assumptions

- A Loan can only be created using a CSV.

- All the endpoints (except ```/token```) have an Authorization and Authentication level.

- The statistics endpoints have cached information unless a new CashFlow or Loan is created.

- You may have Python (3.9+) and Docker installed.

## Stack


- Python 3.8
- Django 4.1
- DRF 3.14 
- DRF SimpleJWT 5.2.2
- SQLite 3
- Redis
- Celery
- Pyxirr

All the libraries you can check at `requirements.txt`



## Project Set Up

Clone the Project

```bash
  git clone https://github.com/luizgtvsilva/investor_api.git
```

```bash
  cd investor_api
```

Create a container

```bash
  docker-compose build
```

Up the application

```bash
  docker-compose up
```

To create a INVESTOR or ANALYST user, you need a ADMIN user created, so you need open the Docker Terminal and run

```bash
  python manage.py createsuperuser
```


## API

#### Login
Only an ADMIN or an INVESTOR can create other users, but at this moment you may only have an ADMIN user created, so use the username and password created in the SET UP section.

```http
  POST /token/
```
Roles accepted: ADMIN, ANALYST, INVESTOR.

| Param               | Type                                                |
| ----------------- | ---------------------------------------------------------------- |
| body       | text/json |


input:
```
{
	"username":"admin",
	"password":"admin"
}
```

output:
```
{
	"refresh": "<refresh token here>",
	"access": "<access token here>"
}
```


#### Create a user

```http
  POST /users/
```
Roles accepted: ADMIN, INVESTOR.


| Param               | Type                                                |
| ----------------- | ---------------------------------------------------------------- |
| body       | text/json |
| header       | Bearer Token |


input:
```
{
    "username": "investor",
    "email": "john.doe@example.com",
    "password": "investor",
    "is_investor": true,
    "is_analyst": false
}
```

output:
```
{
	"id": 2,
	"username": "investor",
	"email": "john.doe@example.com",
	"is_investor": true,
	"is_analyst": false
}
```


#### Upload CSV

```http
  POST /csv/upload/
```
Roles accepted: ADMIN, INVESTOR.

| Param               | Type                                                |
| ----------------- | ---------------------------------------------------------------- |
| body       | multipart/file |
| header       | Bearer Token |


input:
```
    loans.csv
    cash_flow.csv
```

output:
```
{
	"message": "Process started."
}
```


#### Create a CashFlow - Repayment

```http
  POST /cashflows/
```
Roles accepted: ADMIN, INVESTOR.

| Param               | Type                                                |
| ----------------- | ---------------------------------------------------------------- |
| body       | text/json |
| header       | Bearer Token |


input:
```
  {
    "loan_identifier": "L103",
    "reference_date": "2021-05-01",
    "type": "Repayment",
    "amount": 77000
  }
```

output:
```
{
	"id": 5,
	"reference_date": "2021-05-01",
	"type": "Repayment",
	"amount": 77000.0,
	"loan_identifier": "L103"
}
```


#### Statistics - Basic View

```http
  GET /statistics/basic/
```
Roles accepted: ADMIN, ANALYST, INVESTOR.


| Param               | Type                                                |
| ----------------- | ---------------------------------------------------------------- |
| header       | Bearer Token |


output:
```
{
	"number_of_loans": 3,
	"total_invested_amount": 231000.0,
	"current_invested_amount": 76000.0,
	"total_repaid_amount": 255120.0,
	"average_realized_irr": 7.169663038705743
}
```

#### Statistics - Chart View

Open it into a web browser to get a better experience.

```http
  GET /statistics/chart/
```
Roles accepted: ADMIN, ANALYST, INVESTOR.

| Param               | Type                                                |
| ----------------- | ---------------------------------------------------------------- |
| header       | Bearer Token |


#### View CashFlows

```http
  GET /cashflows/<optional: cash_flow id>/
```
Roles accepted: ADMIN, ANALYST, INVESTOR.

| Param               | Type                                                |
| ----------------- | ---------------------------------------------------------------- |
| header       | Bearer Token |


output:
```
[
	{
		"id": 1,
		"reference_date": "2021-05-01",
		"type": "Funding",
		"amount": -100000.0,
		"loan_identifier": "L101"
	},
	{
		"id": 2,
		"reference_date": "2021-06-03",
		"type": "Funding",
		"amount": -55000.0,
		"loan_identifier": "L102"
	},
  ...
]
```

You can also filter by any attribute, using a QueryParam with the key:value of that attribute, like:
```http
  GET /cashflows/?loan_identifier=L103
```

Should return:
```
[
	{
		"id": 3,
		"reference_date": "2021-07-04",
		"type": "Funding",
		"amount": -76000.0,
		"loan_identifier": "L103"
	}
]
```

#### View Loans

```http
  GET /loans/<optional: loan id>/
```
Roles accepted: ADMIN, ANALYST, INVESTOR.

| Param               | Type                                                |
| ----------------- | ---------------------------------------------------------------- |
| header       | Bearer Token |


output:
```
[
  {
		"identifier": "L102",
		"issue_date": "2021-06-01",
		"total_amount": 55000.0,
		"rating": 3,
		"maturity_date": "2021-10-01",
		"total_expected_interest_amount": 30.0,
		"investment_date": "2021-06-03",
		"invested_amount": 55000.0,
		"expected_interest_amount": 30.0,
		"is_closed": true,
		"expected_irr": 0.0016600148960397854,
		"realized_irr": 0.0016327793325660847,
		"cash_flows": [
			{
				"id": 2,
				"reference_date": "2021-06-03",
				"type": "Funding",
				"amount": -55000.0,
				"loan_identifier": "L102"
			},
			{
				"id": 7,
				"reference_date": "2021-10-03",
				"type": "Repayment",
				"amount": 55030.0,
				"loan_identifier": "L102"
			}
		]
	},
	{
		"identifier": "L103",
		"issue_date": "2021-07-01",
		"total_amount": 100000.0,
		"rating": 2,
		"maturity_date": "2021-12-01",
		"total_expected_interest_amount": 50.0,
		"investment_date": "2021-07-04",
		"invested_amount": 76000.0,
		"expected_interest_amount": 38.0,
		"is_closed": false,
		"expected_irr": 0.0012171026703733318,
		"realized_irr": null,
		"cash_flows": [
			{
				"id": 3,
				"reference_date": "2021-07-04",
				"type": "Funding",
				"amount": -76000.0,
				"loan_identifier": "L103"
			}
		]
	}
]
```

You can also filter by any attribute, using a QueryParam with the key:value of that attribute, like:
```http
  GET /loans?identifier=L103
```

Should return:
```
[
	{
		"identifier": "L103",
		"issue_date": "2021-07-01",
		"total_amount": 100000.0,
		"rating": 2,
		"maturity_date": "2021-12-01",
		"total_expected_interest_amount": 50.0,
		"investment_date": "2021-07-04",
		"invested_amount": 76000.0,
		"expected_interest_amount": 38.0,
		"is_closed": false,
		"expected_irr": 0.0012171026703733318,
		"realized_irr": null,
		"cash_flows": [
			{
				"id": 3,
				"reference_date": "2021-07-04",
				"type": "Funding",
				"amount": -76000.0,
				"loan_identifier": "L103"
			}
		]
	}
]
```







## Tests


The project has a 70% coverage.
You can check all in ```investor_api/tests/```

Run to get the report:
```bash
  coverage run --source='.' manage.py test
```
Then you can check the HTML in your web browser:
```bash
  coverage html
```