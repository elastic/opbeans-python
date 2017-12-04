from elasticsearch_dsl import DocType, Integer, Keyword, Text


class Customer(DocType):
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

    def save(self, **kwargs):
        super(Customer, self).save(**kwargs)