# from odoo import fields, models
from odoo import api, fields, models 
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError

class Book(models.Model):
    _name = 'library.book'
    _description = 'Book'
    _order = 'name, date_published desc'
    # _sql_constraints = [
    #     ('library_book_name_date_uq', # Constraint unique identifier 
    #     'UNIQUE (name, date_published)', # Constraint SQL syntax 
    #     'Book title and publication date must be unique.'), # Message
    #     ('library_book_check_date',
    #         'CHECK (date_published <= current_date)',
    #         'Publication date must not be in the future.'),
    #     ]
    # author_ids = fields.Many2many(
    #     'res.partner', string='Authors')
    name = fields.Char(
        'Title',
        default=None,
        index=True,
        help='Book cover title.',
        readonly=False,
        required=True,
        translate=False,
        )
    isbn = fields.Char('ISBN')
    active = fields.Boolean('Active?', default=True)
    date_published = fields.Date()
    image = fields.Binary('Cover')
    publisher_id = fields.Many2one(
        'res.partner', string='Publisher')
    # author_ids = fields.Many2many(
    #     'res.partner', string='Authors')
    author_ids = fields.Many2many(
        comodel_name='res.partner', # related model (required)
        # relation='library_book_res_partner_rel', # relation table name
        # column1='a_id', # rel table field for "this" record
        # column2='p_id', # rel table field for "other" record
        string='Authors') # string label text
        # 'res.partner', # related model (required) 
        # 'library_book_res_partner_rel', # relation table name to use 
        # 'a_id', # rel table field for "this" record 
        # 'p_id', # rel table field for "other" record 
        # 'Authors') # string label text
    book_type = fields.Selection(
        [('paper','Paperback'),
        ('hard','Hardcover'),
        ('electronic','Electronic'),
        ('other', 'Other')],
        'Type')
    notes = fields.Text('Internal Notes')
    descr = fields.Html('Description')
     # Numeric fields:
    copies = fields.Integer(default=1)
    avg_rating = fields.Float('Average Rating', (3, 2))
    price = fields.Monetary('Price', 'currency_id')
    currency_id = fields.Many2one('res.currency') # price helper
    # Date and time fields:
    date_published = fields.Date()
    last_borrow_date = fields.Datetime(
        'Last Borrowed On',
        # default='_default_last_borrow_date',
        )
     # Other fields:
    active = fields.Boolean('Active?')
    image = fields.Binary('Cover')
    publisher_country_id = fields.Many2one(
        'res.country', string='Publisher Country',
        compute='_compute_publisher_country',
        inverse='_inverse_publisher_country',
        search='_search_publisher_country',
        )
    publisher_country_related = fields.Many2one(
        'res.country', string='Publisher Country (related)',
        related='publisher_id.country_id',
        )

    @api.constrains('isbn')
    def _constrain_isbn_valid(self):
        for book in self:
            if book.isbn and not book._check_isbn():
                raise ValidationError('%s is an invalid ISBN' % book.isbn)

    def _inverse_publisher_country(self):
        for book in self:
            book.publisher_id.country_id = book.publisher_country_id
    
    def _search_publisher_country(self, operator, value):
        return [('publisher_id.country_id', operator, value)]

    @api.depends('publisher_id.country_id')
    def _compute_publisher_country(self):
        for book in self:
            book.publisher_country_id = book.publisher_id.country_id

    def _default_last_borrow_date(self):
        return fields.Datetime.now()

    # @api.multi
    def _check_isbn(self):
        self.ensure_one()
        digits = [int(x) for x in self.isbn if x.isdigit()]
        if len(digits) == 13:
            ponderations = [1, 3] * 6
            terms = [a * b for a, b in zip(digits[:12], ponderations)]
            remain = sum(terms) % 10
            check = 10 - remain if remain != 0 else 0
            return digits[-1] == check
    
    # @api.multi
    def button_check_isbn(self):
        for book in self:
           if not book.isbn:
               raise Warning('Please provide an ISBN for %s' % book.name)
           if book.isbn and not book._check_isbn():
               raise Warning('%s is an invalid ISBN' % book.isbn)
        return True