from flask import render_template, flash, redirect, url_for, request
from app import application as app
from app import db
from app.forms import LoginForm, UploadForm, CategoriseForm, CategoriseButton, RemoveCategoryForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Transaction, CategoryRule
from werkzeug.urls import url_parse
import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import column, row, grid
from bokeh.models import ColumnDataSource, DataRange1d, CheckboxGroup, CustomJS, HoverTool, formatters
from bokeh.palettes import d3


def make_plot(source):
    plot = figure(x_axis_type="datetime", plot_height=600, plot_width=1000, tools="", toolbar_location=None)
    plot.title.text = "Montly Spend"

    plot.quad(top='top', bottom='bottom', left='left', right='right',
              fill_color='colour', line_color='black', source=source)

    hover = HoverTool(tooltips=[('Category', '@category'),
                                ('Month', '@MonthBegin{%Y-%m}'),
                                ('Net Spend', '@NetSpend{R0,0}')],
                    mode='mouse',
                    formatters=dict(MonthBegin= 'datetime'))

    plot.add_tools(hover)

    # fixed attributes
    plot.xaxis.axis_label = None
    plot.yaxis.axis_label = "Spend (R)"
    plot.axis.axis_label_text_font_style = "bold"
    plot.x_range = DataRange1d(range_padding=0.2)
    plot.grid.grid_line_alpha = 0.3

    return plot

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
@login_required
def index():
    form = CategoriseButton()
    cnx = app.config.get('SQLALCHEMY_DATABASE_URI')

    if form.validate_on_submit():
        rules = {}
        categories = [x[0] for x in db.session.query(CategoryRule.category.distinct()).all()]
        for cat in categories:
            cat_rules = CategoryRule.query.filter_by(category=cat).all()
            rules[cat] = []
            for rule in cat_rules:
                rules[cat].append({'str': rule.string_match,
                                   'date': rule.date_match,
                                   'exact': rule.exact_rule})
        
        df_transactions = pd.read_sql_query('''
            SELECT 
                *
            FROM 
                "transaction"''', cnx)

        df_transactions['transaction_date'] = pd.to_datetime(df_transactions['transaction_date'])
        df_transactions['transaction_date'] = df_transactions['transaction_date'].dt.date

        def categorise(name, date, categories):
            for category in categories:
                for rule in categories[category]:
                    if rule['exact']==True:
                        if rule['date']==None and rule['str']==name:
                            return category
                        if rule['date']==date and rule['str']==name:
                            return category
                    else:
                        if rule['date']==None and rule['str'] in name:
                            return category
                        if rule['date']==date and rule['str'] in name:
                            return category


        df_transactions['category'] = df_transactions.apply(lambda x: categorise(x['description'], x['transaction_date'], rules), axis=1)

        transactions = Transaction.query.all()
        for i, t in enumerate(transactions):
            t.category = df_transactions['category'].iloc[i]
                            
        db.session.commit()

    ###############################################
    # Create the plot
    ###############################################

    df_transactions = pd.read_sql_query('''
            SELECT 
                *
            FROM 
                "transaction"
            ORDER BY
                transaction_date DESC,
                description ASC''', cnx)

    df_transactions['transaction_date'] = pd.to_datetime(df_transactions['transaction_date'])
    df_transactions = df_transactions[df_transactions['transaction_date']>='2019-01-01']
    df_transactions['MonthBegin'] = df_transactions['transaction_date'] - pd.Timedelta('1d') * (df_transactions['transaction_date'].dt.day - 1)
    df = df_transactions.groupby(['MonthBegin', 'category']).agg({'debits': 'sum', 'credits': 'sum'}).reset_index()
    df['NetSpend'] = df['debits'] - df['credits']
    df['left'] = df['MonthBegin'] + pd.Timedelta(days=8)
    df['right'] = df['MonthBegin'] + pd.Timedelta(days=22)
    df['top'] = df['NetSpend'] 
    df['bottom'] = 0.0

    categories = sorted(df['category'].unique().tolist())

    for i, cat in enumerate(categories):
        idx = i
        while idx > 19:
            idx -= 20
        df.loc[df['category']==cat, 'colour'] = d3['Category20'][20][idx]
    
    df = df.set_index(['MonthBegin'])
    df = df.drop(['debits', 'credits'], axis=1)
    df.sort_index(inplace=True)
    source = ColumnDataSource(data=df)

    category = 'Groceries'
    
    df_filtered = df.copy()
    df_filtered.loc[df_filtered['category']!=category] = np.nan
    source_filtered = ColumnDataSource(data=df_filtered)

    plot = make_plot(source_filtered)

    callback = CustomJS(args=dict(source=source, source_filtered=source_filtered), code="""
        var chosen_idxs = cb_obj.active;
        var labels = cb_obj.labels;
        var month_sum = {};
        var category_bottom = {};
        var chosen_categories = [];
        for (var i = 0; i < chosen_idxs.length; i++) {
            chosen_categories.push(labels[chosen_idxs[i]]);
        }
        for (var i = 0; i < chosen_categories.length; i++) {
            for (var j = 0; j < source.data['category'].length; j++) {
                if (source.data['category'][j]==chosen_categories[i]) {
                    if (!month_sum.hasOwnProperty(source.data['MonthBegin'][j].toString())) {
                        month_sum[source.data['MonthBegin'][j].toString()] = 0.0;
                    }
                    if (!category_bottom.hasOwnProperty(i)) {
                        category_bottom[i] = {}
                    }
                    category_bottom[i][source.data['MonthBegin'][j].toString()] = JSON.parse(JSON.stringify(month_sum[source.data['MonthBegin'][j].toString()]));
                    month_sum[source.data['MonthBegin'][j].toString()] += Math.abs(source.data['NetSpend'][j]);
                }
            }
        } 
        for (var i = 0; i < source.data['category'].length; i++) {
            if (chosen_categories.includes(source.data['category'][i])) {
                source_filtered.data['category'][i] = source.data['category'][i];
                source_filtered.data['MonthBegin'][i] = source.data['MonthBegin'][i];
                source_filtered.data['NetSpend'][i] = source.data['NetSpend'][i];
                source_filtered.data['left'][i] = source.data['left'][i];
                source_filtered.data['right'][i] = source.data['right'][i];
                if (category_bottom[chosen_categories.indexOf(source.data['category'][i])].hasOwnProperty(source.data['MonthBegin'][i].toString())) {
                    source_filtered.data['bottom'][i] = category_bottom[chosen_categories.indexOf(source.data['category'][i])][source.data['MonthBegin'][i].toString()];
                } else {
                    source_filtered.data['bottom'][i] = 0.0;
                }
                source_filtered.data['top'][i] = source_filtered.data['bottom'][i] + Math.abs(source_filtered.data['NetSpend'][i]);
                if (source_filtered.data['NetSpend'][i] < 0.0) {
                    source_filtered.data['colour'][i] = '#ffffff';
                } else {
                    source_filtered.data['colour'][i] = source.data['colour'][i];
                }
            } else {
                source_filtered.data['category'][i] = undefined;
                source_filtered.data['MonthBegin'][i] = undefined;
                source_filtered.data['NetSpend'][i] = undefined;
                source_filtered.data['left'][i] = undefined;
                source_filtered.data['right'][i] = undefined;
                source_filtered.data['bottom'][i] = undefined;
                source_filtered.data['top'][i] = undefined;
                source_filtered.data['colour'][i] = undefined;
            } 
        }
        source_filtered.change.emit();
    """)

    category_select = CheckboxGroup(labels = categories, 
                                    active = [categories.index(category)])

    category_select.js_on_change('active', callback)
    plotgrid = grid([plot, category_select], ncols=2)

    ###############################################
    
    # Embed plot into HTML via Flask Render
    script, div = components(plotgrid)

    df_transactions = pd.read_sql_query('''
            SELECT 
                *
            FROM 
                "transaction"
            WHERE
                category IS NULL
            ORDER BY
                transaction_date DESC,
                description ASC''', cnx)

    return render_template('index.html', title='Home', table=df_transactions, form=form, script=script, div=div)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.csv_file.data
        account_holder = f.readline().decode()
        df = pd.read_csv(f, skiprows=0, index_col=False).fillna(0.0)
        account_holder = account_holder.split(':')[1][:14].strip()
        df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])
        df['Posting Date'] = pd.to_datetime(df['Posting Date'])
        df.columns = [x.lower().replace(' ', '_') for x in df.columns]
        df['account_holder'] = account_holder

        for idx, row in df.iterrows():
            t = Transaction(**row.to_dict())
            t_duplicate = Transaction.query.filter_by(transaction_date=t.transaction_date,
                posting_date=t.posting_date,
                description=t.description,
                debits=t.debits,
                credits=t.credits,
                balance=t.balance,
                account_holder=t.account_holder).first()

            if t_duplicate==None:
                db.session.add(t)

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('upload.html', form=form)

@app.route('/categorise', methods=['GET', 'POST'])
@login_required
def add_category_rule():
    form = CategoriseForm()
    remove_category_form = RemoveCategoryForm()

    if form.validate_on_submit():
        category = form.category.data
        string_match = form.string_match.data
        date_match = form.date_match.data
        exact_rule = form.exact_rule.data

        r = CategoryRule(category=category,
                         string_match=string_match,
                         date_match=date_match, 
                         exact_rule=exact_rule)
        db.session.add(r)
        db.session.commit()
        return redirect(url_for('add_category_rule'))

    if remove_category_form.validate_on_submit():
        remove_rule = CategoryRule.query.get(remove_category_form.id_to_remove.data)
        db.session.delete(remove_rule)
        db.session.commit()
        return redirect(url_for('add_category_rule'))

    cnx = app.config.get('SQLALCHEMY_DATABASE_URI')
    df = pd.read_sql_query('''
        SELECT 
            *
        FROM 
            category_rule
        ORDER BY id DESC''', cnx)

    return render_template('add_category_rule.html', 
                           table=df,
                           form=form,
                           remove_category_form=remove_category_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
