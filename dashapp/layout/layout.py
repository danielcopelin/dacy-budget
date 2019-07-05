import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_table.FormatTemplate as FormatTemplate
import pandas as pd


def layout(app):
    from app import db
    from app.models import Transaction

    def gen_conditionals_categories(category_column, sub_category_column):
        categories = {
            "Income": [
                "Salary",
                "Bonuses",
                "Gifts",
                "Dividends",
                "Savings",
                "Tax Return",
            ],
            "Insurance": [
                "Health Insurance",
                "Bike Insurance",
                "Car Insurance",
                "Pet Insurance",
                "Home Insurance",
                "Mortgage Insurance",
                "Life Insurance",
            ],
            "Housing": [
                "Mortgage",
                "Rent",
                "Accountant Fee",
                "Security",
                "Home maintenance",
            ],
            "Children": [
                "Childcare",
                "School Fees",
                "School activities",
                "Toys",
                "Allowance",
                "School supplies",
                "Babysitter",
                "Daycare",
            ],
            "Entertainment": [
                "Events",
                "Movies",
                "Charity Rides",
                "Experiences",
                "Games",
            ],
            "Health Beauty": [
                "Health Fitness",
                "Hairdresser",
                "Optical",
                "Medical",
                "Medication",
                "Dental",
            ],
            "Utilities": [
                "Gas Bill",
                "Water Bill",
                "Rates",
                "Electricity",
                "Phone Bill",
            ],
            "Memberships": [
                "Music subscription",
                "Internet",
                "Strava",
                "Google storage",
                "Media subscription",
            ],
            "Travel": ["Accommodation", "Flights", "Airbnb"],
            "Food": [
                "Cafe Coffee",
                "Resturants",
                "Takeaway",
                "Bars Pubs",
                "Groceries",
                "Alcohol",
            ],
            "Shopping": [
                "Bike Stuff",
                "Clothing Footwear",
                "Beauty",
                "Books",
                "Electronics Software",
                "Home supplies",
                "Birthday gifts",
                "Christmas gifts",
                "Wedding gifts",
                "Anniversary",
                "Other shopping",
            ],
            "Transportation": [
                "Uber Taxi",
                "Car Loan",
                "Car maintenance",
                "Car registration",
                "Bike maintenance",
                "Public transport",
                "Roadside assistance",
                "Parking",
            ],
            "Pets": ["Vet", "Emergency", "Pet supplies", "Pet sitter", "Pet food"],
            "Miscellaneous": ["Charity Donations", "Hecs", "Fines"],
        }

        conditional_dict = {
            category_column: {
                "options": [{"label": i, "value": i} for i in categories.keys()]
            }
        }

        sub_conditional_list = [
            {
                "if": {
                    "column_id": sub_category_column,
                    "filter_query": f'{{{category_column}}} eq "{category}"',
                },
                "options": [{"label": i, "value": i} for i in categories[category]],
            }
            for category in categories.keys()
        ]

        return conditional_dict, sub_conditional_list

    with app.server.app_context():
        transactions = db.session.query(Transaction)
        df = pd.read_sql(transactions.statement, transactions.session.bind)

    conditional_dict, sub_conditional_list = gen_conditionals_categories(
        "category", "sub_category"
    )

    layout = html.Div(
        [
            html.Div(id="hidden_div", style={"display": "none"}),
            html.Div(
                [
                    dash_table.DataTable(
                        id="transaction_table",
                        data=df.to_dict("rows"),
                        columns=[
                            {
                                "id": "id",
                                "name": "Hash",
                                "type": "text",
                                "hidden": True,
                            },
                            {"id": "date", "name": "Date", "type": "text"},
                            {"id": "narration", "name": "Narration", "type": "text"},
                            {
                                "id": "amount",
                                "name": "Amount",
                                "type": "numeric",
                                "format": FormatTemplate.money(2),
                            },
                            {
                                "id": "category",
                                "name": "Category",
                                "presentation": "dropdown",
                            },
                            {
                                "id": "sub_category",
                                "name": "Sub-category",
                                "presentation": "dropdown",
                            },
                        ],
                        style_cell={"padding": "5px"},
                        style_header={"backgroundColor": "white", "fontWeight": "bold"},
                        editable=True,
                        filter_action="native",
                        sort_action="native",
                        sort_mode="multi",
                        page_action="native",
                        page_current=0,
                        page_size=15,
                        dropdown=conditional_dict,
                        dropdown_conditional=sub_conditional_list,
                    )
                ],
                id="main",
            ),
        ]
    )

    return layout
