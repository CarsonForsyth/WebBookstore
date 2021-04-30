# WebBookstore

This webapp is written for CMPSC 431W @ psu with Dong Xie for Spring 2021.  
This app uses Flask on Python with a SQLite Database to run a Bootstrap Frontend.  

Packages Required for main app: "flask", "flask_bootstrap", "jinja2"  

To use the webapp:  
1. Download the master and required packages  
2. Navigate to /webserver  
3. Run app.py with Python3  
4. Runs on http://127.0.0.1:5000/ by default  

For issues with the data stored in database:  
1. Navigate to /scripts  
2. Run rebuild.py with Python3  
3. Wait for a while as the tables are fully populated with mock data  

**To use the website**  

Accessing the website will redirect users to the homepage.  
Click "Click here to sign into your account" to access login page.  
**On login page:**  
- Input username and password of created account then click "Login" to be logged in.  
- Click "Signup" to access signup page to create a new account.  

**On signup page:**  
- Input unique username, email and password then click "Signup" to create account and be logged in.  

**From the Navigation Bar:**  
- Click "Popular Books" for a list of the most ordered books, based off random mock data.  
- Click "Highest Rated Books" for a list of the books with the highest ratings.  
- Click "Find a Book" to access the search page.  
- Click "My Account" to access user-specific functions:  
  - "My Cart" will display all the books in cart but not ordered.  
  - "My Orders" will display all orders of books.  
  - "My Recommended Books" will take you to see individually recommended books.  
  - "My Addresses" will allow you to add and view stored addresses for your account.  
  - "My Comments" will take you to a list of the comments you have left.  
  - "My Trusted Users" will take you to see users that you have trusted or distrusted.  
  - "My Information" will take you to customer information page, where you may add information to become a customer to then order some books.  
  - "Login" / "Logout" will allow the user to log in or out depending on status.  
- Click "Find a Book" to access search.  
  
**On the search page:**  
Whichever fields have text within them, the site will narrow results to.  
E.g., To search for an author type part of or the entire author's name into "Author" field.  
Select a sort at the bottom to order the results by. Click "Search Books" to return a list of matching books.  
  
*From any of the lists of books, click "View Book" to access the book page.*  

**On the book page:**  
Authors are listed as hyperlinks to their author page.  
The overall rating displays the average rating from every comment on the book.  
The page will tell user if book is in stock, and list the current price.  
If the book is on sale, this is displayed, and the discount, and the discounted price of the book.  
All the necessary book information is listed under the title and authors.  
- Click "Order Now" to add the book to your cart.  
Under Add a Comment:  
- Users can leave a rating and an optional review of the current book if they have not done so already.  
Under View Comments:  
- User can select number of comments to fetch, and comment with negative trust rating and or distrusted by user will be hidden.  
- User can rate each comment as "Very Useful", "Useful", or "Not Useful" using buttons.  
- User can trust the commentor based off of comment using "Trust" or "Distrust" button.  
  
**On the author page:**  
Under Books by this Author:  
- User will be able to see a list of books written by that author.  
Under Books by Related Authors, 1-degree Seperation:  
- User will be able to see a list of books written by 1-degree seperated authors.  
Under Books by Related Authors, 2-degree Seperation:  
- User will be able to see a list of books written by 2-degree seperated authors.  

*To login as manager, use username "admin" and password "pass".*  

While logged in and viewing a book, Manager has access to "Update this Book". Click this to access update book page:  
- From this page, Manager can update all information on books, including stock.  

On the homepage their will be a new button, "Manager Panel". Click this to access manager page.  
**On manager page:**  
- Click "Add a Book" to be taken to add book page:  
  - Manager can create a new book entry here by filling out each field and submitting with "Add Book" button.  
- Click "Get Sales" to view sales page: 
  - Manager may view all sales. 
  - Click "Create a Sale" to access create sale page:  
    - Manager can fill out name, discount, and dates of sale.  
  - Click on a sale hyperlink to update the sale:  
    - Add books to be discounted by putting in ISBN13 and clicking "Add Book" button.  
- Click "Get Users" to view every user in the system and their information.  
  - Click "Update this User" to change email, username, or role of the user. This is how original manager may create more managers.  
Under "View Product Sales by Location":  
  - Fill quarter, year, and number of cities to fetch, then click "Get Stats" to fetch the cities that have been shipped to the most.  
Under "View Most Useful Customers":  
  - Fill number of customers then click "Get Customers" to fetch the selected number of users with the highest rated comments.  
Under "View Most Trusted Customers":  
  - Fill number of customers then click "Get Customers" to fetch the users sorted by the highest number of trusts.  
Under "View Book Statistics"  
  - Fill quarter, year, and number of cities to fetch, then to retrieve statistics click:  
    - "By Book" for the most ordered books.  
    - "By Author" for the most ordered authors.  
    - "By Publisher" for the most ordered publishers.  
Under "View Low Stock Items":  
  - Fill number of books to fetch, then click "Get Books" to display the given number of books with the lowest stock in the store.  

