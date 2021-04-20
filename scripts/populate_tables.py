import pandas
import numpy
def populate(conn):
    
    # Populate Books table:
    book_data = pandas.read_csv(r".\..\books_modified.csv")
    book_data_frame = pandas.DataFrame(book_data)
    reduced_book_df = book_data_frame.drop(columns=['authors','average_rating', 'ratings_count', 'text_reviews_count']).rename(columns={'bookID': 'id','language_code': 'language','publication_date': 'pub_date'})
    num_books = len(reduced_book_df['id'])
    random_prices = numpy.array(numpy.random.randint(0, 25, num_books)) + .99
    reduced_book_df['price'] = random_prices
    random_stocks = numpy.random.randint(0, 40, num_books)
    reduced_book_df['stock'] = random_stocks
    reduced_book_df.to_sql('Books', conn, if_exists='append',index=False)
    # Authors
    authors_df = pandas.DataFrame()
    authorWrites_df = pandas.DataFrame()
    num_authors = 0
    for book in book_data_frame.itertuples():
        authors = book.authors.split('/')
        for author in authors:
            authot_id = 0
            if author not in authors_df.name:
                authors_df = authors_df.append({'id': num_authors, 'name': author}, ignore_index=True)
                num_authors += 1
                author_id = num_authors
            else:
                author_id = authors_df.loc[authors_df['name'] == author]
            authorWrites_df = authorWrites_df.append({'author_id': author_id, 'book_id': book.id})

    # Populate Users, Customers, Addresses
    user_data = pandas.read_csv(r".\..\mock_users.csv")
    user_df = pandas.DataFrame(user_data)
    num_users = len(user_df['id'])
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
    for user in user_df.itertuples():
        while numpy.random.random() > .9:
            num_orders += 1
            order_quarter = 0
            #order = numpy.array([num_orders, order_quarter, user[0], user[0]], dtype=object)
            order = {'id': num_orders, 'order_quarter': order_quarter, 'ships_to': user.id, 'placed_by': user.id}
            print(order)
            while True:
                num_items += 1
                random_book_id = numpy.random.randint(1, num_books)
                quantity = numpy.random.randint(1, 6)
                #item = numpy.array([num_items, reduced_book_df.iloc[random_book_id]['price'], quantity, random_book_id, num_orders], dtype=object)
                item = {'id': num_items, 'price': reduced_book_df.iloc[random_book_id]['price'], 'quantity': quantity, 'book_id': random_book_id, 'order_id': num_orders}
                items_df = items_df.append(item, ignore_index=True)
                if numpy.random.random() > .5:
                    break
            orders_df = orders_df.append(order, ignore_index=True)
    print(orders_df)
    orders_df.to_sql('Orders', conn, if_exists='append',index=False)
    items_df.to_sql('OrderItems', conn, if_exists='append',index=False)

    
