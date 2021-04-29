# WebBookstore

How to deploy your system, including information like system environment, dependent software, steps/scripts to start your systems, etc.
Also, it should include where to find and how to use each of your functionalities.

This webapp is written for CMPSC 431W @ psu with Dong Xie for Spring 2021
This app uses Flask on Python with a SQLite Database to run a Bootstrap Frontend.

To use the webapp:
1. Download the master
2. Navigate to /webserver
3. Run app.py with Python3
4. Runs on http://127.0.0.1:5000/ by default

For issues with the data stored in database:
1. Navigate to /scripts
2. Run rebuild.py with Python3
3. Wait for a while as the tables are fully populated with mock data

To use the website:
Accessing the website will redirect users to the homepage.
From the Navigation Bar:
You may browse through popular books, as described by the number of random orders that have been generated, or highest rated books, or search for a book.
Create a new user using button on homepage, or link under drop down.
Signed in, a user may use the dropdown to view their cart, orders, comments, trusted users, and customer information, or logout.

Search will occur on the fields that have been filled in, based off of a given sorting order by the user.
While browsing books, a user can select a book to view.
On the book's page, users may view comments, or leave a comment.
The user may select an author, where they will see the author's books, books by 1-degree authors, and books by 2-degree authors.
The number of books in stock will be dispalyed, as well as the price, any sales on the book, and a button to order the book.
This adds the book to the user's cart. The user may add multiple books to their cart, and modify quantities.
If the user has an address stored, they may select that address and order all the books in their cart.

To login as manager, use username "admin" and password "pass"
On the homepage their will be a new button, "Manager Panel". Click this for exclusive manager functionality.
Books may be created from this panel.
Book statistics can also be fetched, by author, book or publisher, as well as any Sales in the store. Sales may be added/updated from the Sales page.
Users may be fetched, with all of their data, as well as access to update the user. Here, a manager can create other managers or employees.
Customers with the most useful comments can be fetched, as well as books that have low stock.
When logged in, managers viewing books will have access to a page to update the book information. Here managers can update stock.
