from django.core.paginator import Page, Paginator, InvalidPage

class SearchPaginator(Paginator):    
    def __init__(self, hits):
        self.hits = hits

    @property
    def num_pages(self):
        found = len(self.hits)
        if found:
            rem = self.hits.total % len(self.hits)
            div = self.hits.total / len(self.hits)
            return div if rem == 0 else div + 1
        else:
            return 0

    @property
    def page_range(self):
        return range(1, self.num_pages + 1)

    def has_next(self):
        return self.page < self.num_pages

    def has_previous(self):
        return self.page > 1

    def start_index(self):
        return self.page_range[0]

    def end_index(self):
        return self.page_range[-1]

    def next_page_number(self):
        if self.page >= self.num_pages:
            raise InvalidPage()

    def page(self, page):
        return Page(self.hits, page, self)    


