from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, DecimalField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class UploadForm(FlaskForm):
    csv_file = FileField(validators=[FileRequired()])
    submit = SubmitField('Upload')

class CategoriseForm(FlaskForm):
    categories = [('ATM/Cash', 'ATM/Cash'),
        ('Bitcoin', 'Bitcoin'),
        ('Charity', 'Charity'),
        ('Child Expenses', 'Child Expenses'),
        ('Clothing', 'Clothing'),
        ('Coffee/Lunch', 'Coffee/Lunch'),
        ('Education', 'Education'),
        ('Entertainment', 'Entertainment'),
        ('General Merchandise', 'General Merchandise'),
        ('Gifts', 'Gifts'),
        ('Groceries', 'Groceries'),
        ('Healthcare/Medical', 'Healthcare/Medical'),
        ('Hobbies', 'Hobbies'),
        ('Holidays/Travel', 'Holidays/Travel'),
        ('Home Improvement', 'Home Improvement'),
        ('Home Maintenance', 'Home Maintenance'),
        ('Home Sale/Purchasing/Moving', 'Home Sale/Purchasing/Moving'),
        ('Insurance', 'Insurance'),
        ('Interest', 'Interest'),
        ('Kylie Transfer', 'Kylie Transfer'),
        ('Mortage Transfer', 'Mortage Transfer'),
        ('Mortages', 'Mortages'),
        ('Personal Care', 'Personal Care'),
        ('Pumbaa', 'Pumbaa'),
        ('Rent', 'Rent'),
        ('Restaurants', 'Restaurants'),
        ('Salary', 'Salary'),
        ('Savings', 'Savings'),
        ('Service Charges', 'Service Charges'),
        ('Taxes', 'Taxes'),
        ('Telephone Services', 'Telephone Services'),
        ('Transfer', 'Transfer'),
        ('Transport/Fuel', 'Transport/Fuel'),
        ('Uncategorised', 'Uncategorised'),
        ('Utilities', 'Utilities'),
        ('Vehicle Expenses', 'Vehicle Expenses'),
        ('Work Related', 'Work Related')
    ]

    category = SelectField('Category', choices=categories)
    string_match = StringField('(Sub)string Match', validators=[DataRequired()])
    date_match = DateField('Date Match', validators=[Optional()])
    exact_rule = BooleanField('Exact Rule')
    max_amount = DecimalField('Max Amount')
    submit = SubmitField('Create Rule')

class RemoveCategoryForm(FlaskForm):
    id_to_remove = IntegerField('Id', validators=[DataRequired()])
    submit = SubmitField('Delete Row')

class CategoriseButton(FlaskForm):
    submit = SubmitField('Recategorise')