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
    orders_df = pandas.DataFrame()
    items_df = pandas.DataFrame()
    for user in user_df:
        while numpy.random.random() > .5:
            num_orders += 1
            order_quarter = 0
            order = numpy.array([num_orders, order_quarter, user['id'], user['id']], dtype=object)
            num_items = 0
            while True:
                num_items += 1
                random_book_id = numpy.random.randint(1, num_books)
                item = numpy.array([num_items, reduced_book_df.iloc[random_book_id]['price'], quantity, random_book_id, num_orders], dtype=object)
                if numpy.random.random() > .5:
                    break
                items_df.insert(item, columns=['id', 'price', 'quantity', 'book_id', 'order_id'])
            orders_df.insert(order, columns=['id', 'order_quarter', 'ships_to', 'placed_by'])
        orders_df.to_sql('Orders', conn, if_exists='append',index=False)
        items_df.to_sql('OrderItems', conn, if_exists='append',index=False)

    
