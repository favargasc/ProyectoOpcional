from elasticsearch import Elasticsearch


def main():

    es = Elasticsearch("http://localhost:9200")

    mapping = {
        'mappings': {
            'properties': {
                'fileName': {'type': 'keyword'},
                'contents': {'type': 'text'}
            }
        }
    }

    # es.indices.create(index='files', body=mapping)
    message = {
        'fileName': 'hola.txt',
        'contents': 'hello world!'
    }

    es.index(index='files', document=message)


if __name__ == "__main__":
    main()
