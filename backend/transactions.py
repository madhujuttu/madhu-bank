from backend.database import transactions_collection


def get_transactions(username):

    transactions = transactions_collection.find(
        {
            "username": username
        },
        {
            "_id": 0
        }
    ).sort(
        "date",
        -1
    )

    return list(transactions)


def get_all_transactions():

    transactions = transactions_collection.find(
        {},
        {
            "_id": 0
        }
    ).sort(
        "date",
        -1
    )

    return list(transactions)