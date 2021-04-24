import pandas
import numpy
import re
import nltk
from nltk.corpus import stopwords
from time import strftime
def populate(conn):
    nltk.download('stopwords')
    long_stop_words = (word for word in set(stopwords.words('english')) if len(word) > 3)
    # Read in .csv tables
    book_data = pandas.read_csv(r".\..\books_modified.csv")
    book_data_frame = pandas.DataFrame(book_data).rename(columns={'bookID': 'id'})
    num_books = len(book_data_frame['id'])
    user_data = pandas.read_csv(r".\..\mock_users.csv")
    user_df = pandas.DataFrame(user_data)
    num_users = len(user_df['id'])
    
    # Populate Books table:
    reduced_book_df = book_data_frame.drop(columns=['authors','average_rating', 'ratings_count', 'text_reviews_count']).rename(columns={'language_code': 'language','publication_date': 'pub_date'})
    random_prices = numpy.array(numpy.random.randint(0, 25, num_books)) + .99
    reduced_book_df['price'] = random_prices
    random_stocks = numpy.random.randint(0, 40, num_books)
    reduced_book_df['stock'] = random_stocks
    reduced_book_df.to_sql('Books', conn, if_exists='append',index=False)

    # Authors, keywords, ratings
    authors_df = pandas.DataFrame(columns=['id', 'name'])
    authorWrites_df = pandas.DataFrame()
    keyword_df = pandas.DataFrame(columns=['id', 'keyword'])
    bookRelatesTo_df = pandas.DataFrame()
    comments_df = pandas.DataFrame()
    num_keywords = 0; num_authors = 0; num_comments = 0; bookID_list = []
    for book in book_data_frame.itertuples():
        bookID_list.append(book.id)
        authors = book.authors.split('/')
        for author in authors:
            author_id = -1
            if author in authors_df.values:
                author_id = authors_df.loc[authors_df['name'] == author]['id']
            else:
                authors_df = authors_df.append({'id': int(num_authors), 'name': str(author)}, ignore_index=True)
                num_authors += 1
                author_id = num_authors
            authorWrites_df = authorWrites_df.append({'author_id': int(author_id), 'book_id': int(book.id)}, ignore_index=True)
        for keyword in book.title.split(" "):
            keyword = re.sub(r'[^\w]', '', keyword)
            if len(keyword) > 3 and keyword not in long_stop_words:
                keyword_id = -1
                if keyword in keyword_df.values:
                    keyword_id = keyword_df.loc[keyword_df['keyword'] == keyword]['id']
                else:
                    keyword_df = keyword_df.append({'id': int(num_keywords), 'keyword': str(keyword)}, ignore_index=True)
                    num_keywords += 1
                    keyword_id = num_keywords
                bookRelatesTo_df = bookRelatesTo_df.append({'keyword_id': int(keyword_id), 'book_id': int(book.id)}, ignore_index=True)
        if (book.average_rating > 0):
            ratings_cnt = book.ratings_count
            while (ratings_cnt > 1):
                comments_df = comments_df.append({'score': max(0, min(int(numpy.random.normal(book.average_rating*2, 1)), 10)), 'book_id': book.id, 'user_id': numpy.random.randint(1, num_users)}, ignore_index=True)
                num_comments += 1
                ratings_cnt /= 10
    authors_df.to_sql('Authors', conn, if_exists='append',index=False)
    authorWrites_df.to_sql('AuthorWrites', conn, if_exists='append',index=False)
    keyword_df.to_sql('Keywords', conn, if_exists='append',index=False)
    bookRelatesTo_df.to_sql('BookRelatesTo', conn, if_exists='append',index=False)
    comments_df.to_sql('Comments', conn, if_exists='append',index=False)

    # Populate Users, Customers, Addresses
    
    reduced_user_df = user_df.drop(columns = ['first_name','last_name','phone', 'street_number', 'street_name', 'apt_number', 'city', 'zip_code', 'region', 'country'])
    reduced_user_df.to_sql('Users', conn, if_exists='append',index=False)
    reduced_customer_df = user_df.drop(columns = ['email','username','street_number', 'street_name', 'apt_number', 'city', 'zip_code', 'region', 'country']).rename(columns={'id': 'user_id'})
    reduced_customer_df.to_sql('Customers', conn, if_exists='append',index=False)
    reduced_address_df = user_df.drop(columns = ['first_name','last_name','email','username','phone']).rename(columns={'id': 'user_id'})
    reduced_address_df.to_sql('Addresses', conn, if_exists='append',index=False)

    # Populate Orders
    num_orders = 0
    num_items = 0
    orders_df = pandas.DataFrame()
    items_df = pandas.DataFrame()
    userTrusts_df = pandas.DataFrame()
    order_quarter = 0
    for user in user_df.itertuples():
        while numpy.random.random() > .5:
            trust = {'user_id': user.id, 'trusts': numpy.random.randint(1,num_users), 'value':[-1,1][numpy.random.randint(2)]}
            userTrusts_df = userTrusts_df.append(trust,ignore_index=True)
        while numpy.random.random() > .9:
            num_orders += 1
            #order = numpy.array([num_orders, order_quarter, user[0], user[0]], dtype=object)
            order = {'id': num_orders, 'order_quarter': order_quarter,'time_fulfilled': strftime("%Y-%m-%d %H:%M:%S"), 'ships_to': user.id, 'placed_by': user.id}
            while True:
                num_items += 1
                random_book_id = numpy.random.choice(bookID_list)
                quantity = numpy.random.randint(1, 6)
                #item = numpy.array([num_items, reduced_book_df.iloc[random_book_id]['price'], quantity, random_book_id, num_orders], dtype=object)
                item = {'id': num_items, 'quantity': quantity, 'book_id': random_book_id, 'order_id': num_orders}
                items_df = items_df.append(item, ignore_index=True)
                if numpy.random.random() > .5:
                    break
            orders_df = orders_df.append(order, ignore_index=True)
    userTrusts_df.to_sql('Trusts', conn, if_exists='append',index=False)
    orders_df.to_sql('Orders', conn, if_exists='append',index=False)
    items_df.to_sql('OrderItems', conn, if_exists='append',index=False)

    
