DW Supermarket

This is a Python/Django web application that serves as an online supermarket. This is designed for pick-up orders only!

All users of the website will be able to browse the different product categories and the items and prices contained within each category.

Only logged in users will be able to add items to their shopping cart.  If the user is not logged in (anonymous user), then they will be redirected to a login/signup page to create or sign into their user account.

On the order summary page, the user will have the ability to:
  1. update their order item quantities
  2. change their pick-up time slot, if desired
  3. continue shopping
  4. continue to checkout

The checkout button functionality utilizes an API call to Stripe.  Payment details are handled by Stripe.  The DW Supermarket application uses a webhook provided by stripe, which waits for a success response from Stripe upon a successful payment for an order.  The webhook endpoint on the DW supermarket server securely receives the success event delivered by Stripe, and then updates the 'ordered' status of the corresponding order in the application database.  The manager of the supermarket can then see which orders have been successfully placed and can prepare the orders for pick-up the following day during the user's chosen time slot.  See next section for other actions the supermarket manager can complete.

NOTE: A Stripe account is required to run this app.  The views.py file needs to be updated to reference your Stripe API keys (Store in environment variable, then reference that environment variable so not to expose any private api keys).  In orders_summary.html file, paste the stripe public api key in the location specified.  

The supermarket manager (Django's superuser account) will be able to use Django's admin app for the following tasks:

1. Creating new store items
2. Updating existing store items (i.e. price change)
3. Monitoring submitted orders
4. Fulfilling submitted orders

