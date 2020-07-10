import boto3
from boto3.dynamodb.conditions import Key, Attr

def insertRow(table, columns, primaryColumnName, entryNumber, attributeOne, attributeTwo):
    # test that we can insert a new row into table with a given primary key (entryNumber)

    response = table.put_item(
        Item={
            primaryColumnName: entryNumber,
            columns[0]: attributeOne,
            columns[1]: attributeTwo
        }
    )


def createTable(DB, tableName, primaryColumnName):

    table = DB.create_table(
        TableName=tableName,
        KeySchema=[
            {
                'AttributeName': primaryColumnName,
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': primaryColumnName,
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table

def deleteTable(table):
    table.delete()
    return table
