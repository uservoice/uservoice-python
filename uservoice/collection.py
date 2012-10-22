PER_PAGE = 500
class Collection:
    def __init__(self, client, query, limit=2**60):
        self.client = client
        self.query = query
        self.limit = limit
        self.per_page = min(self.limit, PER_PAGE)
        self.pages = {}
        self.response_data = None

    def __len__(self):
        if not self.response_data:
            try:
                self[0]
            except IndexError:
                pass
        return min(self.response_data['total_records'], self.limit)

    def __getitem__(self, i):
        if i == 0 or (i > 0 and i < len(self)):
            return self.load_page(int(i/float(PER_PAGE)) + 1)[i % PER_PAGE]
        else:
            raise IndexError

    def __iter__(self):
        for index in range(len(self)):
            yield self[index]

    def load_page(self, i):
        if not i in self.pages:
            url = self.query
            if '?' in self.query:
                url += '&'
            else:
                url += '?'
            result = self.client.get(url + "per_page=" + str(self.per_page) + "&page=" + str(i))

            if 'response_data' in result:
                self.response_data = result.pop('response_data')
                if len(result.values()) > 0:
                    self.pages[i] = result.values()[0]
            else:
                raise uservoice.NotFound.new('The resource you requested is not a collection')
        return self.pages[i]

