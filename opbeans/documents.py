from elasticsearch_dsl import Document, Integer, Keyword, Text, Object, Date, Float


class Customer(Document):
    full_name = Text(analyzer='snowball')
    email = Text(fields={'raw': Keyword()})
    company_name = Text(analyzer='snowball')
    address = Text(analyzer='snowball')
    postal_code = Text(analyzer='snowball', fields={'raw': Keyword()})
    city = Text(analyzer='snowball', fields={'raw': Keyword()})
    country = Text(analyzer='snowball', fields={'raw': Keyword()})
    total_orders = Integer()

    class Meta:
        index = 'py-customers'


customer_field = Object(properties={
    'full_name': Text(analyzer='snowball'),
    'id': Integer(),
})


class Order(Document):
    customer = customer_field
    created_at = Date()
    data = Object(properties={
        'total_amount': Float(),
        'cost': Float(),
        'margin': Float(),
    })

    class Meta:
        index = 'py-orders'
